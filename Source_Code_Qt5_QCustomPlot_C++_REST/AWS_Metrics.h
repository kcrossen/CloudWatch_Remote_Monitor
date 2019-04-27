#ifndef AWS_METRICS_H
#define AWS_METRICS_H

#include <QtCore>

typedef struct {
    QDateTime datapoint_datetime;
    double datapoint_value;
} Metric_Statistics_Datapoint;

typedef struct {
    QJsonObject Metric_Descriptor;
    QVector<double> *Datapoints_DateTime_List;
    QVector<double> *Datapoints_Average_List;
    QVector<double> *Datapoints_Maximum_List;
    QVector<double> *Datapoints_Minimum_List;
    QVector<double> *Datapoints_SampleCount_List;
    QVector<double> *Datapoints_Sum_List;
} Metric_Statistics_Descriptor;

#endif // AWS_METRICS_H
