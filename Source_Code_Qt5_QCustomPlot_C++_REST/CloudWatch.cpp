#include "CloudWatch.h"

static
QString AWS_DateTimeFormat = "yyyyMMddThhmmssZ";
static
QString AWS_DateFormat = "yyyyMMdd";

static
QByteArray method = "POST";
static
QByteArray service = "monitoring";

static
QByteArray content_type = "application/x-www-form-urlencoded; charset=utf-8";
static
QByteArray signed_headers = "content-type;host;x-amz-date;x-amz-target";

static
QByteArray algorithm = "AWS4-HMAC-SHA256";
static
QCryptographicHash::Algorithm hashAlgorithm = QCryptographicHash::Sha256;

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

AWS_CloudWatch::AWS_CloudWatch ( QString Client_Access_Key,
                                 QString Client_Secret_Key,
                                 QString Client_Region_Name,
                                 QObject *parent ) : QObject( parent ) {
    network_access_manager = new QNetworkAccessManager(this);
    // connect(network_access_manager, SIGNAL(finished(QNetworkReply*)),
    //         this, SLOT(replyFinished(QNetworkReply*)));
    aws_access_key = Client_Access_Key;
    aws_secret_key = Client_Secret_Key;
    aws_region_name = Client_Region_Name;

    aws_cw_host = "monitoring." + aws_region_name.toUtf8() + ".amazonaws.com";
    aws_cw_endpoint = "https://monitoring." + aws_region_name.toUtf8() + ".amazonaws.com/";
}

static
QByteArray getSignatureKey ( QString key, QString date_stamp, QString regionName, QString serviceName ) {
    return QMessageAuthenticationCode::hash("aws4_request",
                                            QMessageAuthenticationCode::hash(serviceName.toUtf8(),
                                            QMessageAuthenticationCode::hash(regionName.toUtf8(),
                                            QMessageAuthenticationCode::hash(date_stamp.toUtf8(),
                                            "AWS4"+key.toUtf8(),
                                            hashAlgorithm), hashAlgorithm), hashAlgorithm), hashAlgorithm);
}

