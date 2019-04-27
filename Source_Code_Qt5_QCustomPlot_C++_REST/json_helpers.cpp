#include "json_helpers.h"

QString
get_json_string_value ( QJsonObject Json_Obj,
                        QString Value_Name, QString Value_Default ) {
    QString value = Value_Default;
    if (Json_Obj.contains(Value_Name) and Json_Obj[Value_Name].isString())
        value = Json_Obj[Value_Name].toString();
    return value;
}
