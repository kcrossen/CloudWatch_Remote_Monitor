#ifndef CW_REMOTE_H
#define CW_REMOTE_H

#include <QtCore/QDebug>

#include <QMainWindow>
#include <QtCore>
#include <QtGui>
#include <QMainWindow>
#include <QtWidgets>

#include <QThread>
#include <QFuture>
#include <QFutureWatcher>
#include <QtConcurrent/QtConcurrent>

#include <QtCharts/QChartView>
#include <QtCharts/QLineSeries>
#include <QtCore/QDateTime>
#include <QtCharts/QDateTimeAxis>
#include <QtCharts/QValueAxis>
#include <QLegendMarker>

#include <QGraphicsScene>

#include <QToolTip>

#include <QVBoxLayout>
#include <QLabel>

#include <QList>
#include <QMap>

#include <QtGlobal>
#include <QtMath>

#include <algorithm>

#include <aws/core/Aws.h>
#include <aws/core/utils/logging/AWSLogging.h>
#include <aws/core/utils/logging/DefaultLogSystem.h>
#include <aws/core/utils/logging/ConsoleLogSystem.h>

#include <aws/core/client/ClientConfiguration.h>
#include <aws/core/auth/AWSCredentials.h>
#include <aws/core/Region.h>

#include <aws/monitoring/CloudWatchClient.h>
#include <aws/monitoring/CloudWatchEndpoint.h>
#include <aws/monitoring/CloudWatchRequest.h>
#include <aws/monitoring/model/GetMetricStatisticsRequest.h>
#include <aws/monitoring/model/GetMetricStatisticsResult.h>
#include <aws/monitoring/model/Datapoint.h>

static
QMap<QString, Aws::CloudWatch::Model::Statistic> CloudWatch_Statistics
    ( { {"Average", Aws::CloudWatch::Model::Statistic::Average},
        {"Maximum", Aws::CloudWatch::Model::Statistic::Maximum},
        {"Minimum", Aws::CloudWatch::Model::Statistic::Minimum},
        {"SampleCount", Aws::CloudWatch::Model::Statistic::SampleCount},
        {"Sum", Aws::CloudWatch::Model::Statistic::Sum} } );

static
QMap<QString, Aws::CloudWatch::Model::StandardUnit> CloudWatch_Units
    ( { {"Seconds", Aws::CloudWatch::Model::StandardUnit::Seconds},
        {"Microseconds", Aws::CloudWatch::Model::StandardUnit::Microseconds},
        {"Milliseconds", Aws::CloudWatch::Model::StandardUnit::Milliseconds},

        {"Bytes", Aws::CloudWatch::Model::StandardUnit::Bytes},
        {"Kilobytes", Aws::CloudWatch::Model::StandardUnit::Kilobytes},
        {"Megabytes", Aws::CloudWatch::Model::StandardUnit::Megabytes},
        {"Gigabytes", Aws::CloudWatch::Model::StandardUnit::Gigabytes},
        {"Terabytes", Aws::CloudWatch::Model::StandardUnit::Terabytes},

        {"Bits", Aws::CloudWatch::Model::StandardUnit::Bits},
        {"Kilobits", Aws::CloudWatch::Model::StandardUnit::Kilobits},
        {"Megabits", Aws::CloudWatch::Model::StandardUnit::Megabits},
        {"Gigabits", Aws::CloudWatch::Model::StandardUnit::Gigabits},
        {"Terabits", Aws::CloudWatch::Model::StandardUnit::Terabits},

        {"Percent", Aws::CloudWatch::Model::StandardUnit::Percent},
        {"Count", Aws::CloudWatch::Model::StandardUnit::Count},

        {"Bytes/Second", Aws::CloudWatch::Model::StandardUnit::Bytes_Second},
        {"Kilobytes/Second", Aws::CloudWatch::Model::StandardUnit::Kilobytes_Second},
        {"Megabytes/Second", Aws::CloudWatch::Model::StandardUnit::Megabytes_Second},
        {"Gigabytes/Second", Aws::CloudWatch::Model::StandardUnit::Gigabytes_Second},
        {"Terabytes/Second", Aws::CloudWatch::Model::StandardUnit::Terabytes_Second},

        {"Bits/Second", Aws::CloudWatch::Model::StandardUnit::Bits_Second},
        {"Kilobits/Second", Aws::CloudWatch::Model::StandardUnit::Kilobits_Second},
        {"Megabits/Second", Aws::CloudWatch::Model::StandardUnit::Megabits_Second},
        {"Gigabits/Second", Aws::CloudWatch::Model::StandardUnit::Gigabits_Second},
        {"Terabits/Second", Aws::CloudWatch::Model::StandardUnit::Terabits_Second},

        {"Count/Second", Aws::CloudWatch::Model::StandardUnit::Count_Second} } );
