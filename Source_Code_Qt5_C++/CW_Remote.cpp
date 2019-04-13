#include <QApplication>

// X axis ticks/labels optimize
// Alarms
// {@@@@@}


//AWS C++ SDK build from source, unpack, cd to that directory, then:
//$ sudo cmake -DBUILD_ONLY="monitoring" -DBUILD_SHARED_LIBS=OFF -DENABLE_UNITY_BUILD=ON
//$ sudo make


//$ otool -L CW_Remote.app/Contents/MacOs/CW_Remote
//CW_Remote.app/Contents/MacOs/CW_Remote:
//    /System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation (compatibility version 150.0.0, current version 1450.15.0)
//    /usr/lib/libcurl.4.dylib (compatibility version 7.0.0, current version 9.0.0)
//    @rpath/QtCharts.framework/Versions/5/QtCharts (compatibility version 5.12.0, current version 5.12.2)
//    @rpath/QtPrintSupport.framework/Versions/5/QtPrintSupport (compatibility version 5.12.0, current version 5.12.2)
//    @rpath/QtWidgets.framework/Versions/5/QtWidgets (compatibility version 5.12.0, current version 5.12.2)
//    @rpath/QtGui.framework/Versions/5/QtGui (compatibility version 5.12.0, current version 5.12.2)
//    @rpath/QtCore.framework/Versions/5/QtCore (compatibility version 5.12.0, current version 5.12.2)
//    /System/Library/Frameworks/DiskArbitration.framework/Versions/A/DiskArbitration (compatibility version 1.0.0, current version 1.0.0)
//    /System/Library/Frameworks/IOKit.framework/Versions/A/IOKit (compatibility version 1.0.0, current version 275.0.0)
//    /System/Library/Frameworks/OpenGL.framework/Versions/A/OpenGL (compatibility version 1.0.0, current version 1.0.0)
//    /System/Library/Frameworks/AGL.framework/Versions/A/AGL (compatibility version 1.0.0, current version 1.0.0)
//    /usr/lib/libc++.1.dylib (compatibility version 1.0.0, current version 400.9.0)
//    /usr/lib/libSystem.B.dylib (compatibility version 1.0.0, current version 1252.0.0)
//$


//$ /Users/Ken/Qt/5.12.2/clang_64/bin/macdeployqt CW_Remote.app

#include "CW_Remote.h"

using namespace Aws;
using namespace Aws::Auth;
using namespace Aws::CloudWatch;
using namespace Aws::CloudWatch::Model;

QT_CHARTS_USE_NAMESPACE

static
int bound ( int low, int high, int value ) {
    return qMax(low, qMin(high, value));
}

static
int Optimize_DataPoint_Summary_Seconds ( int Period_Hours ) {
    int datapoint_summary_seconds = 60;

    // The maximum number of data points returned from a single call is 1,440.
    // The period for each datapoint can be 1, 5, 10, 30, 60, or any multiple of 60 seconds.

    double datapoint_count = (Period_Hours * 60 * 60) / datapoint_summary_seconds;
    while (datapoint_count > 1440) {
        datapoint_summary_seconds += 60;
        datapoint_count = (Period_Hours * 60 * 60) / datapoint_summary_seconds;
    }

    return datapoint_summary_seconds;
}

static
int Initial_Period_Duration_Hours = 24;
static
int Initial_Period_End_Hours_Ago = 0;

static
CW_Remote *CW_Remote_Main_Window;

static
QJsonObject CW_Remote_ini;

static
QJsonArray Graph_Metric_Descriptor_List;

static
QJsonArray Alarm_Name_List;

static
Aws::CloudWatch::CloudWatchClient *CloudWatch_Client = nullptr;

static
QVector<Graph_Metric_Statistics> Cache_Graph_Metric_Statistics;

static
QVector<Page_Metric_Statistics> Cache_Page_Metric_Statistics;

static
QVector<Metric_Statistics_Descriptor> Upper_Graph_Metric_Statistics;

static
QVector<Metric_Statistics_Descriptor> Lower_Graph_Metric_Statistics;

QString
get_json_string_value ( QJsonObject Json_Obj,
                        QString Value_Name, QString Value_Default ) {
    QString value = Value_Default;
    if (Json_Obj.contains(Value_Name) and Json_Obj[Value_Name].isString())
        value = Json_Obj[Value_Name].toString();
    return value;
}

