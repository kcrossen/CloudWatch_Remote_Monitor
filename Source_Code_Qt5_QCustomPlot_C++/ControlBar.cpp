#include "ControlBar.h"

static
int bound ( int low, int high, int value ) {
    return qMax(low, qMin(high, value));
}


ControlBar::ControlBar ( int Initial_Period_Duration_Hours,
                         int Initial_Period_End_Hours_Ago,
                         QWidget *parent ) : QFrame ( parent ) {
    // Values for relative-to-now begin and end of display period
    period_duration_hours = Initial_Period_Duration_Hours;
    period_end_hours_ago = Initial_Period_End_Hours_Ago;

    setMouseTracking(true);

    int slider_minimum_value = 0;

    int period_duration_slider_maximum_value = 999;
    period_duration_slider_value_span = period_duration_slider_maximum_value - slider_minimum_value;

    int period_end_slider_maximum_value = 1000;
    period_end_slider_value_span = period_end_slider_maximum_value - slider_minimum_value;

    setContentsMargins(0, 0, 0, 0);
    setFrameShape(QFrame::StyledPanel);
    setAutoFillBackground(true);
    setLineWidth(0);
    setMaximumHeight(32);
    // setFrameStyle(QFrame::Plain);

    QHBoxLayout *control_bar_layout = new QHBoxLayout();
    control_bar_layout->setMargin(0);
    control_bar_layout->setContentsMargins(0, 0, 0, 0);
    control_bar_layout->setSpacing(2);
    control_bar_layout->setAlignment(Qt::AlignCenter);

    previous_pushbutton = new QPushButton("⬆", parent=this);
    previous_pushbutton->setFixedWidth(64);
    connect(previous_pushbutton, SIGNAL(clicked()), this, SLOT(emit_previous_signal()));
    previous_pushbutton->setMouseTracking(true);
    control_bar_layout->addWidget(previous_pushbutton);

    period_duration_hours_label = new QLabel("24H", parent=this);
    period_duration_hours_label->setFixedWidth(80);
    period_duration_hours_label->setAlignment(Qt::AlignCenter);
    control_bar_layout->addWidget(period_duration_hours_label);

    period_duration_hours_slider = new QSlider(Qt::Horizontal, parent=this);
    period_duration_hours_slider->setMinimumWidth(360); // 5 pixels per step, 72 steps
    period_duration_hours_slider->setMinimum(slider_minimum_value);
    period_duration_hours_slider->setMaximum(period_duration_slider_maximum_value);
    period_duration_hours_slider->setValue(slider_minimum_value);
    connect(period_duration_hours_slider, SIGNAL(valueChanged(int)),
            this, SLOT(on_period_duration_hours_value_change(int)));
    connect(period_duration_hours_slider, SIGNAL(sliderReleased()), this, SLOT(emit_update_signal()));
    period_duration_hours_slider->setMouseTracking(true);
    control_bar_layout->addWidget(period_duration_hours_slider);

    // min = slider_minimum_value, max = period_duration_slider_maximum_value,
    // value = period_duration_slider_maximum_value, step = 1, size_hint = (0.4, 1))

    duplex_pushbutton = new QPushButton("2", parent=this);
    connect(duplex_pushbutton, SIGNAL(clicked()), this, SLOT(emit_duplex_signal()));
    duplex_pushbutton->setFixedWidth(32);
    duplex_pushbutton->setDown(true);
    duplex_pushbutton->setMouseTracking(true);
    control_bar_layout->addWidget(duplex_pushbutton);

    QPushButton *alarms_pushbutton = new QPushButton("Alarms", parent=this);
    connect(alarms_pushbutton, SIGNAL(clicked()), this, SLOT(emit_alarms_signal()));
    alarms_pushbutton->setFixedWidth(80);
    control_bar_layout->addWidget(alarms_pushbutton);

    QPushButton *refresh_pushbutton = new QPushButton("Refresh", parent=this);
    connect(refresh_pushbutton, SIGNAL(clicked()), this, SLOT(emit_update_signal()));
    refresh_pushbutton->setFixedWidth(80);
    control_bar_layout->addWidget(refresh_pushbutton);

    simplex_pushbutton = new QPushButton("1", parent=this);
    connect(simplex_pushbutton, SIGNAL(clicked()), this, SLOT(emit_simplex_signal()));
    simplex_pushbutton->setFixedWidth(32);
    simplex_pushbutton->setMouseTracking(true);
    control_bar_layout->addWidget(simplex_pushbutton);

    period_end_hours_ago_slider = new QSlider(Qt::Horizontal, parent=this);
    period_end_hours_ago_slider->setMinimumWidth(360); // 5 pixels per step, 72 steps
    period_end_hours_ago_slider->setMinimum(slider_minimum_value);
    period_end_hours_ago_slider->setMaximum(period_end_slider_maximum_value);
    period_end_hours_ago_slider->setValue(period_end_slider_maximum_value);
    connect(period_end_hours_ago_slider, SIGNAL(valueChanged(int)),
            this, SLOT(on_period_end_hours_ago_value_change(int)));
    connect(period_end_hours_ago_slider, SIGNAL(sliderReleased()), this, SLOT(emit_update_signal()));
    period_end_hours_ago_slider->setMouseTracking(true);
    control_bar_layout->addWidget(period_end_hours_ago_slider);

    // min = slider_minimum_value, max = period_end_slider_maximum_value,
    // value = period_end_slider_maximum_value, step = 1, size_hint = (0.4, 1))

    period_end_hours_ago_label = new QLabel("0H ago", parent=this);
    period_end_hours_ago_label->setFixedWidth(80);
    period_end_hours_ago_label->setAlignment(Qt::AlignCenter);
    control_bar_layout->addWidget(period_end_hours_ago_label);

    next_pushbutton = new QPushButton("⬇", parent=this);
    next_pushbutton->setFixedWidth(64);
    connect(next_pushbutton, SIGNAL(clicked()), this, SLOT(emit_next_signal()));
    next_pushbutton->setMouseTracking(true);
    control_bar_layout->addWidget(next_pushbutton);

    setLayout(control_bar_layout);

    set_period_duration_hours_value(period_duration_hours);
    set_period_end_hours_ago_value(period_end_hours_ago);
}

