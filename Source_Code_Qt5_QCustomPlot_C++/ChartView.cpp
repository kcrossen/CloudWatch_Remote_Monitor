#include "ChartView.h"

struct LineSeries_LineSeriesName {
    QtCharts::QLineSeries* line_series;
    QString line_series_name;
};


ChartView::ChartView ( QWidget *parent ) : QtCharts::QChartView ( parent ) {
    setContentsMargins(0, 0, 0, 0);

    has_data = false;

    zoom_level = 0;
    zoom_factor = 4;

    chart = new QtCharts::QChart();
    chart->setBackgroundRoundness(0);
    chart->layout()->setContentsMargins(0, 0, 0, 0);
    QMargins chart_margins = chart->margins();
    chart_margins.setTop(0);
    chart_margins.setBottom(0);
    chart->setMargins(chart_margins);

    axisX = nullptr;
    axisX_top = nullptr;
    axisY_left = nullptr;
    axisY_right = nullptr;

    setChart(chart);
    setRenderHint(QPainter::Antialiasing);

    setAttribute(Qt::WA_AlwaysShowToolTips);
    setMouseTracking(true);

    chartview_scene = scene();
    plot_area_box_item = nullptr;
}

void
ChartView::setChartData ( const QVector<Metric_Statistics_Descriptor> Chart_Metric_Statistics_List ) {
    chart->removeAllSeries();
    // Axes "remember" their previous state, ...
    // ... if not removed, previous min/max values will displayed
    if (axisX) chart->removeAxis(axisX);
    if (axisX_top) chart->removeAxis(axisX_top);
    if (axisY_left) chart->removeAxis(axisY_left);
    if (axisY_right) chart->removeAxis(axisY_right);

    // Replace with new "stateless" axes
    axisX = new QtCharts::QDateTimeAxis();
    axisX_top = new QtCharts::QDateTimeAxis();
    chart->addAxis(axisX, Qt::AlignBottom);
    chart->addAxis(axisX_top, Qt::AlignTop);

    int left_y_axis_series_count = 0;
    int right_y_axis_series_count = 0;

    for (int idx = 0; idx < Chart_Metric_Statistics_List.size(); idx++) {
        QJsonObject metric_descriptor = Chart_Metric_Statistics_List[idx].Metric_Descriptor;
        QString which_y_axis = get_json_string_value(metric_descriptor,"YAxis", "left");
        if (which_y_axis == "left") left_y_axis_series_count += 1;
        else if (which_y_axis == "right") right_y_axis_series_count += 1;
    }

    if (left_y_axis_series_count > 0) {
        axisY_left = new QtCharts::QValueAxis();
        chart->addAxis(axisY_left, Qt::AlignLeft);
    }

    if (right_y_axis_series_count > 0) {
        axisY_right = new QtCharts::QValueAxis();
        chart->addAxis(axisY_right, Qt::AlignRight);
    }

    // {@@@@@} This is not adaptive to enum:
    //            Average, Minimum, Maximum, SampleCount, Sum
    // Should be able to plot multiple line series from same dataset.
    // For example: Average, Minimum, Maximum on same plot
    QList<Metric_Statistics_Datapoint> datapoints =
        Chart_Metric_Statistics_List[0].Datapoints_Maximum_List;

    QDateTime data_min_datetime = datapoints[0].datapoint_datetime;
    QDateTime data_max_datetime = datapoints[0].datapoint_datetime;

    for (int idx = 1; idx < datapoints.size(); idx++) {
        if (datapoints[idx].datapoint_datetime < data_min_datetime)
            data_min_datetime = datapoints[idx].datapoint_datetime;
        if (datapoints[idx].datapoint_datetime > data_max_datetime)
            data_max_datetime = datapoints[idx].datapoint_datetime;
    }

    uint min_unixtime  = data_min_datetime.toTime_t();
    QDateTime data_min_datetime_quantized;
    data_min_datetime_quantized.setTime_t(min_unixtime - (min_unixtime % (60 * 60)));

    uint max_unixtime  = data_max_datetime.toTime_t();
    QDateTime data_max_datetime_quantized;
    data_max_datetime_quantized.setTime_t(max_unixtime + ((60 * 60) - max_unixtime % (60 * 60)));

    QtCharts::QLineSeries *workaround_line_series = new QtCharts::QLineSeries();
    workaround_line_series->append(QDateTime(data_min_datetime_quantized).toMSecsSinceEpoch(), 0);
    workaround_line_series->append(QDateTime(data_max_datetime_quantized).toMSecsSinceEpoch(), 0);
    QPen pen = workaround_line_series->pen();
    pen.setWidth(1);
    pen.setColor("lightgray");
    workaround_line_series->setPen(pen);

    chart->addSeries(workaround_line_series);
    workaround_line_series->attachAxis(axisX);
    if (left_y_axis_series_count > 0) workaround_line_series->attachAxis(axisY_left);
    else if (right_y_axis_series_count > 0) workaround_line_series->attachAxis(axisY_right);

    double data_min_value_left = 0;
    double data_max_value_left = 0;
    double data_min_value_right = 0;
    double data_max_value_right = 0;

    QVector<LineSeries_LineSeriesName> line_series_left_list;
    QVector<LineSeries_LineSeriesName> line_series_right_list;

    for (int idx = (Chart_Metric_Statistics_List.size() - 1); idx >= 0; idx--) {
        QJsonObject metric_descriptor = Chart_Metric_Statistics_List[idx].Metric_Descriptor;
        QString which_y_axis = get_json_string_value(metric_descriptor,"YAxis", "left");

        QList<Metric_Statistics_Datapoint> datapoints =
            Chart_Metric_Statistics_List[idx].Datapoints_Maximum_List;

        QtCharts::QLineSeries *line_series = new QtCharts::QLineSeries();

        for (int idx = 1; idx < datapoints.size(); idx++) {
            if (datapoints[idx].datapoint_datetime < data_min_datetime)
                data_min_datetime = datapoints[idx].datapoint_datetime;
            if (datapoints[idx].datapoint_datetime > data_max_datetime)
                data_max_datetime = datapoints[idx].datapoint_datetime;

            if (which_y_axis == "left") {
                if (datapoints[idx].datapoint_value < data_min_value_left)
                    data_min_value_left = datapoints[idx].datapoint_value;
                if (datapoints[idx].datapoint_value > data_max_value_left)
                    data_max_value_left = datapoints[idx].datapoint_value;
            }
            else if (which_y_axis == "right") {
                if (datapoints[idx].datapoint_value < data_min_value_right)
                    data_min_value_right = datapoints[idx].datapoint_value;
                if (datapoints[idx].datapoint_value > data_max_value_right)
                    data_max_value_right = datapoints[idx].datapoint_value;
            }

            line_series->append(QDateTime(datapoints[idx].datapoint_datetime).toMSecsSinceEpoch(),
                                datapoints[idx].datapoint_value);
        }

        QColor line_color = QColor().fromRgb(0, 0, 0);
        if (metric_descriptor.contains("Color") and
            metric_descriptor["Color"].isArray()) {
            QJsonArray color_values = metric_descriptor["Color"].toArray();
            line_color = QColor().fromRgbF(color_values[0].toDouble(),
                                           color_values[1].toDouble(),
                                           color_values[2].toDouble());
        }

        QPen pen = line_series->pen();
        pen.setWidth(0);
        pen.setColor(line_color);
        line_series->setPen(pen);

        chart->addSeries(line_series);
        line_series->attachAxis(axisX);
        if (which_y_axis == "left") line_series->attachAxis(axisY_left);
        else if (which_y_axis == "right") line_series->attachAxis(axisY_right);

        QString line_series_label = get_json_string_value(metric_descriptor,"MetricLabel", " ");
        if (which_y_axis == "left") {
            line_series_label += "(◀)";
            LineSeries_LineSeriesName lineseries_lineseries_name;
            lineseries_lineseries_name.line_series = line_series;
            lineseries_lineseries_name.line_series_name = line_series_label;
            line_series_left_list.append(lineseries_lineseries_name);
        }
        else if (which_y_axis == "right") {
            line_series_label += "(▶)";
            LineSeries_LineSeriesName lineseries_lineseries_name;
            lineseries_lineseries_name.line_series = line_series;
            lineseries_lineseries_name.line_series_name = line_series_label;
            line_series_right_list.append(lineseries_lineseries_name);
        }
    }

    for (int idx = 0; idx < line_series_left_list.size(); idx++) {
        LineSeries_LineSeriesName lineseries_lineseries_name = line_series_left_list[idx];
        lineseries_lineseries_name.line_series->setName(lineseries_lineseries_name.line_series_name);
    }

    for (int idx = 0; idx < line_series_right_list.size(); idx++) {
        LineSeries_LineSeriesName lineseries_lineseries_name = line_series_right_list[idx];
        lineseries_lineseries_name.line_series->setName(lineseries_lineseries_name.line_series_name);
    }

    // Not necessary:
    // axisX->setMin(data_max_datetime_quantized);
    // axisX->setMax(data_max_datetime_quantized);

    double delta_seconds = data_min_datetime_quantized.secsTo(data_max_datetime_quantized);
    int delta_hours = qRound(delta_seconds / (60 * 60));
    int delta_ticks = 12;
    QVector<int> factor_list({13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2});
    for (int idx = 0; idx < factor_list.size(); idx++) {
        int factor = factor_list[idx];
        if ((delta_hours % factor) == 0) {
            delta_ticks = factor;
            break;
        }
    }

    axisX->setTickCount(delta_ticks + 1);
    axisX->setFormat("hh:mm'\n'MM/dd");

    if (left_y_axis_series_count > 0) {
        axisY_left->setTickType(QtCharts::QValueAxis::TicksDynamic);
        axisY_left->setTickAnchor(0);
        double unit_interval = qPow(10, qFloor(log10(1.025 * data_max_value_left)));
        QVector<int> unit_interval_scale_list({1, 2, 4, 5, 8});
        for (int idx = 0; idx < unit_interval_scale_list.size(); idx++) {
            int unit_interval_scale = unit_interval_scale_list[idx];
            if ((data_max_value_left / (unit_interval / unit_interval_scale)) >= 4) {
                unit_interval = unit_interval / unit_interval_scale;
                break;
            }
        }
        axisY_left->setTickInterval(unit_interval);
        axisY_left->setRange(0, (1.025 * data_max_value_left));

        QColor pen_color = axisY_left->linePen().color();
        pen_color.setNamedColor("#ccccff");
        axisY_left->setLinePenColor(pen_color);
        axisY_left->setGridLineColor(pen_color);
        axisY_left->setGridLineVisible(false);
    }

    if (right_y_axis_series_count >= 0) {
        axisY_right->setTickType(QtCharts::QValueAxis::TicksDynamic);
        axisY_right->setTickAnchor(0);
        double unit_interval = qPow(10, qFloor(log10(1.025 * data_max_value_right)));
        QVector<int> unit_interval_scale_list({1, 2, 4, 5, 8});
        for (int idx = 0; idx < unit_interval_scale_list.size(); idx++) {
            int unit_interval_scale = unit_interval_scale_list[idx];
            if ((data_max_value_right / (unit_interval / unit_interval_scale)) >= 4) {
                unit_interval = unit_interval / unit_interval_scale;
                break;
            }
        }
        axisY_right->setTickInterval(unit_interval);
        axisY_right->setRange(0, (1.025 * data_max_value_right));

        QColor pen_color = axisY_right->linePen().color();
        pen_color.setNamedColor("#ffcccc");
        axisY_right->setLinePenColor(pen_color);
        axisY_right->setGridLineColor(pen_color);
        // axisY_right->setGridLineVisible(false);
    }

    // chart->legend()->setVisible(false);
    QLegend *legend = chart->legend();
    // Don't show the "fake" workaround_line_series' marker
    legend->markers(workaround_line_series)[0]->setVisible(false);
    legend->setVisible(true);
    legend->setAlignment(Qt::AlignTop);
    legend->setContentsMargins(0, 0, 0, 0);
    legend->layout()->setContentsMargins(0, 0, 0, 0);

    plot_area_box = chart->plotArea();
    QColor pen_color;
    pen_color.setNamedColor("lightgray");
    plot_area_box_item = chartview_scene->addRect(plot_area_box, pen_color);

    has_data = true;
}