static
void
Get_Metric_Statistics ( int Graph_Metric_Descriptor_Index,
                        int Metric_Descriptor_Index,
                        QDateTime Period_End_UTC, int Period_Duration_Hours,
                        QVector<Metric_Statistics_Descriptor> *Graph_Metric_Statistics ) {

    GetMetricStatisticsRequest request;
    Dimension request_dimension;

    QJsonArray graph_metric_descriptor_list =
        Graph_Metric_Descriptor_List[Graph_Metric_Descriptor_Index].toArray();
    QJsonObject metric_descr = graph_metric_descriptor_list[Metric_Descriptor_Index].toObject();
    QString metric_name = get_json_string_value(metric_descr, "MetricName", "");
    QString name_space = get_json_string_value(metric_descr, "Namespace", "");

    request.SetMetricName(metric_name.toStdString());
    request.SetNamespace(name_space.toStdString());

    QJsonArray dimensions = metric_descr["Dimensions"].toArray();
    QJsonObject dimension_n = dimensions.at(0).toObject();
    QString dimension_name = get_json_string_value(dimension_n, "Name", "");
    QString dimension_value = get_json_string_value(dimension_n, "Value", "");

    request_dimension.SetName(dimension_name.toStdString());
    request_dimension.SetValue(dimension_value.toStdString());
    request.AddDimensions(request_dimension);

    QDateTime Period_Begin_UTC = Period_End_UTC.addSecs(-(60 * 60 * Period_Duration_Hours));

    request.SetStartTime(Period_Begin_UTC.toMSecsSinceEpoch());
    request.SetEndTime(Period_End_UTC.toMSecsSinceEpoch());

    QDateTime period_end_local = Period_End_UTC.toLocalTime();
    long period_local_offset_seconds = Period_End_UTC.secsTo(period_end_local);

    request.SetPeriod(Optimize_DataPoint_Summary_Seconds(Period_Duration_Hours));

    // {@@@@@} This is not adaptive to enum:
    //            Average, Minimum, Maximum, SampleCount, Sum
    bool request_average = false;
    bool request_maximum = false;
    bool request_minimum = false;
    bool request_samplecount = false;
    bool request_sum = false;
    QJsonArray statistics = metric_descr["Statistics"].toArray();
    for (int idx = 0; idx < statistics.size(); idx++) {
        QString stat_string = statistics[idx].toString();
        // Adaptive to enum: Average, Minimum, Maximum, SampleCount, Sum ...
        if (stat_string == "Average") request_average = true;
        else if (stat_string == "Maximum") request_maximum = true;
        else if (stat_string == "Minimum") request_minimum = true;
        else if (stat_string == "SampleCount") request_samplecount = true;
        else if (stat_string == "Sum") request_sum = true;
        // ... Adaptive to enum: Average, Minimum, Maximum, SampleCount, Sum
        // {@@@@@} Should check for error here.
        Statistic statistic = CloudWatch_Statistics[stat_string];
        // {@@@@@} Should check for error here.
        request.AddStatistics(statistic);
    }

    QString unit_string = get_json_string_value(metric_descr, "Unit", " ");
    // {@@@@@} Should check for error here.
    StandardUnit unit = CloudWatch_Units[unit_string];
    // {@@@@@} Should check for error here.
    request.SetUnit(unit);

    GetMetricStatisticsOutcome raw_metric_statistics_outcome =
        CloudWatch_Client->GetMetricStatistics(request);

    GetMetricStatisticsResult raw_metric_statistics_result;

    if (raw_metric_statistics_outcome.IsSuccess())
        raw_metric_statistics_result = raw_metric_statistics_outcome.GetResult();

        Aws::Vector<Datapoint> raw_metric_datapoints =
            raw_metric_statistics_result.GetDatapoints();

        // Adaptive to enum: Average, Minimum, Maximum, SampleCount, Sum ...
        QList<Metric_Statistics_Datapoint> datapoints_average_list;
        Metric_Statistics_Datapoint datapoint_average;

        QList<Metric_Statistics_Datapoint> datapoints_maximum_list;
        Metric_Statistics_Datapoint datapoint_maximum;

        QList<Metric_Statistics_Datapoint> datapoints_minimum_list;
        Metric_Statistics_Datapoint datapoint_minimum;

        QList<Metric_Statistics_Datapoint> datapoints_samplecount_list;
        Metric_Statistics_Datapoint datapoint_samplecount;

        QList<Metric_Statistics_Datapoint> datapoints_sum_list;
        Metric_Statistics_Datapoint datapoint_sum;
        // ... Adaptive to enum: Average, Minimum, Maximum, SampleCount, Sum

        double y_factor = 1;
        if (metric_descr.contains("YFactor") and metric_descr["YFactor"].isDouble())
            y_factor = metric_descr["YFactor"].toDouble();

        get_json_string_value(metric_descr, "YFactor", "");

        for (unsigned long idx = 0; idx < raw_metric_datapoints.size(); idx++) {
            QDateTime datapoint_datetime =
                QDateTime().fromMSecsSinceEpoch(raw_metric_datapoints[idx].GetTimestamp().Millis()).addSecs(period_local_offset_seconds);
            // Adaptive to enum: Average, Minimum, Maximum, SampleCount, Sum ...
            if (request_average) {
                datapoint_average.datapoint_datetime = datapoint_datetime;
                datapoint_average.datapoint_value = y_factor * raw_metric_datapoints[idx].GetAverage();
                datapoints_average_list.append(datapoint_average);
            }

            if (request_maximum) {
                datapoint_maximum.datapoint_datetime = datapoint_datetime;
                datapoint_maximum.datapoint_value = y_factor * raw_metric_datapoints[idx].GetMaximum();
                datapoints_maximum_list.append(datapoint_maximum);
            }

            if (request_minimum) {
                datapoint_minimum.datapoint_datetime = datapoint_datetime;
                datapoint_minimum.datapoint_value = y_factor * raw_metric_datapoints[idx].GetMinimum();
                datapoints_minimum_list.append(datapoint_minimum);
            }

            if (request_samplecount) {
                datapoint_samplecount.datapoint_datetime = datapoint_datetime;
                datapoint_samplecount.datapoint_value = y_factor * raw_metric_datapoints[idx].GetSampleCount();
                datapoints_samplecount_list.append(datapoint_samplecount);
            }

            if (request_sum) {
                datapoint_sum.datapoint_datetime = datapoint_datetime;
                datapoint_sum.datapoint_value = y_factor * raw_metric_datapoints[idx].GetSum();
                datapoints_sum_list.append(datapoint_sum);
            }
            // ... Adaptive to enum: Average, Minimum, Maximum, SampleCount, Sum
        }

        Metric_Statistics_Descriptor metric_statistics;
        metric_statistics.Metric_Descriptor = metric_descr;

        // Adaptive to enum: Average, Minimum, Maximum, SampleCount, Sum ...
        if (request_average) {
            std::sort(datapoints_average_list.begin(), datapoints_average_list.end(), Metric_Statistics_Datapoint_Compare());
            metric_statistics.Datapoints_Average_List = datapoints_average_list;
        }
        if (request_maximum) {
            std::sort(datapoints_maximum_list.begin(), datapoints_maximum_list.end(), Metric_Statistics_Datapoint_Compare());
            metric_statistics.Datapoints_Maximum_List = datapoints_maximum_list;
        }
        if (request_minimum) {
            std::sort(datapoints_minimum_list.begin(), datapoints_minimum_list.end(), Metric_Statistics_Datapoint_Compare());
            metric_statistics.Datapoints_Minimum_List = datapoints_minimum_list;
        }
        if (request_samplecount) {
            std::sort(datapoints_samplecount_list.begin(), datapoints_samplecount_list.end(), Metric_Statistics_Datapoint_Compare());
            metric_statistics.Datapoints_SampleCount_List = datapoints_samplecount_list;
        }
        if (request_sum) {
            std::sort(datapoints_sum_list.begin(), datapoints_sum_list.end(), Metric_Statistics_Datapoint_Compare());
            metric_statistics.Datapoints_Sum_List = datapoints_sum_list;
        }
        // ... Adaptive to enum: Average, Minimum, Maximum, SampleCount, Sum

        Graph_Metric_Statistics->replace(Metric_Descriptor_Index, metric_statistics);
}

using namespace QtConcurrent;

QVector<Metric_Statistics_Descriptor>
Get_Graph_Metric_Statistics ( int Graph_Metric_Descriptor_Index,
                              QDateTime Period_End_UTC, int Period_Duration_Hours ) {
    QJsonArray graph_metric_descriptor = Graph_Metric_Descriptor_List[Graph_Metric_Descriptor_Index].toArray();
    QVector<Metric_Statistics_Descriptor> graph_metrics_statistics_list(graph_metric_descriptor.size());
    QVector<QFuture<void>> future_list;
    for (int metric_idx = 0; metric_idx < graph_metric_descriptor.size(); metric_idx++) {
        // Get_Metric_Statistics(Graph_Metric_Descriptor_Index, metric_idx,
        //                       Period_End_UTC, Period_Duration_Hours,
        //                       &metrics_statistics_list);
        QFuture<void> future = QtConcurrent::run(Get_Metric_Statistics, Graph_Metric_Descriptor_Index, metric_idx,
                                                 Period_End_UTC, Period_Duration_Hours,
                                                 &graph_metrics_statistics_list);
        future_list.append(future);
        for (int idx = 0; idx < future_list.size(); idx++) {
            QFuture<void> future = future_list[idx];
            future.waitForFinished();
        }
    }
    return graph_metrics_statistics_list;
}