QNetworkReply*
AWS_CloudWatch::AWS_CloudWatch_GetMetricStatistics ( QJsonArray Graph_Metric_Descriptor_List,
                                                     int Metric_Descriptor_Index,
                                                     QDateTime Period_End_UTC, int Period_Duration_Hours,
                                                     QVector<Metric_Statistics_Descriptor> *Graph_Metric_Statistics ) {

    QJsonObject metric_descr = Graph_Metric_Descriptor_List[Metric_Descriptor_Index].toObject();
    QString payload = QString("Action=GetMetricStatistics") + QString("&") + QString("Version=2010-08-01");

    // "Statistics.member.2=Maximum&Statistics.member.1=Average&Namespace=AWS%2FRDS&Period=60&Dimensions.member.1.Value=prod-stories-scale-replica&Version=2010-08-01&StartTime=2019-04-25T02%3A48%3A53.593753Z&Action=GetMetricStatistics&Dimensions.member.1.Name=DBInstanceIdentifier&EndTime=2019-04-26T02%3A48%3A53.593753Z&Unit=Count%2FSecond&MetricName=WriteIOPS";

    QString metric_name = get_json_string_value(metric_descr, "MetricName", "");
    payload +=  QString("&") + QString("MetricName") + QString("=") + QUrl::toPercentEncoding(metric_name);
    QString name_space = get_json_string_value(metric_descr, "Namespace", "");
    payload +=  QString("&") + QString("Namespace") + QString("=") + QUrl::toPercentEncoding(name_space);

    QDateTime Period_Begin_UTC = Period_End_UTC.addSecs(-(60 * 60 * Period_Duration_Hours));

    // request.SetStartTime(Period_Begin_UTC.toMSecsSinceEpoch());
    payload +=  QString("&") + QString("StartTime") + QString("=") +
                QUrl::toPercentEncoding(Period_Begin_UTC.toString(Qt::ISODate));

    // request.SetEndTime(Period_End_UTC.toMSecsSinceEpoch());
    payload +=  QString("&") + QString("EndTime") + QString("=") +
                QUrl::toPercentEncoding(Period_End_UTC.toString(Qt::ISODate));

    // QDateTime period_end_local = Period_End_UTC.toLocalTime();
    QDateTime period_end_local = QDateTime(Period_End_UTC.date(), Period_End_UTC.time(), Qt::LocalTime);
    long period_local_offset_seconds = Period_End_UTC.secsTo(period_end_local);

    // qDebug() << Period_End_UTC;
    // qDebug() << period_end_local;

    // request.SetPeriod(Optimize_DataPoint_Summary_Seconds(Period_Duration_Hours));
    payload +=  QString("&") + QString("Period") + QString("=") +
                QString::number(Optimize_DataPoint_Summary_Seconds(Period_Duration_Hours));

    QJsonArray dimensions = metric_descr["Dimensions"].toArray();
    QJsonObject dimension_n = dimensions.at(0).toObject();
    QString dimension_name = get_json_string_value(dimension_n, "Name", "");
    QString dimension_value = get_json_string_value(dimension_n, "Value", "");

    // request_dimension.SetName(dimension_name.toStdString());
    // request_dimension.SetValue(dimension_value.toStdString());
    // request.AddDimensions(request_dimension);
    payload +=  QString("&") + QString("Dimensions.member.1.Name") + QString("=") +
                QUrl::toPercentEncoding(dimension_name);
    payload +=  QString("&") + QString("Dimensions.member.1.Value") + QString("=") +
                QUrl::toPercentEncoding(dimension_value);

    // bool request_average = false;
    // bool request_maximum = false;
    // bool request_minimum = false;
    // bool request_samplecount = false;
    // bool request_sum = false;
    QJsonArray statistics = metric_descr["Statistics"].toArray();
    for (int idx = 0; idx < statistics.size(); idx++) {
        QString stat_string = statistics[idx].toString();
        // Adaptive to enum: Average, Minimum, Maximum, SampleCount, Sum ...
        // if (stat_string == "Average") request_average = true;
        // else if (stat_string == "Maximum") request_maximum = true;
        // else if (stat_string == "Minimum") request_minimum = true;
        // else if (stat_string == "SampleCount") request_samplecount = true;
        // else if (stat_string == "Sum") request_sum = true;
        // ... Adaptive to enum: Average, Minimum, Maximum, SampleCount, Sum
        // {@@@@@} Should check for error here.
        // Statistic statistic = CloudWatch_Statistics[stat_string];
        // {@@@@@} Should check for error here.
        // request.AddStatistics(statistic);
        payload +=  QString("&") + QString("Statistics.member.") + QString::number(idx + 1) + QString("=") +
                    QUrl::toPercentEncoding(stat_string);
    }

    QString unit_string = get_json_string_value(metric_descr, "Unit", " ");
    // {@@@@@} Should check for error here.
    // StandardUnit unit = CloudWatch_Units[unit_string];
    // {@@@@@} Should check for error here.
    // request.SetUnit(unit);
    payload +=  QString("&") + QString("Unit") + QString("=") + QUrl::toPercentEncoding(unit_string);

    QString request_payload = payload;
    // "Statistics.member.2=Maximum&Statistics.member.1=Average&Namespace=AWS%2FRDS&Period=60&Dimensions.member.1.Value=prod-stories-scale-replica&Version=2010-08-01&StartTime=2019-04-25T02%3A48%3A53.593753Z&Action=GetMetricStatistics&Dimensions.member.1.Name=DBInstanceIdentifier&EndTime=2019-04-26T02%3A48%3A53.593753Z&Unit=Count%2FSecond&MetricName=WriteIOPS";

    double y_factor = 1;
    if (metric_descr.contains("YFactor") and metric_descr["YFactor"].isDouble())
        y_factor = metric_descr["YFactor"].toDouble();

    // qDebug() << payload;
    // qDebug() << request_payload;

    // amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    QByteArray amz_date = QDateTime::currentDateTimeUtc().toString(AWS_DateTimeFormat).toUtf8();
    QByteArray amz_target = "GraniteServiceVersion20100801.GetMetricStatistics";
    // date_stamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope
    QByteArray date_stamp = QDateTime::currentDateTimeUtc().toString(AWS_DateFormat).toUtf8();

    QUrl endpoint_url = QUrl(aws_cw_endpoint);
    QNetworkRequest request(endpoint_url);
    request.setRawHeader("Content-Type", content_type);
    request.setRawHeader("X-Amz-Target", amz_target);
    request.setRawHeader("X-Amz-Date", amz_date);

    QByteArray canonical_uri = "/";
    QByteArray canonical_querystring = "";

    QByteArray canonical_headers =
        "content-type:" + content_type + '\n' +
        "host:" + aws_cw_host + '\n' +
        "x-amz-date:" + amz_date + '\n' +
        "x-amz-target:" + amz_target + '\n';

    QByteArray payload_hash = QCryptographicHash::hash(request_payload.toUtf8(), hashAlgorithm).toHex();

    QByteArray canonical_request =
        method + '\n' +
        canonical_uri + '\n' +
        canonical_querystring + '\n' +
        canonical_headers + '\n' +
        signed_headers + '\n' +
        payload_hash;

    QByteArray credential_scope =
        date_stamp + '/' + aws_region_name.toUtf8() + '/' + service + '/' + "aws4_request";
    QByteArray string_to_sign =
        algorithm + '\n' +
        amz_date + '\n' +
        credential_scope + '\n' +
        QCryptographicHash::hash(canonical_request, hashAlgorithm).toHex();

    // Create the signing key using the function defined above.
    QByteArray signing_key = getSignatureKey(aws_secret_key, date_stamp, aws_region_name, service);

    // Sign the string_to_sign using the signing_key
    QByteArray signature = QMessageAuthenticationCode::hash(string_to_sign, signing_key, hashAlgorithm).toHex();

    // Put the signature information in a header named Authorization.
    QByteArray authorization_header =
        algorithm + ' ' + "Credential=" + aws_access_key.toUtf8() + '/' +
        credential_scope + ", " +  "SignedHeaders=" + signed_headers + ", " + "Signature=" + signature;
    request.setRawHeader("Authorization", authorization_header);

    QNetworkReply *reply = network_access_manager->post(request, request_payload.toUtf8());
    connect(reply, SIGNAL(finished()), this, SLOT(getmetricstatistics_replyFinished()));

    reply->setProperty("period_local_offset_seconds", static_cast<long long>(period_local_offset_seconds));
    reply->setProperty("y_factor", y_factor);
    reply->setProperty("metric_descr", metric_descr);
    reply->setProperty("Metric_Descriptor_Index", Metric_Descriptor_Index);

    getmetricstatistics_reply_data[reply] = Graph_Metric_Statistics;

    // QEventLoop loop;
    // connect(reply, SIGNAL(finished()), &loop, SLOT(quit()));
    // loop.exec();

    return reply;
}

