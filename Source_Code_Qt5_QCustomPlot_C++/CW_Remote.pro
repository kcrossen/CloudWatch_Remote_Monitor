QT += core
QT += widgets
QT += charts

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets printsupport

QMAKE_MACOSX_DEPLOYMENT_TARGET=10.12

TARGET = CW_Remote
TEMPLATE = app

HEADERS += \
    CW_Remote.h \
    ControlBar.h \
    AWS_Metrics.h \
    json_helpers.h \
    curl.h \
    qcustomplot.h \
    CustomPlot.h \
    CW_Remote_Copyright.h \
    AlarmReport.h

SOURCES += \
    CW_Remote.cpp \
    ControlBar.cpp \
    json_helpers.cpp \
    qcustomplot.cpp \
    CustomPlot.cpp \
    AlarmReport.cpp

macx:LIBS += -framework CoreFoundation

macx: LIBS += -L$$PWD/./ -laws-cpp-sdk-core
macx: LIBS += -L$$PWD/./ -laws-cpp-sdk-monitoring

macx:LIBS += /usr/lib/libcurl.4.dylib

ICON = CW_Remote.icns