QVector<QVector<Metric_Statistics_Descriptor>>
Get_Page_Metric_Statistics ( QVector<int> Graph_Metric_Index_List,
                             QDateTime Period_End_UTC,
                             int Period_Duration_Hours ) {

    if (Graph_Metric_Index_List.count() == 0) return QVector<QVector<Metric_Statistics_Descriptor>>(0);

    int first_graph_metric_descriptor_size = 0;
    int second_graph_metric_descriptor_size = 0;
    if (Graph_Metric_Index_List.count() > 0) {
        QJsonArray first_graph_metric_descriptor =
            Graph_Metric_Descriptor_List[Graph_Metric_Index_List[0]].toArray();
        first_graph_metric_descriptor_size = first_graph_metric_descriptor.size();
    }
    if (Graph_Metric_Index_List.count() > 1) {
        QJsonArray second_graph_metric_descriptor =
            Graph_Metric_Descriptor_List[Graph_Metric_Index_List[1]].toArray();
        second_graph_metric_descriptor_size = second_graph_metric_descriptor.size();
    }

    QVector<Metric_Statistics_Descriptor>
        first_graph_metric_statistics_list(first_graph_metric_descriptor_size);
    QVector<Metric_Statistics_Descriptor>
        second_graph_metric_statistics_list(second_graph_metric_descriptor_size);
    // int first_graph_metric_statistics_count = first_graph_metric_statistics_list.count();
    // int second_graph_metric_statistics_count = second_graph_metric_statistics_list.count();

    QVector<QFuture<void>> future_list;

    if (Graph_Metric_Index_List.count() > 0) {
        int graph_metric_index = Graph_Metric_Index_List[0];
        QJsonArray first_graph_metric_descriptor =
            Graph_Metric_Descriptor_List[graph_metric_index].toArray();
        for (int metric_idx = 0; metric_idx < first_graph_metric_descriptor.size(); metric_idx++) {
            // Get_Metric_Statistics(Graph_Metric_Descriptor_Index, metric_idx,
            //                       Period_End_UTC, Period_Duration_Hours,
            //                       &metrics_statistics_list);
            QFuture<void> future = QtConcurrent::run(Get_Metric_Statistics, graph_metric_index, metric_idx,
                                                     Period_End_UTC, Period_Duration_Hours,
                                                     &first_graph_metric_statistics_list);
            future_list.append(future);
        }
    }
    if (Graph_Metric_Index_List.count() > 1) {
        int graph_metric_index = Graph_Metric_Index_List[1];
        QJsonArray second_graph_metric_descriptor =
            Graph_Metric_Descriptor_List[graph_metric_index].toArray();
        for (int metric_idx = 0; metric_idx < second_graph_metric_descriptor.size(); metric_idx++) {
            // Get_Metric_Statistics(Graph_Metric_Descriptor_Index, metric_idx,
            //                       Period_End_UTC, Period_Duration_Hours,
            //                       &metrics_statistics_list);
            QFuture<void> future = QtConcurrent::run(Get_Metric_Statistics, graph_metric_index, metric_idx,
                                                     Period_End_UTC, Period_Duration_Hours,
                                                     &second_graph_metric_statistics_list);
            future_list.append(future);
        }
    }

    // Wait for everything to finish
    for (int idx = 0; idx < future_list.size(); idx++) {
        QFuture<void> future = future_list[idx];
        future.waitForFinished();
    }

    QVector<QVector<Metric_Statistics_Descriptor>> page_graph_metric_statistics_list;
    if (Graph_Metric_Index_List.count() > 0)
        page_graph_metric_statistics_list.append(first_graph_metric_statistics_list);
    if (Graph_Metric_Index_List.count() > 1)
        page_graph_metric_statistics_list.append(second_graph_metric_statistics_list);

    return page_graph_metric_statistics_list;
}


static
void
Describe_Alarm_History ( QString Alarm_Name,
                         QDateTime Period_Begin_UTC, QDateTime Period_End_UTC,
                         QMap<QString, QStringList> Alarm_History_Results ) {

    DescribeAlarmHistoryRequest request;
    request.SetAlarmName(Alarm_Name.toStdString());
    request.SetHistoryItemType(HistoryItemType::StateUpdate);
    request.SetStartDate(Period_Begin_UTC.toMSecsSinceEpoch());
    request.SetEndDate(Period_End_UTC.toMSecsSinceEpoch());
    request.SetMaxRecords(100);

    DescribeAlarmHistoryOutcome raw_alarm_history_outcome =
        CloudWatch_Client->DescribeAlarmHistory(request);

    DescribeAlarmHistoryResult raw_alarm_history_result;

    if (raw_alarm_history_outcome.IsSuccess())
        raw_alarm_history_result = raw_alarm_history_outcome.GetResult();

    // Aws::String next_token = raw_alarm_history_result.GetNextToken();
    // bool done = next_token.empty();

    Aws::Vector<AlarmHistoryItem> alarm_history_items = raw_alarm_history_result.GetAlarmHistoryItems();

    QStringList alarm_history;
    for (unsigned long idx = 0; idx < alarm_history_items.size(); idx++) {
        AlarmHistoryItem history_item = alarm_history_items[idx];

        Aws::String history_item_alarm_name = history_item.GetAlarmName();
        alarm_history.append(QString::fromUtf8(history_item_alarm_name.data()/*, history_item_alarm_name.size()*/));

        QDateTime history_item_datetime_utc = QDateTime().fromMSecsSinceEpoch(history_item.GetTimestamp().Millis());
        alarm_history.append(history_item_datetime_utc.toLocalTime().toString());

        Aws::String history_item_summary = history_item.GetHistorySummary();
        alarm_history.append(QString::fromUtf8(history_item_summary.data()/*, history_item_summary.size()*/));

        Aws::String history_item_data = history_item.GetHistoryData();
        alarm_history.append(QString::fromUtf8(history_item_data.data()/*, history_item_data.size()*/));
    }

    Alarm_History_Results[Alarm_Name] = alarm_history;
}

static
QMap<QString, QStringList>
Alarm_History ( QJsonArray Alarm_Name_List ) {
    QMap<QString, QStringList> alarm_history_results;
    if (Alarm_Name_List.count() == 0) return alarm_history_results;

    QDateTime datetime_now_utc = QDateTime::currentDateTimeUtc();
    QDateTime datetime_yesterday_utc = datetime_now_utc.addSecs(-(24 * 60 * 60));

    QVector<QFuture<void>> future_list;
    for (int idx = 0; idx < Alarm_Name_List.count(); idx++) {
        QString alarm_name = Alarm_Name_List[idx].toString();
        QFuture<void> future = QtConcurrent::run(Describe_Alarm_History, alarm_name,
                                                 datetime_yesterday_utc, datetime_now_utc,
                                                 alarm_history_results);
        future_list.append(future);
    }

    // Wait for everything to finish
    for (int idx = 0; idx < future_list.size(); idx++) {
        QFuture<void> future = future_list[idx];
        future.waitForFinished();
    }

    return alarm_history_results;
}


using namespace Aws::Utils::Logging;

