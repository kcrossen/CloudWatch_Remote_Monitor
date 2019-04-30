#ifndef CW_REMOTE_H
#define CW_REMOTE_H

#include <QtCore/QDebug>

#include <QMainWindow>
#include <QtCore>
#include <QtGui>
#include <QMainWindow>
#include <QtWidgets>

#include <QToolTip>

#include <QVBoxLayout>
#include <QLabel>

#include <QList>
#include <QMap>

#include <QtGlobal>
#include <QtMath>

#include <algorithm>

#include "CustomPlot.h"
#include "ControlBar.h"
#include "AlarmReport.h"
#include "CloudWatch.h"

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
    // int upper_chartview_height;
    // int lower_chartview_height;
    int upper_customplot_height;
    int lower_customplot_height;

    // ChartView *Upper_Chartview;
    CustomPlot *Upper_CustomPlot;
    ControlBar *Control_Bar;
    // ChartView *Lower_Chartview;
    CustomPlot *Lower_CustomPlot;

    AlarmReport *Alarm_Report;
    QDateTime previous_alarm_report_datatime;
    bool alarms_acknowledged;

    QTimer *timer;

protected:
    void
    showEvent ( QShowEvent*  event );

    void
    hideEvent ( QHideEvent*  event );

public slots:
    void
    timer_update_page_metrics (  );

    void
    refresh_button_update_page_metrics (  );

    void
    update_alarms (  );

    void
    update_alarm_history ( bool Force_Alarm_History_Display );

    void
    display_alarms ( QString Alarm_History_Text );

    void
    alarm_report_acknowledged ( );

    void
    alarm_report_dismissed ( );

    void
    update_page_metrics (  );

    void
    previous_page_metrics (  );

    void
    next_page_metrics (  );

    void
    duplex_metrics (  );

    void
    simplex_metrics ( bool Force_Simplex = false );

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
    void
    closeEvent ( QCloseEvent* /*event*/ );

    // void
    // showEvent ( QShowEvent* /* event */ );

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
