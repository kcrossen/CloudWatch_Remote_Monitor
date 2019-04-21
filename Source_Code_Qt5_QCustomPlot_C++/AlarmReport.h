#ifndef ALARMREPORT_H
#define ALARMREPORT_H

#include <QFrame>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QLabel>
#include <QPushButton>
#include <QMouseEvent>

class AlarmReport : public QFrame {
    Q_OBJECT
public:
    explicit AlarmReport ( QWidget *parent = nullptr );

    void
    setAlarmText ( QString AlarmText );

protected:
//    void
//    mousePressEvent ( QMouseEvent* event );

//    void
//    mouseMoveEvent ( QMouseEvent *event );

//    void
//    mouseReleaseEvent ( QMouseEvent *event );

private:
    QLabel *alarm_report_label;
    QFrame *button_bar;

signals:
    void alarmReportAcknowledged ( );

    void alarmReportDismissed ( );

public slots:
    void
    acknowledge_pushbutton_clicked (  );

    void
    dismiss_pushbutton_clicked (  );

};

#endif // ALARMREPORT_H
