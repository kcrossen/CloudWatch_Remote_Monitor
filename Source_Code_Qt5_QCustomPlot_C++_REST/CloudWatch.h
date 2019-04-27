#ifndef CLOUDWATCH_H
#define CLOUDWATCH_H

#include <QtCore>
#include <QObject>
#include <QUrl>
#include <QNetworkAccessManager>
#include <QMessageAuthenticationCode>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QDateTime>
#include <QtXml>

#include "AWS_Metrics.h"
#include "json_helpers.h"

class AWS_CloudWatch : public QObject
{
    Q_OBJECT
public:
    explicit AWS_CloudWatch ( QString Client_Access_Key,
                              QString Client_Secret_Key,
                              QString Client_Region_Name,
                              QObject *parent = nullptr );

    QNetworkReply*
    AWS_CloudWatch_GetMetricStatistics ( QJsonArray Graph_Metric_Descriptor_List,
                                         int Metric_Descriptor_Index,
                                         QDateTime Period_End_UTC, int Period_Duration_Hours,
                                         QVector<Metric_Statistics_Descriptor> *Graph_Metric_Statistics );

    QVector<Metric_Statistics_Descriptor>
    AWS_CloudWatch_GetGraphMetricStatistics ( QJsonArray Graph_Metric_Descriptor_List,
                                              int Graph_Metric_Descriptor_Index,
                                              QDateTime Period_End_UTC, int Period_Duration_Hours );

    QVector<QVector<Metric_Statistics_Descriptor>>
    AWS_CloudWatch_GetPageMetricStatistics ( QJsonArray Graph_Metric_Descriptor_List,
                                             QVector<int> Graph_Metric_Index_List,
                                             QDateTime Period_End_UTC,
                                             int Period_Duration_Hours );

    QNetworkReply*
    AWS_CloudWatch_DescribeAlarmHistory ( QString Alarm_Name,
                                          QDateTime Period_Begin_UTC, QDateTime Period_End_UTC,
                                          QMap<QString, QList<QMap<QString, QString>>> *Alarm_History_Results );

    QMap<QString, QList<QMap<QString, QString>>>
    AWS_CloudWatch_AlarmHistory ( QJsonArray Alarm_Name_List,
                                  QDateTime Period_Begin_UTC, QDateTime Period_End_UTC );

private:
    QNetworkAccessManager *network_access_manager;
    QString aws_access_key;
    QString aws_secret_key;
    QString aws_region_name;

    QByteArray aws_cw_host;
    QByteArray aws_cw_endpoint;

    QHash<QNetworkReply*, QVector<Metric_Statistics_Descriptor>*> getmetricstatistics_reply_data;
    QHash<QNetworkReply*, QMap<QString, QList<QMap<QString, QString>>>*> describealarmhistory_reply_data;

signals:

public slots:
    void
    getmetricstatistics_replyFinished ( );

    void
    describealarmhistory_replyFinished ( );

};

#endif // CLOUDWATCH_H