// Public functions (used to synchronize multiple TimeSpanControlBars) ...
int
ControlBar::get_period_duration_hours_value ( ) {
    return period_duration_hours;
}

void
ControlBar::set_period_duration_hours_value ( int period_duration_hours_value) {
    period_duration_hours = period_duration_hours_value;
    period_duration_hours_label->setText(period_value_display(period_duration_hours));
//    double slider_value_a = Period_Duration_Hours_Steps.indexOf(period_duration_hours);
//    double slider_value_b = period_duration_slider_value_span *
//                             Period_Duration_Hours_Steps.indexOf(period_duration_hours);
//    double slider_value_c = (period_duration_slider_value_span *
//            Period_Duration_Hours_Steps.indexOf(period_duration_hours)) /
//             Period_Duration_Hours_Steps.count();
    period_duration_hours_slider->setValue
        (1000 - int(round((period_duration_slider_value_span *
                           Period_Duration_Hours_Steps.indexOf(period_duration_hours)) /
                          Period_Duration_Hours_Steps.count())));
}

int
ControlBar::get_period_end_hours_ago_value ( ) {
    return period_end_hours_ago;
}

void
ControlBar::set_period_end_hours_ago_value ( int period_end_hours_ago_value ) {
    period_end_hours_ago = period_end_hours_ago_value;
    period_end_hours_ago_slider->setValue
        (1000 - int(round((period_end_slider_value_span *
                           Period_End_Hours_Ago_Steps.indexOf(period_end_hours_ago)) /
                          Period_End_Hours_Ago_Steps.count())));
    period_end_hours_ago_label->setText(period_value_display(period_end_hours_ago) + " ago");
}
// ... Public functions  (used to synchronize multiple TimeSpanControlBars)

// Private functions ...
QString
ControlBar::period_value_display ( int Period_Value ) {
    QString period_value_string = "";
    if (Period_Value >= 24)
        period_value_string += QString::number(qFloor(Period_Value / 24)) + "D";
    if (((Period_Value % 24) > 0) or (period_value_string.count() == 0)) {
        if (period_value_string.count() > 0) period_value_string += " ";
        period_value_string += QString::number(Period_Value % 24) + "H";
    }
    return period_value_string;
}