//'Seconds'|'Microseconds'|'Milliseconds'|
//  Seconds,
//  Microseconds,
//  Milliseconds,
//'Bytes'|'Kilobytes'|'Megabytes'|'Gigabytes'|'Terabytes'|
//  Bytes,
//  Kilobytes,
//  Megabytes,
//  Gigabytes,
//  Terabytes,
//'Bits'|'Kilobits'|'Megabits'|'Gigabits'|'Terabits'|
//  Bits,
//  Kilobits,
//  Megabits,
//  Gigabits,
//  Terabits,
//'Percent'|'Count'|
//  Percent,
//  Count,
//'Bytes/Second'|'Kilobytes/Second'|'Megabytes/Second'|'Gigabytes/Second'|'Terabytes/Second'|
//  Bytes_Second,
//  Kilobytes_Second,
//  Megabytes_Second,
//  Gigabytes_Second,
//  Terabytes_Second,
//'Bits/Second'|'Kilobits/Second'|'Megabits/Second'|'Gigabits/Second'|'Terabits/Second'|
//  Bits_Second,
//  Kilobits_Second,
//  Megabits_Second,
//  Gigabits_Second,
//  Terabits_Second,
//'Count/Second'|'None',
//  Count_Second,
//  None

typedef struct {
    QDateTime datapoint_datetime;
    double datapoint_value;
} Metric_Statistics_Datapoint;

struct Metric_Statistics_Datapoint_Compare {
    bool operator()(const Metric_Statistics_Datapoint& first_datapoint,
                    const Metric_Statistics_Datapoint& second_datapoint) const {
        return first_datapoint.datapoint_datetime < second_datapoint.datapoint_datetime;
    }
};

typedef struct {
    QJsonObject Metric_Descriptor;
    QList<Metric_Statistics_Datapoint> Datapoints_Average_List;
    QList<Metric_Statistics_Datapoint> Datapoints_Maximum_List;
    QList<Metric_Statistics_Datapoint> Datapoints_Minimum_List;
    QList<Metric_Statistics_Datapoint> Datapoints_SampleCount_List;
    QList<Metric_Statistics_Datapoint> Datapoints_Sum_List;
} Metric_Statistics_Descriptor;

typedef struct {
    QVector<Metric_Statistics_Descriptor> graph_metric_statistics;
} Graph_Metric_Statistics;

typedef struct {
    QVector<Graph_Metric_Statistics> page_metric_statistics;
} Page_Metric_Statistics;


class ControlBar : public QFrame  {
    Q_OBJECT

public:
    ControlBar ( QWidget *parent = nullptr );
    // ~ControlBar ( );

    int
    get_period_duration_hours_value ( );

    void
    set_period_duration_hours_value ( int period_duration_hours_value );

    int
    get_period_end_hours_ago_value ( );

    void
    set_period_end_hours_ago_value ( int period_end_hours_ago_value );

private:
    const QVector<int> Period_Duration_Hours_Steps = QVector<int>(
            {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24,  // 18
             26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48,  // 12
             50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72,  // 12
             74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 96,  // 12
             100, 104, 108, 112, 116, 120,  // 6
             124, 128, 132, 136, 140, 144,  // 6
             148, 152, 156, 160, 164, 168});  // 6

    const QVector<int> Period_End_Hours_Ago_Steps = QVector<int>(
            {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24,  // 19
             26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48,  // 12
             50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72,  // 12
             74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 96,  // 12
             100, 104, 108, 112, 116, 120,  // 6
             124, 128, 132, 136, 140, 144,  // 6
             148, 152, 156, 160, 164, 168});  // 6

    QToolTip *tooltip;

    int period_duration_hours;
    int period_end_hours_ago;

    double period_duration_slider_value_span;
    double period_end_slider_value_span;

    QPushButton *previous_pushbutton;
    QLabel *period_duration_hours_label;
    QSlider *period_duration_hours_slider;
    QPushButton *duplex_pushbutton;
    QPushButton *simplex_pushbutton;
    QSlider *period_end_hours_ago_slider;
    QLabel *period_end_hours_ago_label;
    QPushButton *next_pushbutton;

public slots:

signals:
    void metricsUpdate ( );
    void metricsPrevious ( );
    void metricsNext ( );
    void metricsDuplex ( );
    void metricsSimplex ( );

protected:
    void
    mouseMoveEvent ( QMouseEvent *event );

private:
    QString
    period_value_display ( int Period_Value );

private slots:
    void
    on_period_duration_hours_value_change ( int period_duration_slider_value );

    void
    on_period_end_hours_ago_value_change ( int period_end_slider_value );

    void
    emit_update_signal ( );

    void
    emit_previous_signal ( );

    void
    emit_next_signal ( );

    void
    emit_duplex_signal ( );

    void
    emit_simplex_signal ( );

};


using namespace QtCharts;

class ChartView : public QtCharts::QChartView  {
    Q_OBJECT

public:
    ChartView ( QWidget *parent = nullptr );
    // ~ChartView ( );

    void
    setChartData ( const QVector<Metric_Statistics_Descriptor> Chart_Metric_Statistics_List );

    int zoom_level;

public slots:

protected:
    void
    resizeEvent ( QResizeEvent *event );

    void
    mouseMoveEvent ( QMouseEvent *event );

    void
    mousePressEvent ( QMouseEvent *event );

private:
    bool has_data;

    int zoom_factor;

    QtCharts::QChart *chart;