void
AWS_CloudWatch::getmetricstatistics_replyFinished ( ) {
    QNetworkReply *reply = qobject_cast<QNetworkReply *>(sender());

    if (not (reply->error() == 0)) {
        qDebug() << reply->errorString();
        reply->setProperty("Error_Message", reply->errorString());
        return;
    }

    QByteArray reply_data = reply->readAll();
    // qDebug() << reply_data;
    QDomDocument reply_document;
    reply_document.setContent(reply_data);
    QDomElement root = reply_document.documentElement();
    QDomNodeList datapoints_elements = root.elementsByTagName("Datapoints");
    // No Datapoints element, failed somehow
    if (not (datapoints_elements.size() == 1)) {
        reply->setProperty("Error_Message", "No Datapoints element");
        return;
    }

    QDomElement the_one_datapoints_element = datapoints_elements.at(0).toElement();
    QDomNodeList member_elements = the_one_datapoints_element.elementsByTagName("member");
    // qDebug() << member_elements.size();

    // No actual datapoints, failed somehow
    if (member_elements.size() <= 0) {
        reply->setProperty("Error_Message", "No Datapoints element members, no actual datapoints");
        return;
    }

    // long period_local_offset_seconds = reply->property("period_local_offset_seconds").toInt();
    double y_factor = reply->property("y_factor").toDouble();
    QJsonObject metric_descr = reply->property("metric_descr").toJsonObject();
    int Metric_Descriptor_Index = reply->property("Metric_Descriptor_Index").toInt();

    QDomElement datapoint_element = member_elements.at(0).toElement();
    bool request_average = (datapoint_element.elementsByTagName("Average").size() > 0);
    bool request_maximum = (datapoint_element.elementsByTagName("Maximum").size() > 0);
    bool request_minimum = (datapoint_element.elementsByTagName("Minimum").size() > 0);
    bool request_samplecount = (datapoint_element.elementsByTagName("SampleCount").size() > 0);
    bool request_sum = (datapoint_element.elementsByTagName("Sum").size() > 0);

    int metric_datapoints_count = static_cast<int>(member_elements.size());
    // Adaptive to enum: Average, Minimum, Maximum, SampleCount, Sum ...
    QVector<double> *datapoint_datetime_list = new QVector<double>(metric_datapoints_count);
    QVector<double> *datapoint_average_value_list = nullptr;
    QVector<double> *datapoint_maximum_value_list = nullptr;
    QVector<double> *datapoint_minimum_value_list = nullptr;
    QVector<double> *datapoint_samplecount_value_list = nullptr;
    QVector<double> *datapoint_sum_value_list = nullptr;
    if (request_average)
        datapoint_average_value_list = new QVector<double>(metric_datapoints_count);
    if (request_maximum)
        datapoint_maximum_value_list = new QVector<double>(metric_datapoints_count);
    if (request_minimum)
        datapoint_minimum_value_list = new QVector<double>(metric_datapoints_count);
    if (request_samplecount)
        datapoint_samplecount_value_list = new QVector<double>(metric_datapoints_count);
    if (request_sum)
        datapoint_sum_value_list = new QVector<double>(metric_datapoints_count);
    // ... Adaptive to enum: Average, Minimum, Maximum, SampleCount, Sum
    for (int datapoint_idx = 0; datapoint_idx < metric_datapoints_count; datapoint_idx++) {
        QDomElement datapoint_element = member_elements.at(datapoint_idx).toElement();
        // qDebug() << datapoint_element.text();
        // There had better be a timestamp
        QString node_value = datapoint_element.elementsByTagName("Timestamp").at(0).toElement().text();
        // qDebug() << node_value;
        // These appear to be returned/treated as local time
        (*datapoint_datetime_list)[datapoint_idx] =
            QDateTime::fromString(node_value, Qt::ISODate).toSecsSinceEpoch(); // - period_local_offset_seconds;
        if (request_average) {
            QString node_value = datapoint_element.elementsByTagName("Average").at(0).toElement().text();
            (*datapoint_average_value_list)[datapoint_idx] = y_factor * node_value.toDouble();
        }
        if (request_maximum) {
            QString node_value = datapoint_element.elementsByTagName("Maximum").at(0).toElement().text();
            (*datapoint_maximum_value_list)[datapoint_idx] = y_factor * node_value.toDouble();
        }
        if (request_minimum) {
            QString node_value = datapoint_element.elementsByTagName("Minimum").at(0).toElement().text();
            (*datapoint_minimum_value_list)[datapoint_idx] = y_factor * node_value.toDouble();
        }
        if (request_samplecount) {
            QString node_value = datapoint_element.elementsByTagName("SampleCount").at(0).toElement().text();
            (*datapoint_samplecount_value_list)[datapoint_idx] = y_factor * node_value.toDouble();
        }
        if (request_sum) {
            QString node_value = datapoint_element.elementsByTagName("Sum").at(0).toElement().text();
            (*datapoint_sum_value_list)[datapoint_idx] = y_factor * node_value.toDouble();
        }

        // qDebug() << QDateTime::fromSecsSinceEpoch((*datapoint_datetime_list)[datapoint_idx])
        //          << (*datapoint_average_value_list)[datapoint_idx]
        //          << (*datapoint_maximum_value_list)[datapoint_idx];

    }

    Metric_Statistics_Descriptor metric_statistics;
    metric_statistics.Metric_Descriptor = metric_descr;

    metric_statistics.Datapoints_DateTime_List = datapoint_datetime_list;
    // Adaptive to enum: Average, Maximum, Minimum, SampleCount, Sum ...
    metric_statistics.Datapoints_Average_List = datapoint_average_value_list;
    metric_statistics.Datapoints_Maximum_List = datapoint_maximum_value_list;
    metric_statistics.Datapoints_Minimum_List = datapoint_minimum_value_list;
    metric_statistics.Datapoints_SampleCount_List = datapoint_samplecount_value_list;
    metric_statistics.Datapoints_Sum_List = datapoint_sum_value_list;
    // ... Adaptive to enum: Average, Minimum, Maximum, SampleCount, Sum

    QVector<Metric_Statistics_Descriptor> *Graph_Metric_Statistics = getmetricstatistics_reply_data[reply];
    Graph_Metric_Statistics->replace(Metric_Descriptor_Index, metric_statistics);
    getmetricstatistics_reply_data.remove(reply);
    reply->setProperty("Error_Message", "");
}