int main ( int argc, char* argv[] ) {
    QApplication Application(argc, argv);
    // qDebug() << qVersion();

    // Read json ini file
    QString cw_remote_ini_json;
    // QFile cw_remote_ini_file;
    // cw_remote_ini_file.setFileName("~/Documents/CW_Remote/CW_Remote.ini");
    QString cw_remote__ini_filename = QCoreApplication::applicationDirPath();
    cw_remote__ini_filename.truncate(cw_remote__ini_filename.indexOf("CW_Remote.app"));
    cw_remote__ini_filename += "CW_Remote.ini";
    // qDebug() << cw_remote__ini_filename;
    if (not QFileInfo(cw_remote__ini_filename).exists()) {
        cw_remote__ini_filename = QDir::homePath() + "/Documents/CW_Remote/CW_Remote.ini";
        if (not QFileInfo(cw_remote__ini_filename).exists()) return 255;
    }
    QFile cw_remote_ini_file(cw_remote__ini_filename);
    cw_remote_ini_file.open(QIODevice::ReadOnly | QIODevice::Text);
    cw_remote_ini_json = cw_remote_ini_file.readAll();
    cw_remote_ini_file.close();

    CW_Remote_ini = QJsonDocument::fromJson(cw_remote_ini_json.toUtf8()).object();

    QString aws_access_id = get_json_string_value(CW_Remote_ini, "aws_access_id", "");
    QString aws_secret_key = get_json_string_value(CW_Remote_ini, "aws_secret_key", "");
    QString region_name = get_json_string_value(CW_Remote_ini, "region_name", "");

    Graph_Metric_Descriptor_List = CW_Remote_ini["metric_descriptor_list"].toArray();
    Alarm_Name_List = CW_Remote_ini["alarm_name_list"].toArray();

    SDKOptions options;
//    options.loggingOptions.logLevel = Aws::Utils::Logging::LogLevel::Off;

//    options.loggingOptions.logLevel = LogLevel::Off;
//    options.loggingOptions.logger_create_fn = [] { return std::make_shared<ConsoleLogSystem>(LogLevel::Off); };

//    Aws::Utils::Logging::InitializeAWSLogging(
//        Aws::MakeShared<Aws::Utils::Logging::DefaultLogSystem>(
//            "RunUnitTests", Aws::Utils::Logging::LogLevel::Off, "aws_sdk_"));
//    Aws::Utils::Logging::ShutdownAWSLogging();
    InitAPI(options);


    AWSCredentials credentials;
    credentials.SetAWSAccessKeyId(aws_access_id.toStdString());
    credentials.SetAWSSecretKey(aws_secret_key.toStdString());

    Aws::Client::ClientConfiguration client_configuration;
    client_configuration.region = region_name.toStdString();
    client_configuration.scheme = Aws::Http::Scheme::HTTPS;
    client_configuration.connectTimeoutMs = 30000;
    client_configuration.requestTimeoutMs = 120000;

    Aws::CloudWatch::CloudWatchClient cloudwatch_client(credentials, client_configuration);
    CloudWatch_Client = &cloudwatch_client;

    CW_Remote MainWindow;
    MainWindow.setContentsMargins(0, 0, 0, 0);
    MainWindow.show();

    // MainWindow.CW_Remote_Screen_Widget->Update_ChartView_Data();

    int return_code = Application.exec();

    Aws::Utils::Logging::ShutdownAWSLogging();

    ShutdownAPI(options);

    return return_code;
}


CW_Remote::CW_Remote ( QWidget *parent ) : QMainWindow ( parent ) {
    CW_Remote_Main_Window = this;
    CW_Remote_Main_Window->setWindowTitle("CW_Remote");

    setMinimumWidth(1280);
    setMinimumHeight(800);
    setContentsMargins(0, 0, 0, 0);

    CW_Remote_Screen_Widget = new CW_Remote_Screen(this);
    CW_Remote_Screen_Widget->setContentsMargins(0, 0, 0, 0);
    setCentralWidget(CW_Remote_Screen_Widget);

    setAttribute(Qt::WA_AlwaysShowToolTips);
    setMouseTracking(true);
}

CW_Remote::~CW_Remote ( ) {
}


CW_Remote_Screen::CW_Remote_Screen ( QWidget *parent ) : QWidget ( parent ) {
    Visible_Graph_Count = 2;
    Graph_Offset = 0;

    setContentsMargins(0, 0, 0, 0);

    Period_Duration_Hours = Initial_Period_Duration_Hours;
    Period_End_Hours_Ago = Initial_Period_End_Hours_Ago;

    empty_label = new QLabel("");
    empty_label->setMaximumHeight(1);

    Upper_Chartview = new ChartView();

    Control_Bar = new ControlBar();
    connect(Control_Bar, SIGNAL(metricsUpdate()), this, SLOT(update_page_metrics()));
    connect(Control_Bar, SIGNAL(metricsPrevious()), this, SLOT(previous_page_metrics()));
    connect(Control_Bar, SIGNAL(metricsNext()), this, SLOT(next_page_metrics()));
    connect(Control_Bar, SIGNAL(metricsDuplex()), this, SLOT(duplex_metrics()));
    connect(Control_Bar, SIGNAL(metricsSimplex()), this, SLOT(simplex_metrics()));

    Lower_Chartview = new ChartView();

    QDateTime datetime_now_utc = QDateTime::currentDateTimeUtc();
    QDateTime period_end_utc = datetime_now_utc.addSecs(-(Period_End_Hours_Ago * (60 * 60)));

    // QVector<Metric_Statistics_Descriptor> upper_graph_metric_statistics =
    //     Get_Graph_Metric_Statistics((Graph_Offset + 0), period_end_utc, Period_Duration_Hours);

    // QVector<Metric_Statistics_Descriptor> lower_graph_metric_statistics =
    //     Get_Graph_Metric_Statistics((Graph_Offset + 1), period_end_utc, Period_Duration_Hours);

    QVector<QVector<Metric_Statistics_Descriptor>> page_graph_metric_statistics =
        Get_Page_Metric_Statistics ( QVector<int>( { (Graph_Offset + 0), (Graph_Offset + 1) } ),
                                     period_end_utc, Period_Duration_Hours );
    QVector<Metric_Statistics_Descriptor> upper_graph_metric_statistics = page_graph_metric_statistics[0];
    QVector<Metric_Statistics_Descriptor> lower_graph_metric_statistics = page_graph_metric_statistics[1];

    Upper_Chartview->setChartData(upper_graph_metric_statistics);
    Lower_Chartview->setChartData(lower_graph_metric_statistics);

    QVBoxLayout *main_window_layout = new QVBoxLayout();
    main_window_layout->setMargin(0);
    main_window_layout->setContentsMargins(0, 0, 0, 0);
    main_window_layout->setSpacing(0);

    main_window_layout->addWidget(Upper_Chartview, 50);
    main_window_layout->addWidget(Control_Bar, 0);
    main_window_layout->addWidget(Lower_Chartview, 50);

    setLayout(main_window_layout);

    set_main_window_title();

    setAttribute(Qt::WA_AlwaysShowToolTips);
    setMouseTracking(true);

    timer = new QTimer(this);
    connect(timer, SIGNAL(timeout()), this, SLOT(timer_update_page_metrics()));
    timer->start(60000); // 60 seconds in milliseconds
}

CW_Remote_Screen::~CW_Remote_Screen ( ) {
}

void
CW_Remote_Screen::timer_update_page_metrics (  ) {
    if (((Visible_Graph_Count == 2) and
         (Upper_Chartview->zoom_level == 0) and (Lower_Chartview->zoom_level == 0)) or
        ((Visible_Graph_Count == 1) and (Lower_Chartview->zoom_level == 0))) update_page_metrics();

    QMap<QString, QStringList> alarm_history = Alarm_History(Alarm_Name_List);
}

void
CW_Remote_Screen::update_page_metrics (  ) {
    Period_Duration_Hours = Control_Bar->get_period_duration_hours_value();
    Period_End_Hours_Ago = Control_Bar->get_period_end_hours_ago_value();

    set_main_window_title();

    QDateTime datetime_now_utc = QDateTime::currentDateTimeUtc();
    QDateTime period_end_utc = datetime_now_utc.addSecs(-(Period_End_Hours_Ago * (60 * 60)));

    if (Visible_Graph_Count == 2) {
        QVector<QVector<Metric_Statistics_Descriptor>> page_graph_metric_statistics =
            Get_Page_Metric_Statistics ( QVector<int>( { (Graph_Offset + 0), (Graph_Offset + 1) } ),
                                         period_end_utc, Period_Duration_Hours );

        QVector<Metric_Statistics_Descriptor> upper_graph_metric_statistics = page_graph_metric_statistics[0];
        QVector<Metric_Statistics_Descriptor> lower_graph_metric_statistics = page_graph_metric_statistics[1];
        Upper_Chartview->setChartData(upper_graph_metric_statistics);
        Lower_Chartview->setChartData(lower_graph_metric_statistics);
    }
    else if (Visible_Graph_Count == 1) {
        QVector<Metric_Statistics_Descriptor> lower_graph_metric_statistics =
            Get_Graph_Metric_Statistics((Graph_Offset + 0), period_end_utc, Period_Duration_Hours);
        Lower_Chartview->setChartData(lower_graph_metric_statistics);
    }
}

