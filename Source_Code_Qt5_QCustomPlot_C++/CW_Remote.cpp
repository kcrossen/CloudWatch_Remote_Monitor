#include <QApplication>

// X axis ticks/labels optimize
// Automatic adaptive alarms
// Click to expand only datetime axis
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


//$ ~/Qt/5.12.2/clang_64/bin/macdeployqt CW_Remote.app

/****************************************************************************
**
** Copyright (C) 2019 Ken Crossen, example expanded into useful application
**
** "Redistribution and use in source and binary forms, with or without
** modification, are permitted provided that the following conditions are
** met:
**   * Redistributions of source code must retain the above copyright
**     notice, this list of conditions and the following disclaimer.
**   * Redistributions in binary form must reproduce the above copyright
**     notice, this list of conditions and the following disclaimer in
**     the documentation and/or other materials provided with the
**     distribution.
**   * Redistributions in source code or binary form may not be sold.
**
****************************************************************************/

/****************************************************************************
**
** Copyright (C) 2015 Klarälvdalens Datakonsult AB, a KDAB Group company, info@kdab.com, author Giuseppe D'Angelo <giuseppe.dangelo@kdab.com>
** Copyright (C) 2015 Samuel Gaist <samuel.gaist@edeltech.ch>
** Copyright (C) 2015 The Qt Company Ltd.
** Contact: http://www.qt.io/licensing/
**
** This file is part of the examples of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:BSD$
** You may use this file under the terms of the BSD license as follows:
**
** "Redistribution and use in source and binary forms, with or without
** modification, are permitted provided that the following conditions are
** met:
**   * Redistributions of source code must retain the above copyright
**     notice, this list of conditions and the following disclaimer.
**   * Redistributions in binary form must reproduce the above copyright
**     notice, this list of conditions and the following disclaimer in
**     the documentation and/or other materials provided with the
**     distribution.
**   * Neither the name of The Qt Company Ltd nor the names of its
**     contributors may be used to endorse or promote products derived
**     from this software without specific prior written permission.
**
**
** THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
** "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
** LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
** A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
** OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
** SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
** LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
** DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
** THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
** (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
** OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
**
** $QT_END_LICENSE$
**
****************************************************************************/


#include "CW_Remote.h"

using namespace Aws;
using namespace Aws::Auth;
using namespace Aws::Client;
using namespace Aws::CloudWatch;
using namespace Aws::CloudWatch::Model;

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
int Initial_Refresh_Interval_Seconds = 60;

static
int Initial_Graph_Visible_Count = 2;

static
int Initial_Period_Duration_Hours = 24;
static
int Initial_Period_End_Hours_Ago = 0;

static
bool Automatic_Alarm_History = true;

static
CW_Remote *CW_Remote_Main_Window;

static
QJsonObject CW_Remote_ini;

static
QJsonArray Graph_Metric_Descriptor_List;

static
QJsonArray Alarm_Name_List;

static
CloudWatchClient *CloudWatch_Client = nullptr;

static
QVector<Metric_Statistics_Descriptor> Upper_Graph_Metric_Statistics;

static
QVector<Metric_Statistics_Descriptor> Lower_Graph_Metric_Statistics;


static
bool
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

    if (not raw_metric_statistics_outcome.IsSuccess()) return false; // Failed

    // Success
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

    return true;
}

using namespace QtConcurrent;

QVector<Metric_Statistics_Descriptor>
Get_Graph_Metric_Statistics ( int Graph_Metric_Descriptor_Index,
                              QDateTime Period_End_UTC, int Period_Duration_Hours ) {
    bool graph_success = true;
    QJsonArray graph_metric_descriptor = Graph_Metric_Descriptor_List[Graph_Metric_Descriptor_Index].toArray();
    QVector<Metric_Statistics_Descriptor> graph_metrics_statistics_list(graph_metric_descriptor.size());
    QVector<QFuture<bool>> future_list;
    QVector<bool> success_list;
    for (int metric_idx = 0; metric_idx < graph_metric_descriptor.size(); metric_idx++) {
        // Get_Metric_Statistics(Graph_Metric_Descriptor_Index, metric_idx,
        //                       Period_End_UTC, Period_Duration_Hours,
        //                       &metrics_statistics_list);
        QFuture<bool> future = QtConcurrent::run(Get_Metric_Statistics, Graph_Metric_Descriptor_Index, metric_idx,
                                                 Period_End_UTC, Period_Duration_Hours,
                                                 &graph_metrics_statistics_list);
        future_list.append(future);
        for (int idx = 0; idx < future_list.size(); idx++) {
            QFuture<bool> future = future_list[idx];
            future.waitForFinished();
            if (not future.result()) graph_success = false;
        }
    }
    if (graph_success) return graph_metrics_statistics_list;
    else return QVector<Metric_Statistics_Descriptor>(0);
}

