#include <QApplication>

// Keep track of already received alarms and individual alarm states.
// Alarms vs warnings
// Support two graph lines from same data fetch.
// {@@@@@}

// Done:
// X axis ticks/labels optimize
// Automatic adaptive alarms
// Click to expand only datetime axis


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

// In Qt Creator, from the "Build" menu:
//     "Run qmake",
//     "Clean Project 'CW_Remote'",
//     "Rebuild Project 'CW_Remote'",
//     "Clean Project 'CW_Remote'"
//$ cd <release build directory>
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
** Copyright (C) 2019 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** $QT_BEGIN_LICENSE:BSD$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** BSD License Usage
** Alternatively, you may use this file under the terms of the BSD license
** as follows:
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
// #include "CW_Remote_Ini_Do_Not_Publish.h"

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
AWS_CloudWatch *cloudwatch = nullptr;

static
QVector<Metric_Statistics_Descriptor> Upper_Graph_Metric_Statistics;

static
QVector<Metric_Statistics_Descriptor> Lower_Graph_Metric_Statistics;

int main ( int argc, char* argv[] ) {

    QApplication Application(argc, argv);
    // qDebug() << qVersion();

    // Read json ini file
    QString cw_remote_ini_json;
    // QFile cw_remote_ini_file;
    // cw_remote_ini_file.setFileName("~/Documents/CW_Remote/CW_Remote.ini");
    QString cw_remote_ini_filename = QCoreApplication::applicationDirPath();
    cw_remote_ini_filename.truncate(cw_remote_ini_filename.indexOf("CW_Remote.app"));
    cw_remote_ini_filename += "CW_Remote.ini";
    // qDebug() << cw_remote__ini_filename;
    if (not QFileInfo(cw_remote_ini_filename).exists()) {
        cw_remote_ini_filename = QDir::homePath() + "/Documents/CW_Remote/CW_Remote.ini";
        if (not QFileInfo(cw_remote_ini_filename).exists()) return 255;
    }
    QFile cw_remote_ini_file(cw_remote_ini_filename);
    cw_remote_ini_file.open(QIODevice::ReadOnly | QIODevice::Text);
    cw_remote_ini_json = cw_remote_ini_file.readAll();
    cw_remote_ini_file.close();

    // QString cw_remote_ini_json = CW_Remote_Ini_Json;
    CW_Remote_ini = QJsonDocument::fromJson(cw_remote_ini_json.toUtf8()).object();

    QString aws_access_id = get_json_string_value(CW_Remote_ini, "aws_access_id", "");
    QString aws_secret_key = get_json_string_value(CW_Remote_ini, "aws_secret_key", "");
    QString region_name = get_json_string_value(CW_Remote_ini, "region_name", "");

    cloudwatch = new AWS_CloudWatch(aws_access_id, aws_secret_key, region_name);

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

    CW_Remote MainWindow;
    MainWindow.setContentsMargins(0, 0, 0, 0);
    MainWindow.show();

    int return_code = Application.exec();

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

void
CW_Remote::closeEvent ( QCloseEvent* /*event*/ ) {
    qApp->closeAllWindows();
    qApp->exit();
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

    Control_Bar = new ControlBar(Initial_Period_Duration_Hours,
                                 Initial_Period_End_Hours_Ago,
                                 Visible_Graph_Count,
                                 this);
    connect(Control_Bar, SIGNAL(alarmsUpdate()), this, SLOT(update_alarms()));
    connect(Control_Bar, SIGNAL(metricsUpdate()), this, SLOT(refresh_button_update_page_metrics()));
    connect(Control_Bar, SIGNAL(metricsPrevious()), this, SLOT(previous_page_metrics()));
    connect(Control_Bar, SIGNAL(metricsNext()), this, SLOT(next_page_metrics()));
    connect(Control_Bar, SIGNAL(metricsDuplex()), this, SLOT(duplex_metrics()));
    connect(Control_Bar, SIGNAL(metricsSimplex()), this, SLOT(simplex_metrics()));

    QDateTime datetime_now_utc = QDateTime::currentDateTimeUtc();
    QDateTime period_end_utc = datetime_now_utc.addSecs(-(Period_End_Hours_Ago * (60 * 60)));

    if (Visible_Graph_Count == 2) {
        QVector<QVector<Metric_Statistics_Descriptor>> page_graph_metric_statistics =
            cloudwatch->AWS_CloudWatch_GetPageMetricStatistics
                (Graph_Metric_Descriptor_List,
                 QVector<int>( { (Graph_Offset + 0), (Graph_Offset + 1) } ),
                 period_end_utc, Period_Duration_Hours);

        if (page_graph_metric_statistics.size() == 2) {
            QVector<Metric_Statistics_Descriptor> upper_graph_metric_statistics = page_graph_metric_statistics[0];
            QVector<Metric_Statistics_Descriptor> lower_graph_metric_statistics = page_graph_metric_statistics[1];

            Upper_CustomPlot = new CustomPlot(upper_graph_metric_statistics, this);
            Lower_CustomPlot = new CustomPlot(lower_graph_metric_statistics, this);
        }
    }
    else if (Visible_Graph_Count == 1) {
        QVector<Metric_Statistics_Descriptor> lower_graph_metric_statistics =
            cloudwatch->AWS_CloudWatch_GetGraphMetricStatistics
                (Graph_Metric_Descriptor_List, (Graph_Offset + 0),
                 period_end_utc, Period_Duration_Hours);

        if (lower_graph_metric_statistics.size() >= 1) {
            // Must initialize both graph widgets potentially on page, ...
            // ... initialize both with same dataset.
            Upper_CustomPlot = new CustomPlot(lower_graph_metric_statistics, this);
            Lower_CustomPlot = new CustomPlot(lower_graph_metric_statistics, this);
        }
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

    Alarm_Report = new AlarmReport(this);
    connect(Alarm_Report, SIGNAL(alarmReportAcknowledged()), this, SLOT(alarm_report_acknowledged()));
    connect(Alarm_Report, SIGNAL(alarmReportDismissed()), this, SLOT(alarm_report_dismissed()));
    Alarm_Report->setVisible(false);
    alarms_acknowledged = false;

    setAttribute(Qt::WA_AlwaysShowToolTips);
    setMouseTracking(true);

    timer = new QTimer(this);
    connect(timer, SIGNAL(timeout()), this, SLOT(timer_update_page_metrics()));
    // Default 60 seconds as milliseconds
    timer->start(Initial_Refresh_Interval_Seconds * 1000);

    if (Visible_Graph_Count == 1) simplex_metrics(true);
}

CW_Remote_Screen::~CW_Remote_Screen ( ) {
}

void
CW_Remote_Screen::showEvent ( QShowEvent* event ) {
    QWidget::showEvent(event);
    timer_update_page_metrics();
    timer->start(Initial_Refresh_Interval_Seconds * 1000);
    repaint();
}

void
CW_Remote_Screen::hideEvent ( QHideEvent* event ) {
    QWidget::hideEvent( event );
    // The timer will otherwise waste power and carry out useless calculations
    timer->stop();
}

void
CW_Remote_Screen::update_alarms (  ) {
    update_alarm_history(true);
}

void
CW_Remote_Screen::update_alarm_history ( bool Force_Alarm_History_Display ) {
    QDateTime datetime_now_utc = QDateTime::currentDateTimeUtc();
    QDateTime datetime_before_utc = datetime_now_utc.addSecs(-(24 * 60 * 60));

    if (alarms_acknowledged and (not Force_Alarm_History_Display))
        datetime_before_utc = previous_alarm_report_datatime;

    QMap<QString, QList<QMap<QString, QString>>> alarms_history =
        cloudwatch->AWS_CloudWatch_AlarmHistory
            (Alarm_Name_List, datetime_before_utc, datetime_now_utc);

    previous_alarm_report_datatime = datetime_now_utc;

    if (alarms_history.size() == 0) return;

    QList<QString> alarm_name_list = alarms_history.uniqueKeys();
    QString alarm_history_text;

    bool alarm_currently_in_alarm_state = false;

    for (int key_idx = 0; key_idx < alarm_name_list.size(); key_idx++) {
        QString alarm_name = alarm_name_list[key_idx];
        if (alarm_history_text.size() > 0) alarm_history_text += "<br/><br/>";
        QList<QMap<QString, QString>> alarm_detail_list = alarms_history.value(alarm_name);
        for (int detail_idx = 0; detail_idx < qMin(alarm_detail_list.size(), 2); detail_idx++) {
            QMap<QString, QString> alarm_detail_map = alarm_detail_list[detail_idx];
            QString alarm_datetime = alarm_detail_map["AlarmDateTime"];
            QString alarm_summary = alarm_detail_map["AlarmSummary"];

            if (detail_idx == 0) {
                if (alarm_summary == "Alarm updated from OK to ALARM") {
                    alarm_currently_in_alarm_state = true;
                    alarm_history_text += "<font color=\"Red\">" + alarm_name + "</font>:";
                }
                else alarm_history_text += alarm_name + ":";
            }

            QJsonObject alarm_data = QJsonDocument::fromJson(alarm_detail_map["AlarmData"].toUtf8()).object();
            QJsonObject alarm_data_new_state = alarm_data["newState"].toObject();
            QString alarm_data_new_state_reason = alarm_data_new_state["stateReason"].toString();
            int ch_idx = 0;
            ch_idx = alarm_data_new_state_reason.indexOf("[");
            alarm_data_new_state_reason.remove(0, (ch_idx + 1));
            ch_idx = alarm_data_new_state_reason.indexOf(".");
            int ch_end_idx = alarm_data_new_state_reason.indexOf("]");
            alarm_data_new_state_reason.remove((ch_idx + 2), (ch_end_idx - (ch_idx + 1)));
            alarm_data_new_state_reason.replace(" was not greater than the threshold (", " LT ");
            alarm_data_new_state_reason.replace(" was greater than the threshold (", " GT ");
            alarm_data_new_state_reason.replace(").", "");
            // qDebug() << alarm_data_new_state_reason;
             if (alarm_summary == "Alarm updated from OK to ALARM") {
                if (detail_idx == 0)
                    alarm_history_text +=
                        "<br/>&nbsp;&nbsp;&nbsp;<b><font color=\"Red\">ALARM</font></b> " +
                        alarm_datetime + " (value " +
                        alarm_data_new_state_reason + " threshold)";
                else
                    alarm_history_text +=
                        "<br/>&nbsp;&nbsp;&nbsp;<b>ALARM</b> " + alarm_datetime + " (value " +
                        alarm_data_new_state_reason + " threshold)";
            }
            else if (alarm_summary == "Alarm updated from ALARM to OK")
                alarm_history_text +=
                    "<br/>&nbsp;&nbsp;&nbsp;<b>OK</b> " + alarm_datetime + " (value " +
                    alarm_data_new_state_reason + " threshold)";
            else
                alarm_history_text += "<br/>&nbsp;&nbsp;&nbsp;" + alarm_datetime + ":<br/>    " + alarm_summary;
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
    Alarm_Report->setAlarmText(Alarm_History_Text);
    Alarm_Report->setVisible(true);
    repaint();
}

void
CW_Remote_Screen::alarm_report_acknowledged ( ) {
    alarms_acknowledged = true;
    repaint();
}

void
CW_Remote_Screen::alarm_report_dismissed ( ) {
    alarms_acknowledged = false;
    repaint();
}

void
CW_Remote_Screen::timer_update_page_metrics (  ) {
    if (((Visible_Graph_Count == 2) and
         (Upper_CustomPlot->zoom_level == 0) and (Lower_CustomPlot->zoom_level == 0)) or
        ((Visible_Graph_Count == 1) and (Lower_CustomPlot->zoom_level == 0))) update_page_metrics();

    if (Automatic_Alarm_History) update_alarm_history(false);
}

void
CW_Remote_Screen::refresh_button_update_page_metrics (  ) {
    update_page_metrics();
    // Make certain the timer is running, even if it causes a restart
    timer->start(Initial_Refresh_Interval_Seconds * 1000);
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
            cloudwatch->AWS_CloudWatch_GetPageMetricStatistics
                (Graph_Metric_Descriptor_List,
                 QVector<int>( { (Graph_Offset + 0), (Graph_Offset + 1) } ),
                 period_end_utc, Period_Duration_Hours);

        if (page_graph_metric_statistics.size() == 2) {
            QVector<Metric_Statistics_Descriptor> upper_graph_metric_statistics = page_graph_metric_statistics[0];
            QVector<Metric_Statistics_Descriptor> lower_graph_metric_statistics = page_graph_metric_statistics[1];

            Upper_CustomPlot->setCustomPlotData(upper_graph_metric_statistics);
            Lower_CustomPlot->setCustomPlotData(lower_graph_metric_statistics);

        }
    }
    else if (Visible_Graph_Count == 1) {
        QVector<Metric_Statistics_Descriptor> lower_graph_metric_statistics =
            cloudwatch->AWS_CloudWatch_GetGraphMetricStatistics
                (Graph_Metric_Descriptor_List, (Graph_Offset + 0),
                 period_end_utc, Period_Duration_Hours);

        if (lower_graph_metric_statistics.size() >= 1)
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

        main_window_layout->replaceWidget(empty_label, Upper_CustomPlot, Qt::FindDirectChildrenOnly);
        Lower_CustomPlot->setMaximumHeight(lower_customplot_height);
        Upper_CustomPlot->setMaximumHeight(upper_customplot_height);

        Graph_Offset = qMax((Graph_Offset - 1), 0);
        Visible_Graph_Count = 2;
        // Transitioning from simplex, the old Upper_CustomPlot is probably stale
        update_page_metrics();
        // update();
    }
}

void
CW_Remote_Screen::simplex_metrics ( bool Force_Simplex ) {
    if ((Visible_Graph_Count == 2) or Force_Simplex) {
        int descriptor_list_length = Graph_Metric_Descriptor_List.count();
        upper_customplot_height = Upper_CustomPlot->height();
        lower_customplot_height = Lower_CustomPlot->height();

        QLayout *main_window_layout = layout();
        main_window_layout->replaceWidget(Upper_CustomPlot, empty_label, Qt::FindDirectChildrenOnly);

        Graph_Offset = qMin((Graph_Offset + 1), (descriptor_list_length - 1));
        Visible_Graph_Count = 1;
        // Transitioning from duplex, the current Lower_CustomPlot is not stale
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