void
CW_Remote_Screen::previous_page_metrics (  ) {
    if (Visible_Graph_Count == 2) {
        if ((Graph_Offset % 2) == 1)
            // If odd, then 1, 3, 5 ..., move back to even alignment
            Graph_Offset -= 1;
        else if (Graph_Offset > 1)
            Graph_Offset -= 2;
        else Graph_Offset = 0;
    }
    else {
        if (Graph_Offset > 0)
            Graph_Offset -= 1;
        else Graph_Offset = 0;
    }
    update_page_metrics();
}

void
CW_Remote_Screen::next_page_metrics (  ) {
    int descriptor_list_length = Graph_Metric_Descriptor_List.count();
    if (Visible_Graph_Count == 2) {
        // We are displaying two graphs, must account for second graph after skipping ahead
        if ((Graph_Offset + 2 + 1) < descriptor_list_length)
            Graph_Offset += 2;
        else if ((Graph_Offset + 1 + 1) < descriptor_list_length)
            // If at at the end save one graph, move ahead by one for odd alignment
            Graph_Offset += 1;
    }
    else {
        if ((Graph_Offset + 1) < descriptor_list_length)
            Graph_Offset += 1;
    }
    update_page_metrics();
}

void
CW_Remote_Screen::duplex_metrics (  ) {
    if (Visible_Graph_Count == 1) {
        QLayout *main_window_layout = layout();
        main_window_layout->replaceWidget(empty_label, Upper_Chartview, Qt::FindDirectChildrenOnly);
        Lower_Chartview->setMaximumHeight(lower_chartview_height);
        Upper_Chartview->setMaximumHeight(upper_chartview_height);
        Graph_Offset = qMax((Graph_Offset - 1), 0);
        Visible_Graph_Count = 2;
        // Transitioning from simplex, the old Upper_Chartview is probably stale
        update_page_metrics();
        // update();
    }
}

void
CW_Remote_Screen::simplex_metrics (  ) {
    if (Visible_Graph_Count == 2) {
        int descriptor_list_length = Graph_Metric_Descriptor_List.count();
        upper_chartview_height = Upper_Chartview->height();
        lower_chartview_height = Lower_Chartview->height();
        QLayout *main_window_layout = layout();
        main_window_layout->replaceWidget(Upper_Chartview, empty_label, Qt::FindDirectChildrenOnly);
        Graph_Offset = qMin((Graph_Offset + 1), (descriptor_list_length - 1));
        Visible_Graph_Count = 1;
        // Transitioning from duplex, the current Lower_Chartview is not stale
        // update_page_metrics();
        update();
    }
}

void
CW_Remote_Screen::set_main_window_title (  ) {
    if (CW_Remote_Main_Window) {
        QDateTime datetime_now_utc = QDateTime::currentDateTimeUtc();
        QDateTime period_end_utc = datetime_now_utc.addSecs(-(Period_End_Hours_Ago * (60 * 60)));

        QDateTime period_end_local = period_end_utc.toLocalTime();
        QDateTime period_begin_local = period_end_local.addSecs(-(Period_Duration_Hours * (60 * 60)));

        QString main_window_title = QString("CW_Remote");
        main_window_title +=
            " ( " + period_begin_local.toString() + " - " + period_end_local.toString() + " )";
        CW_Remote_Main_Window->setWindowTitle(main_window_title);
    }
}


struct LineSeries_LineSeriesName {
    QtCharts::QLineSeries* line_series;
    QString line_series_name;
};


ChartView::ChartView ( QWidget *parent ) : QtCharts::QChartView ( parent ) {
    setContentsMargins(0, 0, 0, 0);

    has_data = false;

    zoom_level = 0;
    zoom_factor = 4;

    chart = new QtCharts::QChart();
    chart->setBackgroundRoundness(0);
    chart->layout()->setContentsMargins(0, 0, 0, 0);
    QMargins chart_margins = chart->margins();
    chart_margins.setTop(0);
    chart_margins.setBottom(0);
    chart->setMargins(chart_margins);

    axisX = nullptr;
    axisX_top = nullptr;
    axisY_left = nullptr;
    axisY_right = nullptr;

    setChart(chart);
    setRenderHint(QPainter::Antialiasing);

    setAttribute(Qt::WA_AlwaysShowToolTips);
    setMouseTracking(true);

    chartview_scene = scene();
    plot_area_box_item = nullptr;
}