QVector<QVector<Metric_Statistics_Descriptor>>
Get_Page_Metric_Statistics ( QVector<int> Graph_Metric_Index_List,
                             QDateTime Period_End_UTC,
                             int Period_Duration_Hours ) {

    if (Graph_Metric_Index_List.count() == 0) return QVector<QVector<Metric_Statistics_Descriptor>>(0);

    bool page_success = true;

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

    QVector<QFuture<bool>> future_list;

    if (Graph_Metric_Index_List.count() > 0) {
        int graph_metric_index = Graph_Metric_Index_List[0];
        QJsonArray first_graph_metric_descriptor =
            Graph_Metric_Descriptor_List[graph_metric_index].toArray();
        for (int metric_idx = 0; metric_idx < first_graph_metric_descriptor.size(); metric_idx++) {
            // Get_Metric_Statistics(Graph_Metric_Descriptor_Index, metric_idx,
            //                       Period_End_UTC, Period_Duration_Hours,
            //                       &metrics_statistics_list);
            QFuture<bool> future = QtConcurrent::run(Get_Metric_Statistics, graph_metric_index, metric_idx,
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
            QFuture<bool> future = QtConcurrent::run(Get_Metric_Statistics, graph_metric_index, metric_idx,
                                                     Period_End_UTC, Period_Duration_Hours,
                                                     &second_graph_metric_statistics_list);
            future_list.append(future);
        }
    }

    // Wait for everything to finish
    for (int idx = 0; idx < future_list.size(); idx++) {
        QFuture<bool> future = future_list[idx];
        future.waitForFinished();
        if (not future.result()) page_success = false;
    }

    if (not page_success) return QVector<QVector<Metric_Statistics_Descriptor>>(0);

    QVector<QVector<Metric_Statistics_Descriptor>> page_graph_metric_statistics_list;
    if (Graph_Metric_Index_List.count() > 0)
        page_graph_metric_statistics_list.append(first_graph_metric_statistics_list);
    if (Graph_Metric_Index_List.count() > 1)
        page_graph_metric_statistics_list.append(second_graph_metric_statistics_list);

    return page_graph_metric_statistics_list;
}


static
bool
Describe_Alarm_History ( QString Alarm_Name,
                         QDateTime Period_Begin_UTC, QDateTime Period_End_UTC,
                         QMap<QString, QList<QMap<QString, QString>>> *Alarm_History_Results ) {

    DescribeAlarmHistoryRequest request;
    request.SetAlarmName(Alarm_Name.toStdString());
    request.SetHistoryItemType(HistoryItemType::StateUpdate);
    request.SetStartDate(Period_Begin_UTC.toMSecsSinceEpoch());
    request.SetEndDate(Period_End_UTC.toMSecsSinceEpoch());
    request.SetMaxRecords(100);

    DescribeAlarmHistoryOutcome raw_alarm_history_outcome =
        CloudWatch_Client->DescribeAlarmHistory(request);

    DescribeAlarmHistoryResult raw_alarm_history_result;

    if (not raw_alarm_history_outcome.IsSuccess()) return false; // Failed

    raw_alarm_history_result = raw_alarm_history_outcome.GetResult();

    // Aws::String next_token = raw_alarm_history_result.GetNextToken();
    // bool done = next_token.empty();

    Aws::Vector<AlarmHistoryItem> alarm_history_list = raw_alarm_history_result.GetAlarmHistoryItems();

    QList<QMap<QString, QString>> alarm_history;
    for (unsigned long idx = 0; idx < alarm_history_list.size(); idx++) {
        AlarmHistoryItem history_item = alarm_history_list[idx];

        QMap<QString, QString> alarm_history_item;

        Aws::String history_item_alarm_name = history_item.GetAlarmName();
        alarm_history_item["AlarmName"] = QString::fromUtf8(history_item_alarm_name.data()/*, history_item_alarm_name.size()*/);

        QDateTime history_item_datetime_utc = QDateTime().fromMSecsSinceEpoch(history_item.GetTimestamp().Millis());
        alarm_history_item["AlarmDateTime"] = history_item_datetime_utc.toLocalTime().toString();

        Aws::String history_item_summary = history_item.GetHistorySummary();
        alarm_history_item["AlarmSummary"] = QString::fromUtf8(history_item_summary.data()/*, history_item_summary.size()*/);

        Aws::String history_item_data = history_item.GetHistoryData();
        alarm_history_item["AlarmData"] = QString::fromUtf8(history_item_data.data()/*, history_item_data.size()*/);

        alarm_history.append(alarm_history_item);
    }

    if (alarm_history.size() > 0)
        (*Alarm_History_Results)[Alarm_Name] = alarm_history;

    return true;
}

static
QMap<QString, QList<QMap<QString, QString>>>
Alarm_History ( QJsonArray Alarm_Name_List ) {
    QMap<QString, QList<QMap<QString, QString>>> alarm_history_results;
    if (Alarm_Name_List.count() == 0) return alarm_history_results;

    bool alarm_success = true;

    QDateTime datetime_now_utc = QDateTime::currentDateTimeUtc();
    QDateTime datetime_yesterday_utc = datetime_now_utc.addSecs(-(24 * 60 * 60));

    QVector<QFuture<bool>> future_list;
    for (int idx = 0; idx < Alarm_Name_List.count(); idx++) {
        QString alarm_name = Alarm_Name_List[idx].toString();
        QFuture<bool> future = QtConcurrent::run(Describe_Alarm_History, alarm_name,
                                                 datetime_yesterday_utc, datetime_now_utc,
                                                 &alarm_history_results);
        future_list.append(future);
    }

    // Wait for everything to finish
    for (int idx = 0; idx < future_list.size(); idx++) {
        QFuture<bool> future = future_list[idx];
        future.waitForFinished();
        if (not future.result()) alarm_success = false;
    }

    if (not alarm_success) alarm_history_results.clear();

    return alarm_history_results;
}


using namespace Aws::Utils::Logging;

int main ( int argc, char* argv[] ) {

//    Aws::SDKOptions options;
//    Aws::InitAPI(options);
//    {
//        Aws::CloudWatch::CloudWatchClient cw;
//        Aws::CloudWatch::Model::ListMetricsRequest request;

//        request.SetMetricName("CPUUtilization");
//        request.SetNamespace("AWS/RDS");

//        bool done = false;
//        bool header = false;
//        while (!done)
//        {
//            auto outcome = cw.ListMetrics(request);
//            const bool outcome_is_success = outcome.IsSuccess();
//            const auto outcome_error = outcome.GetError();
//            if (!outcome.IsSuccess())
//            {
//                std::cout << "Failed to list CloudWatch metrics:" <<
//                    outcome.GetError().GetMessage() << std::endl;
//                break;
//            }
//            done = true;
//        }

//    }
//    Aws::ShutdownAPI(options);

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

    QString layout = get_json_string_value(CW_Remote_ini, "layout", "paged");
    if (layout == "duplex") Initial_Graph_Visible_Count = 2;
    else Initial_Graph_Visible_Count = 1;

    if (CW_Remote_ini.contains("refresh_interval_seconds") and
        CW_Remote_ini["refresh_interval_seconds"].isDouble())
        Initial_Refresh_Interval_Seconds = CW_Remote_ini["refresh_interval_seconds"].toInt();

    Initial_Period_Duration_Hours = 24;
    if (CW_Remote_ini.contains("initial_period_hours") and
        CW_Remote_ini["initial_period_hours"].isDouble())
        Initial_Period_Duration_Hours = CW_Remote_ini["initial_period_hours"].toInt();

    Graph_Metric_Descriptor_List = CW_Remote_ini["metric_descriptor_list"].toArray();
    Alarm_Name_List = CW_Remote_ini["alarm_name_list"].toArray();

    SDKOptions cw_remote_options;
//    options.loggingOptions.logLevel = Aws::Utils::Logging::LogLevel::Off;

//    options.loggingOptions.logLevel = LogLevel::Off;
//    options.loggingOptions.logger_create_fn = [] { return std::make_shared<ConsoleLogSystem>(LogLevel::Off); };

//    Aws::Utils::Logging::InitializeAWSLogging(
//        Aws::MakeShared<Aws::Utils::Logging::DefaultLogSystem>(
//            "RunUnitTests", Aws::Utils::Logging::LogLevel::Off, "aws_sdk_"));
//    Aws::Utils::Logging::ShutdownAWSLogging();
    InitAPI(cw_remote_options);

    AWSCredentials credentials;
    credentials.SetAWSAccessKeyId(aws_access_id.toStdString());
    credentials.SetAWSSecretKey(aws_secret_key.toStdString());

    ClientConfiguration client_configuration;
    client_configuration.region = region_name.toStdString();
    client_configuration.scheme = Aws::Http::Scheme::HTTPS;
    client_configuration.connectTimeoutMs = 30000;
    client_configuration.requestTimeoutMs = 120000;

    CloudWatchClient cloudwatch_client(credentials, client_configuration);
    CloudWatch_Client = &cloudwatch_client;

    CW_Remote MainWindow;
    MainWindow.setContentsMargins(0, 0, 0, 0);
    MainWindow.show();

    int return_code = Application.exec();

    Aws::Utils::Logging::ShutdownAWSLogging();

    ShutdownAPI(cw_remote_options);

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
    int descriptor_list_length = Graph_Metric_Descriptor_List.count();

    Visible_Graph_Count = qMin(qMin(descriptor_list_length, Initial_Graph_Visible_Count), 2);
    Graph_Offset = 0;

    setContentsMargins(0, 0, 0, 0);

    Period_Duration_Hours = Initial_Period_Duration_Hours;
    Period_End_Hours_Ago = Initial_Period_End_Hours_Ago;

    empty_label = new QLabel("");
    empty_label->setMaximumHeight(1);

    Control_Bar = new ControlBar(Initial_Period_Duration_Hours, Initial_Period_End_Hours_Ago);
    connect(Control_Bar, SIGNAL(alarmsUpdate()), this, SLOT(update_alarms()));
    connect(Control_Bar, SIGNAL(metricsUpdate()), this, SLOT(update_page_metrics()));
    connect(Control_Bar, SIGNAL(metricsPrevious()), this, SLOT(previous_page_metrics()));
    connect(Control_Bar, SIGNAL(metricsNext()), this, SLOT(next_page_metrics()));
    connect(Control_Bar, SIGNAL(metricsDuplex()), this, SLOT(duplex_metrics()));
    connect(Control_Bar, SIGNAL(metricsSimplex()), this, SLOT(simplex_metrics()));

    // Upper_Chartview = new ChartView();
    // Lower_Chartview = new ChartView();

    QDateTime datetime_now_utc = QDateTime::currentDateTimeUtc();
    QDateTime period_end_utc = datetime_now_utc.addSecs(-(Period_End_Hours_Ago * (60 * 60)));

    // QVector<Metric_Statistics_Descriptor> upper_graph_metric_statistics =
    //     Get_Graph_Metric_Statistics((Graph_Offset + 0), period_end_utc, Period_Duration_Hours);

    // QVector<Metric_Statistics_Descriptor> lower_graph_metric_statistics =
    //     Get_Graph_Metric_Statistics((Graph_Offset + 1), period_end_utc, Period_Duration_Hours);

    QVector<QVector<Metric_Statistics_Descriptor>> page_graph_metric_statistics =
        Get_Page_Metric_Statistics ( QVector<int>( { (Graph_Offset + 0), (Graph_Offset + 1) } ),
                                     period_end_utc, Period_Duration_Hours );

    if (page_graph_metric_statistics.size() == 2) {
        QVector<Metric_Statistics_Descriptor> upper_graph_metric_statistics = page_graph_metric_statistics[0];
        QVector<Metric_Statistics_Descriptor> lower_graph_metric_statistics = page_graph_metric_statistics[1];

        // Upper_Chartview->setChartData(upper_graph_metric_statistics);
        Upper_CustomPlot = new CustomPlot(upper_graph_metric_statistics);
        // Lower_Chartview->setChartData(lower_graph_metric_statistics);
        Lower_CustomPlot = new CustomPlot(lower_graph_metric_statistics);
    }
    else if (Visible_Graph_Count == 1) {
        QVector<Metric_Statistics_Descriptor> lower_graph_metric_statistics =
            Get_Graph_Metric_Statistics((Graph_Offset + 0), period_end_utc, Period_Duration_Hours);
        if (lower_graph_metric_statistics.size() >= 1)
            // Lower_Chartview->setChartData(lower_graph_metric_statistics);
            Lower_CustomPlot->setCustomPlotData(lower_graph_metric_statistics);
    }

    QVBoxLayout *main_window_layout = new QVBoxLayout();
    main_window_layout->setMargin(0);
    main_window_layout->setContentsMargins(0, 0, 0, 0);
    main_window_layout->setSpacing(0);

    // main_window_layout->addWidget(Upper_Chartview, 50);
    main_window_layout->addWidget(Upper_CustomPlot, 50);
    main_window_layout->addWidget(Control_Bar, 0);
    // main_window_layout->addWidget(Lower_Chartview, 50);
    main_window_layout->addWidget(Lower_CustomPlot, 50);

    setLayout(main_window_layout);

    set_main_window_title();

    setAttribute(Qt::WA_AlwaysShowToolTips);
    setMouseTracking(true);

    timer = new QTimer(this);
    connect(timer, SIGNAL(timeout()), this, SLOT(timer_update_page_metrics()));
    // Default 60 seconds as milliseconds
    timer->start(Initial_Refresh_Interval_Seconds * 1000);
}

CW_Remote_Screen::~CW_Remote_Screen ( ) {
}

void
CW_Remote_Screen::update_alarms (  ) {
    update_alarm_history(true);
}

void
CW_Remote_Screen::update_alarm_history ( bool Force_Alarm_History_Display ) {
    QMap<QString, QList<QMap<QString, QString>>> alarms_history = Alarm_History(Alarm_Name_List);

    if (alarms_history.size() == 0) return;

    QList<QString> alarm_name_list = alarms_history.uniqueKeys();
    QString alarm_history_text;

    bool alarm_currently_in_alarm_state = false;

    for (int key_idx = 0; key_idx < alarm_name_list.size(); key_idx++) {
        QString alarm_name = alarm_name_list[key_idx];
        if (alarm_history_text.size() > 0) alarm_history_text += "\n\n";
        alarm_history_text += alarm_name + ":";
        QList<QMap<QString, QString>> alarm_detail_list = alarms_history.value(alarm_name);
        for (int detail_idx = 0; detail_idx < alarm_detail_list.size(); detail_idx++) {
            QMap<QString, QString> alarm_detail_map = alarm_detail_list[detail_idx];
            QString alarm_datetime = alarm_detail_map["AlarmDateTime"];
            QString alarm_summary = alarm_detail_map["AlarmSummary"];

            if ((detail_idx == 0) and
                (alarm_summary == "Alarm updated from OK to ALARM"))
                alarm_currently_in_alarm_state = true;

            QJsonObject alarm_data = QJsonDocument::fromJson(alarm_detail_map["AlarmData"].toUtf8()).object();
            QJsonObject alarm_data_new_state = alarm_data["newState"].toObject();
            QString alarm_data_new_state_reason = alarm_data_new_state["stateReason"].toString();
            int ch_idx = 0;
            ch_idx = alarm_data_new_state_reason.indexOf("[");
            alarm_data_new_state_reason.remove(0, (ch_idx + 1));
            ch_idx = alarm_data_new_state_reason.indexOf(".");
            int ch_end_idx = alarm_data_new_state_reason.indexOf("]");
            alarm_data_new_state_reason.remove((ch_idx + 2), (ch_end_idx - (ch_idx + 1)));
            alarm_data_new_state_reason.replace(" was not greater than the threshold (", " < ");
            alarm_data_new_state_reason.replace(" was greater than the threshold (", " > ");
            alarm_data_new_state_reason.replace(").", "");
            // qDebug() << alarm_data_new_state_reason;
            if (alarm_summary == "Alarm updated from OK to ALARM")
                alarm_history_text +=
                    "\n  " + alarm_datetime + ": ALARM\n    (value " +
                    alarm_data_new_state_reason + " threshold)";
            else if (alarm_summary == "Alarm updated from ALARM to OK")
                alarm_history_text +=
                    "\n  " + alarm_datetime + ": OK\n    (value " +
                    alarm_data_new_state_reason + " threshold)";
            else
                alarm_history_text += "\n  " + alarm_datetime + ":\n    " + alarm_summary;
        }
    }

    if (alarm_currently_in_alarm_state or Force_Alarm_History_Display) {
        if (alarm_currently_in_alarm_state and (not Force_Alarm_History_Display))
            // Only routine sceduled with alarm currently in alarm state
            QApplication::beep();
        display_alarms(alarm_history_text);
    }
}

void
CW_Remote_Screen::display_alarms ( QString Alarm_History_Text ) {
    QMessageBox Alarm_History_MessageBox;
    Alarm_History_MessageBox.setFixedWidth(800);
    Alarm_History_MessageBox.setText(Alarm_History_Text);
    Alarm_History_MessageBox.exec();
}

void
CW_Remote_Screen::timer_update_page_metrics (  ) {
    // if (((Visible_Graph_Count == 2) and
    //      (Upper_Chartview->zoom_level == 0) and (Lower_Chartview->zoom_level == 0)) or
    //     ((Visible_Graph_Count == 1) and (Lower_Chartview->zoom_level == 0))) update_page_metrics();
    if (((Visible_Graph_Count == 2) and
         (Upper_CustomPlot->zoom_level == 0) and (Lower_CustomPlot->zoom_level == 0)) or
        ((Visible_Graph_Count == 1) and (Lower_CustomPlot->zoom_level == 0))) update_page_metrics();

    if (Automatic_Alarm_History) update_alarm_history(false);
}

void
CW_Remote_Screen::update_page_metrics (  ) {
    Period_Duration_Hours = Control_Bar->get_period_duration_hours_value();
    Period_End_Hours_Ago = Control_Bar->get_period_end_hours_ago_value();

    set_main_window_title();

    QDateTime datetime_now_utc = QDateTime::currentDateTimeUtc();
    QDateTime period_end_utc = datetime_now_utc.addSecs(-(Period_End_Hours_Ago * (60 * 60)));

    if (Visible_Graph_Count >= 2) {
        QVector<QVector<Metric_Statistics_Descriptor>> page_graph_metric_statistics =
            Get_Page_Metric_Statistics ( QVector<int>( { (Graph_Offset + 0), (Graph_Offset + 1) } ),
                                         period_end_utc, Period_Duration_Hours );

        if (page_graph_metric_statistics.size() == 2) {
            QVector<Metric_Statistics_Descriptor> upper_graph_metric_statistics = page_graph_metric_statistics[0];
            QVector<Metric_Statistics_Descriptor> lower_graph_metric_statistics = page_graph_metric_statistics[1];

            // Upper_Chartview->setChartData(upper_graph_metric_statistics);
            Upper_CustomPlot->setCustomPlotData(upper_graph_metric_statistics);
            // Lower_Chartview->setChartData(lower_graph_metric_statistics);
            Lower_CustomPlot->setCustomPlotData(lower_graph_metric_statistics);

        }
    }
    else if (Visible_Graph_Count == 1) {
        QVector<Metric_Statistics_Descriptor> lower_graph_metric_statistics =
            Get_Graph_Metric_Statistics((Graph_Offset + 0), period_end_utc, Period_Duration_Hours);
        if (lower_graph_metric_statistics.size() >= 1)
            // Lower_Chartview->setChartData(lower_graph_metric_statistics);
            Lower_CustomPlot->setCustomPlotData(lower_graph_metric_statistics);
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
        // main_window_layout->replaceWidget(empty_label, Upper_Chartview, Qt::FindDirectChildrenOnly);
        // Lower_Chartview->setMaximumHeight(lower_chartview_height);
        // Upper_Chartview->setMaximumHeight(upper_chartview_height);

        main_window_layout->replaceWidget(empty_label, Upper_CustomPlot, Qt::FindDirectChildrenOnly);
        Lower_CustomPlot->setMaximumHeight(lower_customplot_height);
        Upper_CustomPlot->setMaximumHeight(upper_customplot_height);

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
        // upper_chartview_height = Upper_Chartview->height();
        // lower_chartview_height = Lower_Chartview->height();
        upper_customplot_height = Upper_CustomPlot->height();
        lower_customplot_height = Lower_CustomPlot->height();

        QLayout *main_window_layout = layout();
        // main_window_layout->replaceWidget(Upper_Chartview, empty_label, Qt::FindDirectChildrenOnly);
        main_window_layout->replaceWidget(Upper_CustomPlot, empty_label, Qt::FindDirectChildrenOnly);

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
