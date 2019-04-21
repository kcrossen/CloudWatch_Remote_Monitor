#include "AlarmReport.h"

AlarmReport::AlarmReport ( QWidget *parent ) : QFrame ( parent ) {

    // setMouseTracking(true);

    setWindowFlags(Qt::Tool | Qt::WindowStaysOnTopHint);

    setMaximumWidth(480);
    setContentsMargins(0, 0, 0, 0);

    alarm_report_label = new QLabel("alarm text goes here");
    alarm_report_label->setTextFormat(Qt::RichText);
    alarm_report_label->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Preferred);

    button_bar = new QFrame();
    button_bar->setContentsMargins(0, 0, 0, 0);
    button_bar->setFrameShape(QFrame::StyledPanel);
    button_bar->setAutoFillBackground(true);
    button_bar->setLineWidth(0);
    button_bar->setMaximumHeight(32);

    QHBoxLayout *button_bar_layout = new QHBoxLayout();
    button_bar_layout->setMargin(0);
    button_bar_layout->setContentsMargins(0, 0, 0, 0);
    button_bar_layout->setSpacing(2);
    button_bar_layout->setAlignment(Qt::AlignCenter);

    QPushButton *acknowledge_pushbutton = new QPushButton("Acknowledge (OK, got it)", parent=this);
    connect(acknowledge_pushbutton, SIGNAL(clicked()), this, SLOT(acknowledge_pushbutton_clicked()));
    // acknowledge_pushbutton->setMouseTracking(true);
    button_bar_layout->addWidget(acknowledge_pushbutton);

    QPushButton *dismiss_pushbutton = new QPushButton("Dismiss (Out of my way)", parent=this);
    connect(dismiss_pushbutton, SIGNAL(clicked()), this, SLOT(dismiss_pushbutton_clicked()));
    // acknowledge_pushbutton->setMouseTracking(true);
    button_bar_layout->addWidget(dismiss_pushbutton);

    button_bar->setLayout(button_bar_layout);

    QVBoxLayout *alarm_report_layout = new QVBoxLayout();
    alarm_report_layout->setMargin(0);
    alarm_report_layout->setContentsMargins(0, 0, 0, 0);
    alarm_report_layout->setSpacing(16);
    alarm_report_layout->setAlignment(Qt::AlignCenter);

    alarm_report_layout->addWidget(alarm_report_label);
    alarm_report_layout->addWidget(button_bar);

    setLayout(alarm_report_layout);

    setSizePolicy(QSizePolicy::Fixed, QSizePolicy::Fixed);
    setGeometry(50, 50, 480, (alarm_report_label->height() + button_bar->height() + 48));
}

void
AlarmReport::setAlarmText ( QString AlarmText ) {
    alarm_report_label->setText(AlarmText);
    alarm_report_label->adjustSize();
    setFixedSize((alarm_report_label->width() + 64),
                 (alarm_report_label->height() + button_bar->height() + 48));
}

void
AlarmReport::acknowledge_pushbutton_clicked (  ) {
    setVisible(false);
    emit alarmReportAcknowledged();
}

void
AlarmReport::dismiss_pushbutton_clicked (  ) {
    setVisible(false);
    emit alarmReportDismissed();
}