QVector<Metric_Statistics_Descriptor>
AWS_CloudWatch::AWS_CloudWatch_GetGraphMetricStatistics ( QJsonArray Graph_Metric_Descriptor_List,
                                                          int Graph_Metric_Descriptor_Index,
                                                          QDateTime Period_End_UTC, int Period_Duration_Hours ) {
    bool graph_success = true;
    QJsonArray graph_metric_descriptor = Graph_Metric_Descriptor_List[Graph_Metric_Descriptor_Index].toArray();
    QVector<Metric_Statistics_Descriptor> graph_metrics_statistics_list(graph_metric_descriptor.size());

    QVector<QNetworkReply*> reply_list;

    QJsonArray graph_metric_descriptor_list =
        Graph_Metric_Descriptor_List[Graph_Metric_Descriptor_Index].toArray();
    for (int metric_idx = 0; metric_idx < graph_metric_descriptor.size(); metric_idx++) {
//        QFuture<bool> future = QtConcurrent::run(Get_Metric_Statistics,
//                                                 graph_metric_descriptor_list, metric_idx,
//                                                 Period_End_UTC, Period_Duration_Hours,
//                                                 &graph_metrics_statistics_list);
//        future_list.append(future);
//        for (int idx = 0; idx < future_list.size(); idx++) {
//            QFuture<bool> future = future_list[idx];
//            future.waitForFinished();
//            if (not future.result()) graph_success = false;
//        }
        QNetworkReply *reply =
            AWS_CloudWatch_GetMetricStatistics(graph_metric_descriptor, metric_idx,
                                               Period_End_UTC, Period_Duration_Hours,
                                               &graph_metrics_statistics_list);
        reply_list.append(reply);
    }

    // Wait for everything to finish
    for (int idx = 0; idx < reply_list.size(); idx++) {
        QNetworkReply *reply = reply_list[idx];
        while (reply->isRunning()) qApp->processEvents();
        QVariant error_message_variant = reply->property("Error_Message");
        if (error_message_variant.isValid()) {
            if (not (error_message_variant.toString().size() == 0)) {
                qDebug() << error_message_variant.toString();
                getmetricstatistics_reply_data.remove(reply);
                graph_success = false;
            }
        }
    }

    for (int idx = 0; idx < reply_list.size(); idx++) {
        QNetworkReply *reply = reply_list[idx];
        while (not reply->isFinished()) qApp->processEvents();
        QVariant error_message_variant = reply->property("Error_Message");
        if (error_message_variant.isValid()) {
            if (error_message_variant.toString().size() > 0) {
                qDebug() << error_message_variant.toString();
                getmetricstatistics_reply_data.remove(reply);
                graph_success = false;
            }
        }
    }

    getmetricstatistics_reply_data.clear();

    if (graph_success) return graph_metrics_statistics_list;
    else return QVector<Metric_Statistics_Descriptor>(0);
}



