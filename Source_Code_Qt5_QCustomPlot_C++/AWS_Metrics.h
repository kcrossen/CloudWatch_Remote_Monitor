#ifndef AWS_METRICS_H
#define AWS_METRICS_H

#include <QtCore>

typedef struct {
    QDateTime datapoint_datetime;
    double datapoint_value;
} Metric_Statistics_Datapoint;

typedef struct {
    QJsonObject Metric_Descriptor;
    QList<Metric_Statistics_Datapoint> Datapoints_Average_List;
    QList<Metric_Statistics_Datapoint> Datapoints_Maximum_List;
    QList<Metric_Statistics_Datapoint> Datapoints_Minimum_List;
    QList<Metric_Statistics_Datapoint> Datapoints_SampleCount_List;
    QList<Metric_Statistics_Datapoint> Datapoints_Sum_List;
} Metric_Statistics_Descriptor;

#endif // AWS_METRICS_H