void
ChartView::setChartData ( const QVector<Metric_Statistics_Descriptor> Chart_Metric_Statistics_List ) {
    chart->removeAllSeries();
    // Axes "remember" their previous state, ...
    // ... if not removed, previous min/max values will displayed
    if (axisX) chart->removeAxis(axisX);
    if (axisX_top) chart->removeAxis(axisX_top);
    if (axisY_left) chart->removeAxis(axisY_left);
    if (axisY_right) chart->removeAxis(axisY_right);

    // Replace with new "stateless" axes
    axisX = new QtCharts::QDateTimeAxis();
    axisX_top = new QtCharts::QDateTimeAxis();
    chart->addAxis(axisX, Qt::AlignBottom);
    chart->addAxis(axisX_top, Qt::AlignTop);

    int left_y_axis_series_count = 0;
    int right_y_axis_series_count = 0;

    for (int idx = 0; idx < Chart_Metric_Statistics_List.size(); idx++) {
        QJsonObject metric_descriptor = Chart_Metric_Statistics_List[idx].Metric_Descriptor;
        QString which_y_axis = get_json_string_value(metric_descriptor,"YAxis", "left");
        if (which_y_axis == "left") left_y_axis_series_count += 1;
        else if (which_y_axis == "right") right_y_axis_series_count += 1;
    }

    if (left_y_axis_series_count > 0) {
        axisY_left = new QtCharts::QValueAxis();
        chart->addAxis(axisY_left, Qt::AlignLeft);
    }

    if (right_y_axis_series_count > 0) {
        axisY_right = new QtCharts::QValueAxis();
        chart->addAxis(axisY_right, Qt::AlignRight);
    }

    QList<Metric_Statistics_Datapoint> datapoints =
        Chart_Metric_Statistics_List[0].Datapoints_Maximum_List;

    QDateTime data_min_datetime = datapoints[0].datapoint_datetime;
    QDateTime data_max_datetime = datapoints[0].datapoint_datetime;

    for (int idx = 1; idx < datapoints.size(); idx++) {
        if (datapoints[idx].datapoint_datetime < data_min_datetime)
            data_min_datetime = datapoints[idx].datapoint_datetime;
        if (datapoints[idx].datapoint_datetime > data_max_datetime)
            data_max_datetime = datapoints[idx].datapoint_datetime;
    }

    uint min_unixtime  = data_min_datetime.toTime_t();
    QDateTime data_min_datetime_quantized;
    data_min_datetime_quantized.setTime_t(min_unixtime - (min_unixtime % (60 * 60)));

    uint max_unixtime  = data_max_datetime.toTime_t();
    QDateTime data_max_datetime_quantized;
    data_max_datetime_quantized.setTime_t(max_unixtime + ((60 * 60) - max_unixtime % (60 * 60)));

    QtCharts::QLineSeries *workaround_line_series = new QtCharts::QLineSeries();
    workaround_line_series->append(QDateTime(data_min_datetime_quantized).toMSecsSinceEpoch(), 0);
    workaround_line_series->append(QDateTime(data_max_datetime_quantized).toMSecsSinceEpoch(), 0);
    QPen pen = workaround_line_series->pen();
    pen.setWidth(1);
    pen.setColor("lightgray");
    workaround_line_series->setPen(pen);

    chart->addSeries(workaround_line_series);
    workaround_line_series->attachAxis(axisX);
    if (left_y_axis_series_count > 0) workaround_line_series->attachAxis(axisY_left);
    else if (right_y_axis_series_count > 0) workaround_line_series->attachAxis(axisY_right);

    double data_min_value_left = 0;
    double data_max_value_left = 0;
    double data_min_value_right = 0;
    double data_max_value_right = 0;

    QVector<LineSeries_LineSeriesName> line_series_left_list;
    QVector<LineSeries_LineSeriesName> line_series_right_list;

    for (int idx = (Chart_Metric_Statistics_List.size() - 1); idx >= 0; idx--) {
        QJsonObject metric_descriptor = Chart_Metric_Statistics_List[idx].Metric_Descriptor;
        QString which_y_axis = get_json_string_value(metric_descriptor,"YAxis", "left");

        QList<Metric_Statistics_Datapoint> datapoints =
            Chart_Metric_Statistics_List[idx].Datapoints_Maximum_List;

        QtCharts::QLineSeries *line_series = new QtCharts::QLineSeries();

        for (int idx = 1; idx < datapoints.size(); idx++) {
            if (datapoints[idx].datapoint_datetime < data_min_datetime)
                data_min_datetime = datapoints[idx].datapoint_datetime;
            if (datapoints[idx].datapoint_datetime > data_max_datetime)
                data_max_datetime = datapoints[idx].datapoint_datetime;

            if (which_y_axis == "left") {
                if (datapoints[idx].datapoint_value < data_min_value_left)
                    data_min_value_left = datapoints[idx].datapoint_value;
                if (datapoints[idx].datapoint_value > data_max_value_left)
                    data_max_value_left = datapoints[idx].datapoint_value;
            }
            else if (which_y_axis == "right") {
                if (datapoints[idx].datapoint_value < data_min_value_right)
                    data_min_value_right = datapoints[idx].datapoint_value;
                if (datapoints[idx].datapoint_value > data_max_value_right)
                    data_max_value_right = datapoints[idx].datapoint_value;
            }

            line_series->append(QDateTime(datapoints[idx].datapoint_datetime).toMSecsSinceEpoch(),
                                datapoints[idx].datapoint_value);
        }

        QColor line_color = QColor().fromRgb(0, 0, 0);
        if (metric_descriptor.contains("Color") and
            metric_descriptor["Color"].isArray()) {
            QJsonArray color_values = metric_descriptor["Color"].toArray();
            line_color = QColor().fromRgbF(color_values[0].toDouble(),
                                           color_values[1].toDouble(),
                                           color_values[2].toDouble());
        }

        QPen pen = line_series->pen();
        pen.setWidth(0);
        pen.setColor(line_color);
        line_series->setPen(pen);

        chart->addSeries(line_series);
        line_series->attachAxis(axisX);
        if (which_y_axis == "left") line_series->attachAxis(axisY_left);
        else if (which_y_axis == "right") line_series->attachAxis(axisY_right);

        QString line_series_label = get_json_string_value(metric_descriptor,"MetricLabel", " ");
        if (which_y_axis == "left") {
            line_series_label += "(◀)";
            LineSeries_LineSeriesName lineseries_lineseries_name;
            lineseries_lineseries_name.line_series = line_series;
            lineseries_lineseries_name.line_series_name = line_series_label;
            line_series_left_list.append(lineseries_lineseries_name);
        }
        else if (which_y_axis == "right") {
            line_series_label += "(▶)";
            LineSeries_LineSeriesName lineseries_lineseries_name;
            lineseries_lineseries_name.line_series = line_series;
            lineseries_lineseries_name.line_series_name = line_series_label;
            line_series_right_list.append(lineseries_lineseries_name);
        }
    }

    for (int idx = 0; idx < line_series_left_list.size(); idx++) {
        LineSeries_LineSeriesName lineseries_lineseries_name = line_series_left_list[idx];
        lineseries_lineseries_name.line_series->setName(lineseries_lineseries_name.line_series_name);
    }

    for (int idx = 0; idx < line_series_right_list.size(); idx++) {
        LineSeries_LineSeriesName lineseries_lineseries_name = line_series_right_list[idx];
        lineseries_lineseries_name.line_series->setName(lineseries_lineseries_name.line_series_name);
    }

    // Not necessary:
    // axisX->setMin(data_max_datetime_quantized);
    // axisX->setMax(data_max_datetime_quantized);

    double delta_seconds = data_min_datetime_quantized.secsTo(data_max_datetime_quantized);
    int delta_hours = qRound(delta_seconds / (60 * 60));
    int delta_ticks = 12;
    QVector<int> factor_list({13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2});
    for (int idx = 0; idx < factor_list.size(); idx++) {
        int factor = factor_list[idx];
        if ((delta_hours % factor) == 0) {
            delta_ticks = factor;
            break;
        }
    }

    axisX->setTickCount(delta_ticks + 1);
    axisX->setFormat("hh:mm'\n'MM/dd");

    if (left_y_axis_series_count > 0) {
        axisY_left->setTickType(QtCharts::QValueAxis::TicksDynamic);
        axisY_left->setTickAnchor(0);
        double unit_interval = qPow(10, qFloor(log10(1.025 * data_max_value_left)));
        QVector<int> unit_interval_scale_list({1, 2, 4, 5, 8});
        for (int idx = 0; idx < unit_interval_scale_list.size(); idx++) {
            int unit_interval_scale = unit_interval_scale_list[idx];
            if ((data_max_value_left / (unit_interval / unit_interval_scale)) >= 4) {
                unit_interval = unit_interval / unit_interval_scale;
                break;
            }
        }
        axisY_left->setTickInterval(unit_interval);
        axisY_left->setRange(0, (1.025 * data_max_value_left));

        QColor pen_color = axisY_left->linePen().color();
        pen_color.setNamedColor("#ccccff");
        axisY_left->setLinePenColor(pen_color);
        axisY_left->setGridLineColor(pen_color);
        axisY_left->setGridLineVisible(false);
    }

    if (right_y_axis_series_count >= 0) {
        axisY_right->setTickType(QtCharts::QValueAxis::TicksDynamic);
        axisY_right->setTickAnchor(0);
        double unit_interval = qPow(10, qFloor(log10(1.025 * data_max_value_right)));
        QVector<int> unit_interval_scale_list({1, 2, 4, 5, 8});
        for (int idx = 0; idx < unit_interval_scale_list.size(); idx++) {
            int unit_interval_scale = unit_interval_scale_list[idx];
            if ((data_max_value_right / (unit_interval / unit_interval_scale)) >= 4) {
                unit_interval = unit_interval / unit_interval_scale;
                break;
            }
        }
        axisY_right->setTickInterval(unit_interval);
        axisY_right->setRange(0, (1.025 * data_max_value_right));

        QColor pen_color = axisY_right->linePen().color();
        pen_color.setNamedColor("#ffcccc");
        axisY_right->setLinePenColor(pen_color);
        axisY_right->setGridLineColor(pen_color);
        // axisY_right->setGridLineVisible(false);
    }

    // chart->legend()->setVisible(false);
    QLegend *legend = chart->legend();
    // Don't show the "fake" workaround_line_series' marker
    legend->markers(workaround_line_series)[0]->setVisible(false);
    legend->setVisible(true);
    legend->setAlignment(Qt::AlignTop);
    legend->setContentsMargins(0, 0, 0, 0);
    legend->layout()->setContentsMargins(0, 0, 0, 0);

    plot_area_box = chart->plotArea();
    QColor pen_color;
    pen_color.setNamedColor("lightgray");
    plot_area_box_item = chartview_scene->addRect(plot_area_box, pen_color);

    has_data = true;
}