QVector<QVector<Metric_Statistics_Descriptor>>
AWS_CloudWatch::AWS_CloudWatch_GetPageMetricStatistics ( QJsonArray Graph_Metric_Descriptor_List,
                                                         QVector<int> Graph_Metric_Index_List,
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

    QVector<QNetworkReply*> reply_list;

    if (Graph_Metric_Index_List.count() > 0) {
        int graph_metric_index = Graph_Metric_Index_List[0];
        QJsonArray first_graph_metric_descriptor =
            Graph_Metric_Descriptor_List[graph_metric_index].toArray();
        for (int metric_idx = 0; metric_idx < first_graph_metric_descriptor.size(); metric_idx++) {
            QNetworkReply *reply =
                AWS_CloudWatch_GetMetricStatistics(first_graph_metric_descriptor, metric_idx,
                                                   Period_End_UTC, Period_Duration_Hours,
                                                   &first_graph_metric_statistics_list);
            reply_list.append(reply);
        }
    }
    if (Graph_Metric_Index_List.count() > 1) {
        int graph_metric_index = Graph_Metric_Index_List[1];
        QJsonArray second_graph_metric_descriptor =
            Graph_Metric_Descriptor_List[graph_metric_index].toArray();
        for (int metric_idx = 0; metric_idx < second_graph_metric_descriptor.size(); metric_idx++) {
            QNetworkReply *reply =
                AWS_CloudWatch_GetMetricStatistics(second_graph_metric_descriptor, metric_idx,
                                                   Period_End_UTC, Period_Duration_Hours,
                                                   &second_graph_metric_statistics_list);
            reply_list.append(reply);
        }
    }

    // Wait for everything to finish
    for (int idx = 0; idx < reply_list.size(); idx++) {
        QNetworkReply *reply = reply_list[idx];
        while (reply->isRunning()) qApp->processEvents();
        QVariant error_message_variant = reply->property("Error_Message");
        if (error_message_variant.isValid()) {
            if (not (error_message_variant.toString().size() == 0)) {
                qDebug() << error_message_variant.toString();
                getmetricstatistics_reply_data.remove(reply);
                page_success = false;
            }
        }
        // future.waitForFinished();
        // if (not future.result()) page_success = false;
    }

    for (int idx = 0; idx < reply_list.size(); idx++) {
        QNetworkReply *reply = reply_list[idx];
        while (not reply->isFinished()) qApp->processEvents();
        QVariant error_message_variant = reply->property("Error_Message");
        if (error_message_variant.isValid()) {
            if (error_message_variant.toString().size() > 0) {
                qDebug() << error_message_variant.toString();
                getmetricstatistics_reply_data.remove(reply);
                page_success = false;
            }
        }
        // future.waitForFinished();
        // if (not future.result()) page_success = false;
    }

    getmetricstatistics_reply_data.clear();

    if (not page_success) return QVector<QVector<Metric_Statistics_Descriptor>>(0);

    QVector<QVector<Metric_Statistics_Descriptor>> page_graph_metric_statistics_list;
    if (Graph_Metric_Index_List.count() > 0)
        page_graph_metric_statistics_list.append(first_graph_metric_statistics_list);
    if (Graph_Metric_Index_List.count() > 1)
        page_graph_metric_statistics_list.append(second_graph_metric_statistics_list);

    return page_graph_metric_statistics_list;
}