void
ChartView::resizeEvent ( QResizeEvent *event ) {
    QtCharts::QChartView::resizeEvent(event);
    // Otherwise, we'll draw the box before ChartView is sized
    if (plot_area_box_item) chartview_scene->removeItem(plot_area_box_item);
    plot_area_box = chart->plotArea();
    QColor pen_color;
    pen_color.setNamedColor("lightgray");
    plot_area_box_item = chartview_scene->addRect(plot_area_box, pen_color);
}

//ChartView::~ChartView ( ) {
//}

void
ChartView::mouseMoveEvent ( QMouseEvent *event ) {
    if (has_data) {
        QRectF plotarea_rect = chart->plotArea();
        if (not plotarea_rect.contains(event->pos()))
            QToolTip::hideText();
        else {
            QString tooltip_text = "";

            QList<QAbstractSeries*> chart_series_list = chart->series();
            // First series is workaround for datetime axis labeling issue
            QPointF mouse_move_point_left = chart->mapToValue(event->pos(), chart_series_list[1]);
            QPointF mouse_move_point_right =
                chart->mapToValue(event->pos(), chart_series_list[chart_series_list.size()-1]);

            qint64 mouse_move_point_right_x = static_cast<qint64>(mouse_move_point_right.x());
            // qDebug() << mouse_move_point_right_x;
            QDateTime mouse_move_datetime = QDateTime().fromMSecsSinceEpoch(mouse_move_point_right_x);
            tooltip_text += mouse_move_datetime.toString("yyyy-MM-dd HH:mm");
            tooltip_text += QString("\n") + QString("L: ") + QString::number(mouse_move_point_left.y(), 'f', 2);
            tooltip_text += QString("   R: ") + QString::number(mouse_move_point_right.y(), 'f', 2);

            QPoint tooltip_pos = event->pos();
            tooltip_pos.setX(this->pos().x() + tooltip_pos.x()); // + tooltip_pos_offset_x)
            tooltip_pos.setY(this->pos().y() + tooltip_pos.y()); // + tooltip_pos_offset_y)

            QToolTip::showText(tooltip_pos, tooltip_text, this);
        }
    }
}