void
ControlBar::on_period_duration_hours_value_change ( int period_duration_slider_value ) {
    // print (period_duration_slider_value)
    int period_value_index =
        int(round((Period_Duration_Hours_Steps.count() *
                   abs(period_duration_slider_value - 1000)) / period_duration_slider_value_span));
    period_duration_hours =
        Period_Duration_Hours_Steps[bound(0, (Period_Duration_Hours_Steps.count() - 1), period_value_index)];
    period_duration_hours_label->setText(period_value_display(period_duration_hours));
    // print (period_duration_slider_value, period_value_index, period_duration_hours, period_duration_label.text)
    // return True
}

void
ControlBar::on_period_end_hours_ago_value_change ( int period_end_slider_value ) {
    int period_end_value_index =
        int(round((Period_End_Hours_Ago_Steps.count() *
                   abs(period_end_slider_value - 1000)) / period_end_slider_value_span));
    period_end_hours_ago =
        Period_End_Hours_Ago_Steps[bound(0, (Period_End_Hours_Ago_Steps.count() -1), period_end_value_index)];
    period_end_hours_ago_label->setText(period_value_display(period_end_hours_ago) + " ago");
    // return True
}

void
ControlBar::emit_alarms_signal ( ) {
    emit alarmsUpdate();
}

void
ControlBar::emit_update_signal ( ) {
    emit metricsUpdate();
}

void
ControlBar::emit_previous_signal ( ) {
    emit metricsPrevious();
}

void
ControlBar::emit_next_signal ( ) {
    emit metricsNext();
}

void
ControlBar::emit_duplex_signal ( ) {
    if (not duplex_pushbutton->isDown()) {
        duplex_pushbutton->setDown(true);
        simplex_pushbutton->setDown(false);
    }
    emit metricsDuplex();
}

void
ControlBar::emit_simplex_signal ( ) {
    if (not simplex_pushbutton->isDown()) {
        duplex_pushbutton->setDown(false);
        simplex_pushbutton->setDown(true);
    }
    emit metricsSimplex();
}

void
ControlBar::mouseMoveEvent ( QMouseEvent *event ) {
    if (rect().contains(event->pos())) {
        QPoint control_bar_pos = pos();

        QPoint tooltip_pos = event->pos();
        tooltip_pos.setX(control_bar_pos.x() + tooltip_pos.x());
        tooltip_pos.setY(control_bar_pos.y() + tooltip_pos.y() + 100);

        // qDebug() << "previous_pushbutton" << previous_pushbutton->geometry().width();
        // qDebug() << "period_duration_hours_slider" << period_duration_hours_slider->geometry().width();
        // qDebug() << "duplex_pushbutton" << duplex_pushbutton->geometry().width();
        // qDebug() << "simplex_pushbutton" << simplex_pushbutton->geometry().width();
        // qDebug() << "period_end_hours_ago_slider" << period_end_hours_ago_slider->geometry().width();
        // qDebug() << "next_pushbutton" << next_pushbutton->geometry().width();

        if (previous_pushbutton->geometry().contains(event->pos()))
            QToolTip::showText(tooltip_pos, "Previous graph page");
        else if (period_duration_hours_slider->geometry().contains(event->pos()))
            QToolTip::showText(tooltip_pos, "Adjust period of displayed metrics in hours");
        else if (duplex_pushbutton->geometry().contains(event->pos()))
            QToolTip::showText(tooltip_pos, "Duplex page (two graphs)");
        else if (simplex_pushbutton->geometry().contains(event->pos()))
            QToolTip::showText(tooltip_pos, "Simplex page (one graph)");
        else if (period_end_hours_ago_slider->geometry().contains(event->pos()))
            QToolTip::showText(tooltip_pos, "Adjust hours ago of end of displayed metrics period");
        else if (next_pushbutton->geometry().contains(event->pos()))
            QToolTip::showText(tooltip_pos, "Next graph page");
        else QToolTip::hideText();
    }
    else QToolTip::hideText();
}
// ... Private functions

////ControlBar::~ControlBar ( ) {
////}