QNetworkReply*
AWS_CloudWatch::AWS_CloudWatch_DescribeAlarmHistory ( QString Alarm_Name,
                                                      QDateTime Period_Begin_UTC, QDateTime Period_End_UTC,
                                                      QMap<QString, QList<QMap<QString, QString>>> *Alarm_History_Results ) {

// "StartDate=2019-04-25T11%3A33%3A05.152164Z&EndDate=2019-04-26T11%3A33%3A05.152164Z&AlarmName=DBA+Lag+Replica+CPU+Alarm&MaxRecords=100&Version=2010-08-01&Action=DescribeAlarmHistory&HistoryItemType=StateUpdate&NextToken="
    QString payload = QString("Action=DescribeAlarmHistory") + QString("&") + QString("Version=2010-08-01");
    // request.SetAlarmName(Alarm_Name.toStdString());
    payload +=  QString("&") + QString("AlarmName") + QString("=") + QUrl::toPercentEncoding(Alarm_Name);

    // request.SetHistoryItemType(HistoryItemType::StateUpdate);
    payload +=  QString("&") + QString("HistoryItemType=StateUpdate");

    // request.SetMaxRecords(100);
    payload +=  QString("&") + QString("MaxRecords") + QString("=") + QString::number(100);

    // request.SetStartTime(Period_Begin_UTC.toMSecsSinceEpoch());
    payload +=  QString("&") + QString("StartDate") + QString("=") +
                QUrl::toPercentEncoding(Period_Begin_UTC.toString(Qt::ISODate));

    // request.SetEndTime(Period_End_UTC.toMSecsSinceEpoch());
    payload +=  QString("&") + QString("EndDate") + QString("=") +
                QUrl::toPercentEncoding(Period_End_UTC.toString(Qt::ISODate));

    payload +=  QString("&") + QString("NextToken=");

    QString request_payload = payload;

    // amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    QByteArray amz_date = QDateTime::currentDateTimeUtc().toString(AWS_DateTimeFormat).toUtf8();
    QByteArray amz_target = "GraniteServiceVersion20100801.DescribeAlarmHistory";
    // date_stamp = t.strftime('%Y%m%d') # Date w/o time, used in credential scope
    QByteArray date_stamp = QDateTime::currentDateTimeUtc().toString(AWS_DateFormat).toUtf8();

    QUrl endpoint_url = QUrl(aws_cw_endpoint);
    QNetworkRequest request(endpoint_url);
    request.setRawHeader("Content-Type", content_type);
    request.setRawHeader("X-Amz-Target", amz_target);
    request.setRawHeader("X-Amz-Date", amz_date);

    QByteArray canonical_uri = "/";
    QByteArray canonical_querystring = "";

    QByteArray canonical_headers =
        "content-type:" + content_type + '\n' +
        "host:" + aws_cw_host + '\n' +
        "x-amz-date:" + amz_date + '\n' +
        "x-amz-target:" + amz_target + '\n';

    QByteArray payload_hash = QCryptographicHash::hash(request_payload.toUtf8(), hashAlgorithm).toHex();

    QByteArray canonical_request =
        method + '\n' +
        canonical_uri + '\n' +
        canonical_querystring + '\n' +
        canonical_headers + '\n' +
        signed_headers + '\n' +
        payload_hash;

    QByteArray credential_scope =
        date_stamp + '/' + aws_region_name.toUtf8() + '/' + service + '/' + "aws4_request";
    QByteArray string_to_sign =
        algorithm + '\n' +
        amz_date + '\n' +
        credential_scope + '\n' +
        QCryptographicHash::hash(canonical_request, hashAlgorithm).toHex();

    // Create the signing key using the function defined above.
    QByteArray signing_key = getSignatureKey(aws_secret_key, date_stamp, aws_region_name, service);

    // Sign the string_to_sign using the signing_key
    QByteArray signature = QMessageAuthenticationCode::hash(string_to_sign, signing_key, hashAlgorithm).toHex();

    // Put the signature information in a header named Authorization.
    QByteArray authorization_header =
        algorithm + ' ' + "Credential=" + aws_access_key.toUtf8() + '/' +
        credential_scope + ", " +  "SignedHeaders=" + signed_headers + ", " + "Signature=" + signature;
    request.setRawHeader("Authorization", authorization_header);

    QNetworkReply *reply = network_access_manager->post(request, request_payload.toUtf8());
    connect(reply, SIGNAL(finished()), this, SLOT(describealarmhistory_replyFinished()));

    reply->setProperty("Alarm_Name", Alarm_Name);
    describealarmhistory_reply_data[reply] = Alarm_History_Results;

    return reply;
}

