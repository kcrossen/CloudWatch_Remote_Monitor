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
#include <aws/monitoring/model/DescribeAlarmHistoryRequest.h>
#include <aws/monitoring/model/DescribeAlarmHistoryResult.h>

#include <aws/monitoring/model/ListMetricsRequest.h>
#include <aws/monitoring/model/ListMetricsResult.h>

#include <aws/monitoring/model/Datapoint.h>

#include "ChartView.h"
#include "ControlBar.h"

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

#include "AWS_Metrics.h"
#include "json_helpers.h"

struct Metric_Statistics_Datapoint_Compare {
    bool operator()(const Metric_Statistics_Datapoint& first_datapoint,
                    const Metric_Statistics_Datapoint& second_datapoint) const {
        return first_datapoint.datapoint_datetime < second_datapoint.datapoint_datetime;
    }
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
    update_alarms (  );

    void
    update_alarm_history ( bool Force_Alarm_History_Display );

    void
    display_alarms ( QString Alarm_History_Text );

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