void
ChartView::mousePressEvent ( QMouseEvent *event ) {
    if (has_data) {
        if (zoom_level == 0) {
            QRectF plotarea_rect = chart->plotArea();
            double zoom_area_left =
                qMax((event->pos().x() - (plotarea_rect.width() / (2 * zoom_factor))), plotarea_rect.left());
            double zoom_area_top =
                qMax((event->pos().y() - (plotarea_rect.height() / (2 * zoom_factor))), plotarea_rect.top());
            double zoom_area_width = plotarea_rect.width() / zoom_factor;
            double zoom_area_height = plotarea_rect.height() / zoom_factor;
            if ((zoom_area_left + zoom_area_width) > (plotarea_rect.left() + plotarea_rect.width()))
                zoom_area_left = (plotarea_rect.left() + plotarea_rect.width()) - zoom_area_width;
            if ((zoom_area_top + zoom_area_height) > (plotarea_rect.top() + plotarea_rect.height()))
                zoom_area_top = (plotarea_rect.top() + plotarea_rect.height()) - zoom_area_height;
            QRectF zoom_rect = QRectF(zoom_area_left, zoom_area_top, zoom_area_width, zoom_area_height);
            chart->zoomIn(zoom_rect);
            zoom_level += 1;
        }
        else {
            chart->zoomReset();
            zoom_level -= 1;
        }
    }
}