void
AWS_CloudWatch::describealarmhistory_replyFinished ( ) {
    QNetworkReply *reply = qobject_cast<QNetworkReply *>(sender());

    if (not (reply->error() == 0)) {
        qDebug() << reply->errorString();
        reply->setProperty("Error_Message", reply->errorString());
        return;
    }

    QByteArray reply_data = reply->readAll();
    // qDebug() << reply_data;
    QDomDocument reply_document;
    reply_document.setContent(reply_data);
    QDomElement root = reply_document.documentElement();
    QDomNodeList alarmhistoryitems_elements = root.elementsByTagName("AlarmHistoryItems");
    // No AlarmHistoryItems element, failed somehow
    if (not (alarmhistoryitems_elements.size() == 1)) {
        reply->setProperty("Error_Message", "No AlarmHistoryItems element");
        return;
    }

    QDomElement the_one_alarmhistoryitems_element = alarmhistoryitems_elements.at(0).toElement();
    QDomNodeList member_elements = the_one_alarmhistoryitems_element.elementsByTagName("member");
    // qDebug() << member_elements.size();

    // No actual AlarmHistoryItems, this could be OK, almost certainly OK
    if (member_elements.size() <= 0) {
        // reply->setProperty("Error_Message", "No AlarmHistoryItems element members, no actual items");
        reply->setProperty("Error_Message", "");
        return;
    }

    QList<QMap<QString, QString>> alarm_history;

    int history_items_count = static_cast<int>(member_elements.size());
    for (int item_idx = 0; item_idx < history_items_count; item_idx++) {
        QDomElement history_item_element = member_elements.at(item_idx).toElement();

        QString alarm_name_value = history_item_element.elementsByTagName("AlarmName").at(0).toElement().text();
        QString history_data_value = history_item_element.elementsByTagName("HistoryData").at(0).toElement().text();
        QString history_summary_value = history_item_element.elementsByTagName("HistorySummary").at(0).toElement().text();
        QString history_timestamp_value = history_item_element.elementsByTagName("Timestamp").at(0).toElement().text();

        // qDebug() << "alarm_name_value:" << alarm_name_value;
        // qDebug() << "history_data_value:" << history_data_value;
        // qDebug() << "history_summary_value:" << history_summary_value;
        // qDebug() << "history_timestamp_value:" << history_timestamp_value;

        QMap<QString, QString> alarm_history_item;

        QDateTime history_item_datetime_utc = QDateTime::fromString(history_timestamp_value, Qt::ISODate);
        alarm_history_item["AlarmDateTime"] = history_item_datetime_utc.toLocalTime().toString(Qt::ISODate);
        // qDebug() << "AlarmDateTime:" << alarm_history_item["AlarmDateTime"];
        alarm_history_item["AlarmName"] = alarm_name_value;
        alarm_history_item["AlarmSummary"] = history_summary_value;
        alarm_history_item["AlarmData"] = history_data_value;

        alarm_history.append(alarm_history_item);
    }

    if (alarm_history.size() > 0) {
        QString Alarm_Name = reply->property("Alarm_Name").toString();
        QMap<QString, QList<QMap<QString, QString>>> *Alarm_History_Results = describealarmhistory_reply_data[reply];
        (*Alarm_History_Results)[Alarm_Name] = alarm_history;
    }

    describealarmhistory_reply_data.remove(reply);
    reply->setProperty("Error_Message", "");
}

