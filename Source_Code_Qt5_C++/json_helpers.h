#ifndef JSON_HELPERS_H
#define JSON_HELPERS_H

#include <QtCore>

QString
get_json_string_value ( QJsonObject Json_Obj,
                        QString Value_Name, QString Value_Default );

#endif // JSON_HELPERS_H