void
ChartView::resizeEvent ( QResizeEvent *event ) {
    QtCharts::QChartView::resizeEvent(event);
    // Otherwise, we'll draw the box before ChartView is sized
    if (plot_area_box_item) chartview_scene->removeItem(plot_area_box_item);
    plot_area_box = chart->plotArea();
    QColor pen_color;
    pen_color.setNamedColor("lightgray");
    plot_area_box_item = chartview_scene->addRect(plot_area_box, pen_color);
}

//ChartView::~ChartView ( ) {
//}

void
ChartView::mouseMoveEvent ( QMouseEvent *event ) {
    if (has_data) {
        QRectF plotarea_rect = chart->plotArea();
        if (not plotarea_rect.contains(event->pos()))
            QToolTip::hideText();
        else {
            QString tooltip_text = "";

            QList<QAbstractSeries*> chart_series_list = chart->series();
            // First series is workaround for datetime axis labeling issue
            QPointF mouse_move_point_left = chart->mapToValue(event->pos(), chart_series_list[1]);
            QPointF mouse_move_point_right =
                chart->mapToValue(event->pos(), chart_series_list[chart_series_list.size()-1]);

            qint64 mouse_move_point_right_x = static_cast<qint64>(mouse_move_point_right.x());
            // qDebug() << mouse_move_point_right_x;
            QDateTime mouse_move_datetime = QDateTime().fromMSecsSinceEpoch(mouse_move_point_right_x);
            tooltip_text += mouse_move_datetime.toString("yyyy-MM-dd HH:mm");
            tooltip_text += QString("\n") + QString("L: ") + QString::number(mouse_move_point_left.y(), 'f', 2);
            tooltip_text += QString("   R: ") + QString::number(mouse_move_point_right.y(), 'f', 2);

            QPoint tooltip_pos = event->pos();
            tooltip_pos.setX(this->pos().x() + tooltip_pos.x()); // + tooltip_pos_offset_x)
            tooltip_pos.setY(this->pos().y() + tooltip_pos.y()); // + tooltip_pos_offset_y)

            QToolTip::showText(tooltip_pos, tooltip_text, this);
        }
    }

}

void
ChartView::mousePressEvent ( QMouseEvent *event ) {
    if (has_data) {
        if (zoom_level == 0) {
            QRectF plotarea_rect = chart->plotArea();
            double zoom_area_left =
                qMax((event->pos().x() - (plotarea_rect.width() / (2 * zoom_factor))), plotarea_rect.left());
            double zoom_area_top =
                qMax((event->pos().y() - (plotarea_rect.height() / (2 * zoom_factor))), plotarea_rect.top());
            double zoom_area_width = plotarea_rect.width() / zoom_factor;
            double zoom_area_height = plotarea_rect.height() / zoom_factor;
            if ((zoom_area_left + zoom_area_width) > (plotarea_rect.left() + plotarea_rect.width()))
                zoom_area_left = (plotarea_rect.left() + plotarea_rect.width()) - zoom_area_width;
            if ((zoom_area_top + zoom_area_height) > (plotarea_rect.top() + plotarea_rect.height()))
                zoom_area_top = (plotarea_rect.top() + plotarea_rect.height()) - zoom_area_height;
            QRectF zoom_rect = QRectF(zoom_area_left, zoom_area_top, zoom_area_width, zoom_area_height);
            chart->zoomIn(zoom_rect);
            zoom_level += 1;
        }
        else {
            chart->zoomReset();
            zoom_level -= 1;
        }
    }

}


ControlBar::ControlBar ( QWidget *parent ) : QFrame ( parent ) {
    // Values for relative-to-now begin and end of display period
    period_duration_hours = Initial_Period_Duration_Hours;
    period_end_hours_ago = Initial_Period_End_Hours_Ago;

    setMouseTracking(true);

    int slider_minimum_value = 0;

    int period_duration_slider_maximum_value = 999;
    period_duration_slider_value_span = period_duration_slider_maximum_value - slider_minimum_value;

    int period_end_slider_maximum_value = 1000;
    period_end_slider_value_span = period_end_slider_maximum_value - slider_minimum_value;

    setContentsMargins(0, 0, 0, 0);
    setFrameShape(QFrame::StyledPanel);
    setAutoFillBackground(true);
    setLineWidth(0);
    setMaximumHeight(32);
    // setFrameStyle(QFrame::Plain);

    QHBoxLayout *control_bar_layout = new QHBoxLayout();
    control_bar_layout->setMargin(0);
    control_bar_layout->setContentsMargins(0, 0, 0, 0);
    control_bar_layout->setSpacing(2);
    control_bar_layout->setAlignment(Qt::AlignCenter);

    previous_pushbutton = new QPushButton("⬆", parent=this);
    previous_pushbutton->setFixedWidth(56);
    connect(previous_pushbutton, SIGNAL(clicked()), this, SLOT(emit_previous_signal()));
    previous_pushbutton->setMouseTracking(true);
    control_bar_layout->addWidget(previous_pushbutton);

    period_duration_hours_label = new QLabel("24H", parent=this);
    period_duration_hours_label->setFixedWidth(76);
    period_duration_hours_label->setAlignment(Qt::AlignCenter);
    control_bar_layout->addWidget(period_duration_hours_label);

    period_duration_hours_slider = new QSlider(Qt::Horizontal, parent=this);
    period_duration_hours_slider->setMinimumWidth(360); // 5 pixels per step, 72 steps
    period_duration_hours_slider->setMinimum(slider_minimum_value);
    period_duration_hours_slider->setMaximum(period_duration_slider_maximum_value);
    period_duration_hours_slider->setValue(slider_minimum_value);
    connect(period_duration_hours_slider, SIGNAL(valueChanged(int)),
            this, SLOT(on_period_duration_hours_value_change(int)));
    connect(period_duration_hours_slider, SIGNAL(sliderReleased()), this, SLOT(emit_update_signal()));
    period_duration_hours_slider->setMouseTracking(true);
    control_bar_layout->addWidget(period_duration_hours_slider);

    // min = slider_minimum_value, max = period_duration_slider_maximum_value,
    // value = period_duration_slider_maximum_value, step = 1, size_hint = (0.4, 1))

    duplex_pushbutton = new QPushButton("2", parent=this);
    connect(duplex_pushbutton, SIGNAL(clicked()), this, SLOT(emit_duplex_signal()));
    duplex_pushbutton->setFixedWidth(32);
    duplex_pushbutton->setDown(true);
    duplex_pushbutton->setMouseTracking(true);
    control_bar_layout->addWidget(duplex_pushbutton);

    QPushButton *refresh_pushbutton = new QPushButton("Refresh", parent=this);
    connect(refresh_pushbutton, SIGNAL(clicked()), this, SLOT(emit_update_signal()));
    refresh_pushbutton->setFixedWidth(104);
    control_bar_layout->addWidget(refresh_pushbutton);

    simplex_pushbutton = new QPushButton("1", parent=this);
    connect(simplex_pushbutton, SIGNAL(clicked()), this, SLOT(emit_simplex_signal()));
    simplex_pushbutton->setFixedWidth(32);
    simplex_pushbutton->setMouseTracking(true);
    control_bar_layout->addWidget(simplex_pushbutton);

    period_end_hours_ago_slider = new QSlider(Qt::Horizontal, parent=this);
    period_end_hours_ago_slider->setMinimumWidth(360); // 5 pixels per step, 72 steps
    period_end_hours_ago_slider->setMinimum(slider_minimum_value);
    period_end_hours_ago_slider->setMaximum(period_end_slider_maximum_value);
    period_end_hours_ago_slider->setValue(period_end_slider_maximum_value);
    connect(period_end_hours_ago_slider, SIGNAL(valueChanged(int)),
            this, SLOT(on_period_end_hours_ago_value_change(int)));
    connect(period_end_hours_ago_slider, SIGNAL(sliderReleased()), this, SLOT(emit_update_signal()));
    period_end_hours_ago_slider->setMouseTracking(true);
    control_bar_layout->addWidget(period_end_hours_ago_slider);

    // min = slider_minimum_value, max = period_end_slider_maximum_value,
    // value = period_end_slider_maximum_value, step = 1, size_hint = (0.4, 1))

    period_end_hours_ago_label = new QLabel("0H ago", parent=this);
    period_end_hours_ago_label->setFixedWidth(76);
    period_end_hours_ago_label->setAlignment(Qt::AlignCenter);
    control_bar_layout->addWidget(period_end_hours_ago_label);

    next_pushbutton = new QPushButton("⬇", parent=this);
    next_pushbutton->setFixedWidth(56);
    connect(next_pushbutton, SIGNAL(clicked()), this, SLOT(emit_next_signal()));
    next_pushbutton->setMouseTracking(true);
    control_bar_layout->addWidget(next_pushbutton);

    setLayout(control_bar_layout);

    set_period_duration_hours_value(period_duration_hours);
    set_period_end_hours_ago_value(period_end_hours_ago);
}

