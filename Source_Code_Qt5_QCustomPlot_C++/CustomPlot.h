#ifndef CUSTOMPLOT_H
#define CUSTOMPLOT_H

#include <QtCore>
#include <QWidget>

#include "AWS_Metrics.h"
#include "qcustomplot.h"
#include "json_helpers.h"

class CustomPlot : public QCustomPlot {
    Q_OBJECT
public:
    explicit CustomPlot ( const QVector<Metric_Statistics_Descriptor> Chart_Metric_Statistics_List,
                          QCustomPlot *parent = nullptr );

    void
    setCustomPlotData ( const QVector<Metric_Statistics_Descriptor> Chart_Metric_Statistics_List );

    int zoom_level;

private:
    void
    initialize_plot_private_values ( const QVector<Metric_Statistics_Descriptor> Chart_Metric_Statistics_List );

    void
    plot_datasets ( const QVector<Metric_Statistics_Descriptor> Chart_Metric_Statistics_List );

    void
    center_legend_items ( );

    int zoom_factor;

    int left_y_axis_series_count;
    int right_y_axis_series_count;

    QDateTime data_min_datetime;
    QDateTime data_max_datetime;
    double data_min_value_left;
    double data_max_value_left;
    double data_min_value_right;
    double data_max_value_right;

protected:
    void
    mouseMoveEvent ( QMouseEvent *event );

    void
    mousePressEvent ( QMouseEvent *event );

signals:

public slots:

};

#endif // CUSTOMPLOT_H
