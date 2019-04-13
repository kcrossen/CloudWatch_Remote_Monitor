#ifndef CHARTVIEW_H
#define CHARTVIEW_H

#include <QtWidgets>

#include <QtCharts/QChartView>
#include <QtCharts/QLineSeries>
#include <QtCore/QDateTime>
#include <QtCharts/QDateTimeAxis>
#include <QtCharts/QValueAxis>
#include <QLegendMarker>

#include <QGraphicsScene>

#include <QToolTip>

#include <QVBoxLayout>
#include <QLabel>

#include "AWS_Metrics.h"
#include "json_helpers.h"


QT_CHARTS_USE_NAMESPACE

using namespace QtCharts;

class ChartView : public QtCharts::QChartView  {
    Q_OBJECT

public:
    ChartView ( QWidget *parent = nullptr );
    // ~ChartView ( );

    void
    setChartData ( const QVector<Metric_Statistics_Descriptor> Chart_Metric_Statistics_List );

    int zoom_level;

public slots:

protected:
    void
    resizeEvent ( QResizeEvent *event );

    void
    mouseMoveEvent ( QMouseEvent *event );

    void
    mousePressEvent ( QMouseEvent *event );

private:
    bool has_data;

    int zoom_factor;

    QtCharts::QChart *chart;

    QtCharts::QDateTimeAxis *axisX;
    QtCharts::QDateTimeAxis *axisX_top;
    QtCharts::QValueAxis *axisY_left;
    QtCharts::QValueAxis *axisY_right;

    QGraphicsScene *chartview_scene;
    QRectF plot_area_box;
    QGraphicsRectItem *plot_area_box_item;

};

#endif // CHARTVIEW_H
