QT += core
QT += widgets
QT += network
QT += xml

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets printsupport

QMAKE_MACOSX_DEPLOYMENT_TARGET=10.12

TARGET = CW_Remote
TEMPLATE = app

HEADERS += \
    CW_Remote.h \
    ControlBar.h \
    CustomPlot.h \
    CloudWatch.h \
    AlarmReport.h \
    AWS_Metrics.h \
    CW_Remote_Copyright.h \
    json_helpers.h \
    qcustomplot.h

SOURCES += \
    CW_Remote.cpp \
    ControlBar.cpp \
    json_helpers.cpp \
    qcustomplot.cpp \
    CustomPlot.cpp \
    CloudWatch.cpp \
    AlarmReport.cpp \
    json_helpers.cpp

ICON = CW_Remote.icns