QMap<QString, QList<QMap<QString, QString>>>
AWS_CloudWatch::AWS_CloudWatch_AlarmHistory ( QJsonArray Alarm_Name_List,
                                              QDateTime Period_Begin_UTC, QDateTime Period_End_UTC ) {
    QMap<QString, QList<QMap<QString, QString>>> alarm_history_results;
    if (Alarm_Name_List.count() == 0) return alarm_history_results;

    bool alarm_success = true;

    QVector<QNetworkReply*> reply_list;

    for (int idx = 0; idx < Alarm_Name_List.count(); idx++) {
        QString alarm_name = Alarm_Name_List[idx].toString();
        QNetworkReply* reply =
            AWS_CloudWatch_DescribeAlarmHistory
                (alarm_name, Period_Begin_UTC, Period_End_UTC, &alarm_history_results);
        reply_list.append(reply);
    }

    // Wait for everything to finish
    for (int idx = 0; idx < reply_list.size(); idx++) {
        QNetworkReply *reply = reply_list[idx];
        while (reply->isRunning()) qApp->processEvents();
        QVariant error_message_variant = reply->property("Error_Message");
        if (error_message_variant.isValid()) {
            if (not (error_message_variant.toString().size() == 0)) {
                qDebug() << error_message_variant.toString();
                describealarmhistory_reply_data.remove(reply);
                alarm_success = false;
            }
        }
    }

    for (int idx = 0; idx < reply_list.size(); idx++) {
        QNetworkReply *reply = reply_list[idx];
        while (not reply->isFinished()) qApp->processEvents();
        QVariant error_message_variant = reply->property("Error_Message");
        if (error_message_variant.isValid()) {
            if (error_message_variant.toString().size() > 0) {
                qDebug() << error_message_variant.toString();
                describealarmhistory_reply_data.remove(reply);
                alarm_success = false;
            }
        }
    }

    describealarmhistory_reply_data.clear();

    if (not alarm_success) alarm_history_results.clear();

    return alarm_history_results;
}