    QtCharts::QDateTimeAxis *axisX;
    QtCharts::QDateTimeAxis *axisX_top;
    QtCharts::QValueAxis *axisY_left;
    QtCharts::QValueAxis *axisY_right;

    QGraphicsScene *chartview_scene;
    QRectF plot_area_box;
    QGraphicsRectItem *plot_area_box_item;

};

class CW_Remote_Screen : public QWidget {
    Q_OBJECT

public:
    CW_Remote_Screen ( QWidget *parent = nullptr );
    ~CW_Remote_Screen ( );

private:
    int Visible_Graph_Count;
    int Graph_Offset;

    int Period_Duration_Hours;
    int Period_End_Hours_Ago;

    QLabel *empty_label;
    int upper_chartview_height;
    int lower_chartview_height;

    ChartView *Upper_Chartview;
    ControlBar *Control_Bar;
    ChartView *Lower_Chartview;

    QTimer *timer;

protected:

public slots:
    void
    timer_update_page_metrics (  );

    void
    update_page_metrics (  );

    void
    previous_page_metrics (  );

    void
    next_page_metrics (  );

    void
    duplex_metrics (  );

    void
    simplex_metrics (  );

    void
    set_main_window_title (  );
};


class CW_Remote : public QMainWindow {
    Q_OBJECT

public:
    CW_Remote ( QWidget *parent = nullptr );
    ~CW_Remote ( );

    CW_Remote_Screen *CW_Remote_Screen_Widget;

private:

protected:
//    void
//    closeEvent ( QCloseEvent* event );

public slots:

};

#endif // CW_REMOTE_H

//enum Aws::CloudWatch::Model::Statistic
//Enumerator:
//NOT_SET
//SampleCount
//Average
//Sum
//Minimum
//Maximum

//enum Aws::CloudWatch::Model::StandardUnit
//Enumerator:
//NOT_SET
//Seconds
//Microseconds
//Milliseconds
//Bytes
//Kilobytes
//Megabytes
//Gigabytes
//Terabytes
//Bits
//Kilobits
//Megabits
//Gigabits
//Terabits
//Percent
//Count
//Bytes_Second
//Kilobytes_Second
//Megabytes_Second
//Gigabytes_Second
//Terabytes_Second
//Bits_Second
//Kilobits_Second
//Megabits_Second
//Gigabits_Second
//Terabits_Second
//Count_Second
//None


// // Test code
// Aws::String endpoint = Aws::CloudWatch::CloudWatchEndpoint::ForRegion("us-east-1");

//    request.SetStartTime(Aws::Utils::DateTime("2019-04-03T06:30:00Z",
//                                              Aws::Utils::DateFormat::ISO_8601));
//    request.SetEndTime(Aws::Utils::DateTime("2019-04-04T06:30:00Z",
//                                            Aws::Utils::DateFormat::ISO_8601));

//def Get_Metric_Statistics ( Metric_Descriptor, Metric_Statistics_List, Metric_Statistics_Index ):
//    raw_metric_statistics = \
//        cloudwatch_client.get_metric_statistics(MetricName=Metric_Descriptor["MetricName"],
//                                                Namespace=Metric_Descriptor["Namespace"],
//                                                Dimensions=Metric_Descriptor["Dimensions"],
//                                                StartTime=Metric_Descriptor["StartTime"],
//                                                EndTime=Metric_Descriptor["EndTime"],
//                                                Period=Metric_Descriptor["Period"],
//                                                Statistics=Metric_Descriptor["Statistics"],
//                                                Unit=Metric_Descriptor["Unit"])

//    raw_metric_statistics_datapoints = raw_metric_statistics.get("Datapoints", [])
//    nyc_wall_time_offset = NYC_Wall_DateTime_Offset(Metric_Descriptor["EndTime"])
//    nyc_wall_datetime_offset = datetime.timedelta(hours=int(nyc_wall_time_offset) / 100)
//    y_factor = Metric_Descriptor.get("YFactor", 1)

//    data_point_list = []
//    for data_point in raw_metric_statistics_datapoints:
//        data_datetime = data_point["Timestamp"]
//        # This will return some wrong local time values ...
//        # ... if StartTime and EndTime straddle standard <=> daylight savings
//        # The alternative will cause graph to have discontinuity (worse), ...
//        # ... or duplicates of time values (fatal)
//        data_datetime = data_datetime + nyc_wall_datetime_offset
//        data_maximum = data_point["Maximum"] * y_factor
//        data_average = data_point["Average"] * y_factor
//        data_point_list.append((data_datetime, data_maximum, data_average))
//    data_point_list.sort()

//    data_time_max_list = [(time, max) for time, max, avg in data_point_list]
//    data_time_avg_list = [(time, avg) for time, max, avg in data_point_list]

//    prepared_metric_statistics = {}
//    prepared_metric_statistics["Datapoints_Maximum_List"] = data_time_max_list
//    prepared_metric_statistics["Datapoints_Average_List"] = data_time_avg_list

//    prepared_metric_statistics["MetricDescriptor"] = Metric_Descriptor

//    Metric_Statistics_List[Metric_Statistics_Index] = prepared_metric_statistics
