#ifndef CONTROLBAR_H
#define CONTROLBAR_H

#include <QtWidgets>

class ControlBar : public QFrame  {
    Q_OBJECT

public:
    ControlBar (int Initial_Period_Duration_Hours,
                int Initial_Period_End_Hours_AgoQWidget,
                QWidget *parent = nullptr );
    // ~ControlBar ( );

    int
    get_period_duration_hours_value ( );

    void
    set_period_duration_hours_value ( int period_duration_hours_value );

    int
    get_period_end_hours_ago_value ( );

    void
    set_period_end_hours_ago_value ( int period_end_hours_ago_value );

private:
    const QVector<int> Period_Duration_Hours_Steps = QVector<int>(
            {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24,  // 18
             26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48,  // 12
             50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72,  // 12
             74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 96,  // 12
             100, 104, 108, 112, 116, 120,  // 6
             124, 128, 132, 136, 140, 144,  // 6
             148, 152, 156, 160, 164, 168});  // 6

    const QVector<int> Period_End_Hours_Ago_Steps = QVector<int>(
            {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24,  // 19
             26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48,  // 12
             50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72,  // 12
             74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 96,  // 12
             100, 104, 108, 112, 116, 120,  // 6
             124, 128, 132, 136, 140, 144,  // 6
             148, 152, 156, 160, 164, 168});  // 6

    QToolTip *tooltip;

    int period_duration_hours;
    int period_end_hours_ago;

    double period_duration_slider_value_span;
    double period_end_slider_value_span;

    QPushButton *previous_pushbutton;
    QLabel *period_duration_hours_label;
    QSlider *period_duration_hours_slider;
    QPushButton *duplex_pushbutton;
    QPushButton *simplex_pushbutton;
    QSlider *period_end_hours_ago_slider;
    QLabel *period_end_hours_ago_label;
    QPushButton *next_pushbutton;

public slots:

signals:
    void alarmsUpdate ( );
    void metricsUpdate ( );
    void metricsPrevious ( );
    void metricsNext ( );
    void metricsDuplex ( );
    void metricsSimplex ( );

protected:
    void
    mouseMoveEvent ( QMouseEvent *event );

private:
    QString
    period_value_display ( int Period_Value );

private slots:
    void
    on_period_duration_hours_value_change ( int period_duration_slider_value );

    void
    on_period_end_hours_ago_value_change ( int period_end_slider_value );

    void
    emit_alarms_signal ( );

    void
    emit_update_signal ( );

    void
    emit_previous_signal ( );

    void
    emit_next_signal ( );

    void
    emit_duplex_signal ( );

    void
    emit_simplex_signal ( );

};

#endif // CONTROLBAR_H