// Public functions (used to synchronize multiple TimeSpanControlBars) ...
int
ControlBar::get_period_duration_hours_value ( ) {
    return period_duration_hours;
}

void
ControlBar::set_period_duration_hours_value ( int period_duration_hours_value) {
    period_duration_hours = period_duration_hours_value;
    period_duration_hours_label->setText(period_value_display(period_duration_hours));
//    double slider_value_a = Period_Duration_Hours_Steps.indexOf(period_duration_hours);
//    double slider_value_b = period_duration_slider_value_span *
//                             Period_Duration_Hours_Steps.indexOf(period_duration_hours);
//    double slider_value_c = (period_duration_slider_value_span *
//            Period_Duration_Hours_Steps.indexOf(period_duration_hours)) /
//             Period_Duration_Hours_Steps.count();
    period_duration_hours_slider->setValue
        (1000 - int(round((period_duration_slider_value_span *
                           Period_Duration_Hours_Steps.indexOf(period_duration_hours)) /
                          Period_Duration_Hours_Steps.count())));
}

int
ControlBar::get_period_end_hours_ago_value ( ) {
    return period_end_hours_ago;
}

void
ControlBar::set_period_end_hours_ago_value ( int period_end_hours_ago_value ) {
    period_end_hours_ago = period_end_hours_ago_value;
    period_end_hours_ago_slider->setValue
        (1000 - int(round((period_end_slider_value_span *
                           Period_End_Hours_Ago_Steps.indexOf(period_end_hours_ago)) /
                          Period_End_Hours_Ago_Steps.count())));
    period_end_hours_ago_label->setText(period_value_display(period_end_hours_ago) + " ago");
}
// ... Public functions  (used to synchronize multiple TimeSpanControlBars)

// Private functions ...
QString
ControlBar::period_value_display ( int Period_Value ) {
    QString period_value_string = "";
    if (Period_Value >= 24)
        period_value_string += QString::number(qFloor(Period_Value / 24)) + "D";
    if (((Period_Value % 24) > 0) or (period_value_string.count() == 0)) {
        if (period_value_string.count() > 0) period_value_string += " ";
        period_value_string += QString::number(Period_Value % 24) + "H";
    }
    return period_value_string;
}

void
ControlBar::on_period_duration_hours_value_change ( int period_duration_slider_value ) {
    // print (period_duration_slider_value)
    int period_value_index =
        int(round((Period_Duration_Hours_Steps.count() *
                   abs(period_duration_slider_value - 1000)) / period_duration_slider_value_span));
    period_duration_hours =
        Period_Duration_Hours_Steps[bound(0, (Period_Duration_Hours_Steps.count() - 1), period_value_index)];
    period_duration_hours_label->setText(period_value_display(period_duration_hours));
    // print (period_duration_slider_value, period_value_index, period_duration_hours, period_duration_label.text)
    // return True
}

void
ControlBar::on_period_end_hours_ago_value_change ( int period_end_slider_value ) {
    int period_end_value_index =
        int(round((Period_End_Hours_Ago_Steps.count() *
                   abs(period_end_slider_value - 1000)) / period_end_slider_value_span));
    period_end_hours_ago =
        Period_End_Hours_Ago_Steps[bound(0, (Period_End_Hours_Ago_Steps.count() -1), period_end_value_index)];
    period_end_hours_ago_label->setText(period_value_display(period_end_hours_ago) + " ago");
    // return True
}

void
ControlBar::emit_update_signal ( ) {
    emit metricsUpdate();
}

void
ControlBar::emit_previous_signal ( ) {
    emit metricsPrevious();
}

void
ControlBar::emit_next_signal ( ) {
    emit metricsNext();
}

void
ControlBar::emit_duplex_signal ( ) {
    if (not duplex_pushbutton->isDown()) {
        duplex_pushbutton->setDown(true);
        simplex_pushbutton->setDown(false);
    }
    emit metricsDuplex();
}

void
ControlBar::emit_simplex_signal ( ) {
    if (not simplex_pushbutton->isDown()) {
        duplex_pushbutton->setDown(false);
        simplex_pushbutton->setDown(true);
    }
    emit metricsSimplex();
}

void
ControlBar::mouseMoveEvent ( QMouseEvent *event ) {
    if (rect().contains(event->pos())) {
        QPoint control_bar_pos = pos();

        QPoint tooltip_pos = event->pos();
        tooltip_pos.setX(control_bar_pos.x() + tooltip_pos.x());
        tooltip_pos.setY(control_bar_pos.y() + tooltip_pos.y() + 100);

        if (previous_pushbutton->geometry().contains(event->pos()))
            QToolTip::showText(tooltip_pos, "Previous graph page");
        else if (period_duration_hours_slider->geometry().contains(event->pos()))
            QToolTip::showText(tooltip_pos, "Adjust period of displayed metrics in hours");
        else if (duplex_pushbutton->geometry().contains(event->pos()))
            QToolTip::showText(tooltip_pos, "Duplex page (two graphs)");
        else if (simplex_pushbutton->geometry().contains(event->pos()))
            QToolTip::showText(tooltip_pos, "Simplex page (one graph)");
        else if (period_end_hours_ago_slider->geometry().contains(event->pos()))
            QToolTip::showText(tooltip_pos, "Adjust hours ago of end of displayed metrics period");
        else if (next_pushbutton->geometry().contains(event->pos()))
            QToolTip::showText(tooltip_pos, "Next graph page");
        else QToolTip::hideText();
    }
    else QToolTip::hideText();
}
// ... Private functions

////ControlBar::~ControlBar ( ) {
////}
