#include "CustomPlot.h"

CustomPlot::CustomPlot( const QVector<Metric_Statistics_Descriptor> Chart_Metric_Statistics_List,
                        QWidget *parent ) : QCustomPlot ( parent ) {

    setMouseTracking(true);

    initialize_plot_private_values(Chart_Metric_Statistics_List);
    plot_datasets(Chart_Metric_Statistics_List);

    // QDateTime X-axis
    QSharedPointer<QCPAxisTickerDateTime> dateTicker(new QCPAxisTickerDateTime);
    dateTicker->setDateTimeFormat("HH:mm MM/dd");
    dateTicker->setTickCount(12);
    xAxis->setTicker(dateTicker);
    xAxis->setTickLabelFont(QFont(QFont().family(), 12));

    // double left and right Y-Axes
    QSharedPointer<QCPAxisTicker> valueTicker(new QCPAxisTicker);
    yAxis->setTicker(valueTicker);
    yAxis->setTickLabelFont(QFont(QFont().family(), 12));
    yAxis2->setTicker(valueTicker);
    yAxis2->setTickLabelFont(QFont(QFont().family(), 12));

    // xAxis->setLabel("Metric QDateTime");
    // yAxis->setLabel("Metric Value");
    // yAxis2->setLabel("Other Metric Value");

    // Nothing on top X-axis
    xAxis2->setVisible(true);
    xAxis2->setTicks(false);
    xAxis2->setTickLabels(false);

    yAxis->setVisible(true);
    if (left_y_axis_series_count > 0) {
        yAxis->setTicks(true);
        yAxis->setTickLabels(true);
    }

    yAxis2->setVisible(true);
    if (right_y_axis_series_count > 0) {
        yAxis2->setTicks(true);
        yAxis2->setTickLabels(true);
    }

    // set axis ranges to show all data:
    xAxis->setRange(data_min_datetime, data_max_datetime);
    if (left_y_axis_series_count > 0) yAxis->setRange(0, (data_max_value_left * 1.025));
    if (right_y_axis_series_count > 0) yAxis2->setRange(0, (data_max_value_right * 1.025));

    axisRect()->setMinimumMargins(QMargins(40, 0, 40, 0));

    // To get legend outside data plotting area:
    // Insert an empty row above the axis rect
    plotLayout()->insertRow(0);
    // Place the legend in the empty cell created
    plotLayout()->addElement(0, 0, legend);

    // Legend will wipe out graph if not arranged horizontally
    legend->setFillOrder(QCPLegend::foColumnsFirst);
    legend->setMargins(QMargins(0, 0, 0, 0));
    legend->layout()->setMargins(QMargins(0, 0, 0, 0));
    legend->setBorderPen(QPen(QColor(255, 255, 255, 0)));

    center_legend_items();

    plotLayout()->setRowSpacing(0);
    plotLayout()->setMargins(QMargins(0, 2, 0, 2));

    plotLayout()->setRowStretchFactor(0, 0.001);
    plotLayout()->setRowStretchFactor(1, 0.999);
    legend->setVisible(true);
}

void
CustomPlot::initialize_plot_private_values ( const QVector<Metric_Statistics_Descriptor> Chart_Metric_Statistics_List ) {
    zoom_level = 0;
    zoom_factor = 4;

    left_y_axis_series_count = 0;
    right_y_axis_series_count = 0;

    for (int idx = 0; idx < Chart_Metric_Statistics_List.size(); idx++) {
        QJsonObject metric_descriptor = Chart_Metric_Statistics_List[idx].Metric_Descriptor;
        QString which_y_axis = get_json_string_value(metric_descriptor,"YAxis", "left");
        if (which_y_axis == "left") left_y_axis_series_count += 1;
        else if (which_y_axis == "right") right_y_axis_series_count += 1;
    }

    // {@@@@@} This is not adaptive to enum:
    //            Average, Maximum, Minimum, SampleCount, Sum
    // Should be able to plot multiple line series from same dataset.
    // For example: Average, Minimum, Maximum on same plot
    QVector<double> *datapoint_time_list = Chart_Metric_Statistics_List[0].Datapoints_DateTime_List;

    data_min_datetime = (*datapoint_time_list)[0];
    data_max_datetime = (*datapoint_time_list)[0];
    data_min_value_left = 0;
    data_max_value_left = 0;
    data_min_value_right = 0;
    data_max_value_right = 0;
}

void
CustomPlot::plot_datasets ( const QVector<Metric_Statistics_Descriptor> Chart_Metric_Statistics_List ) {
    bool left_min_max_not_seeded = true;
    bool right_min_max_not_seeded = true;

    for (int line_idx = (Chart_Metric_Statistics_List.size() - 1); line_idx >= 0; line_idx--) {
        QJsonObject metric_descriptor = Chart_Metric_Statistics_List[line_idx].Metric_Descriptor;
        QString which_y_axis = get_json_string_value(metric_descriptor,"YAxis", "left");
        QString y_value = get_json_string_value(metric_descriptor,"YValue", "Maximum");

        QCPGraph *graph_ptr = nullptr;
        if (which_y_axis == "left") graph_ptr = addGraph(xAxis, yAxis);
        else if (which_y_axis == "right") graph_ptr = addGraph(xAxis, yAxis2);

        QColor line_color = QColor().fromRgb(0, 0, 0);
        if (metric_descriptor.contains("Color") and
            metric_descriptor["Color"].isArray()) {
            QJsonArray color_values = metric_descriptor["Color"].toArray();
            line_color = QColor().fromRgbF(color_values[0].toDouble(),
                                           color_values[1].toDouble(),
                                           color_values[2].toDouble());
        }
        graph_ptr->setLineStyle(QCPGraph::lsLine);
        graph_ptr->setPen(QPen(line_color));

        QString line_series_label = get_json_string_value(metric_descriptor,"MetricLabel", " ");
        if (which_y_axis == "left") {
            line_series_label += "(◀)";
        }
        else if (which_y_axis == "right") {
            line_series_label += "(▶)";
        }
        graph_ptr->setName(line_series_label);

        QVector<double> *datapoint_time_list = Chart_Metric_Statistics_List[line_idx].Datapoints_DateTime_List;
        QVector<double> *datapoint_value_list = nullptr;
        // Adaptive to enum: Average, Maximum, Minimum, SampleCount, Sum
        if (y_value == "Average")
            datapoint_value_list = Chart_Metric_Statistics_List[line_idx].Datapoints_Average_List;
        else if (y_value == "Maximum")
            datapoint_value_list = Chart_Metric_Statistics_List[line_idx].Datapoints_Maximum_List;
        else if (y_value == "Minimum")
            datapoint_value_list = Chart_Metric_Statistics_List[line_idx].Datapoints_Minimum_List;
        else if (y_value == "SampleCount")
            datapoint_value_list = Chart_Metric_Statistics_List[line_idx].Datapoints_SampleCount_List;
        else if (y_value == "Sum")
            datapoint_value_list = Chart_Metric_Statistics_List[line_idx].Datapoints_Sum_List;
        // ... Adaptive to enum: Average, Maximum, Minimum, SampleCount, Sum

        for (int data_idx = 0; data_idx < datapoint_time_list->size(); data_idx++) {
            if ((*datapoint_time_list)[data_idx] < data_min_datetime)
                data_min_datetime = (*datapoint_time_list)[data_idx];
            if ((*datapoint_time_list)[data_idx] > data_max_datetime)
                data_max_datetime = (*datapoint_time_list)[data_idx];

            if (which_y_axis == "left") {
                if (left_min_max_not_seeded and (data_idx == 0)) {
                    data_min_value_left = (*datapoint_value_list)[data_idx];
                    data_max_value_left = (*datapoint_value_list)[data_idx];
                    left_min_max_not_seeded = false;
                }
                else {
                    if ((*datapoint_value_list)[data_idx] < data_min_value_left)
                        data_min_value_left = (*datapoint_value_list)[data_idx];
                    if ((*datapoint_value_list)[data_idx] > data_max_value_left)
                        data_max_value_left = (*datapoint_value_list)[data_idx];
                }
            }
            else if (which_y_axis == "right") {
                if (right_min_max_not_seeded and (data_idx == 0)) {
                    data_min_value_right = (*datapoint_value_list)[data_idx];
                    data_max_value_right = (*datapoint_value_list)[data_idx];
                    right_min_max_not_seeded = false;
                }
                else {
                    if ((*datapoint_value_list)[data_idx] < data_min_value_right)
                        data_min_value_right = (*datapoint_value_list)[data_idx];
                    if ((*datapoint_value_list)[data_idx] > data_max_value_right)
                        data_max_value_right = (*datapoint_value_list)[data_idx];
                }
            }
        }

        graph_ptr->setData(*datapoint_time_list, *datapoint_value_list); // , alreadySorted=false
    }
}

void
CustomPlot::center_legend_items ( ) {
    // This function assumes that legend items are arranged horizontally
    legend->insertColumn(0);
    QCPTextElement *legendDummyFirst = new QCPTextElement(this);
    // Place dummy text element on same layer as legend
    legendDummyFirst->setLayer(legend->layer());
    legendDummyFirst->setText("");
    legend->addElement(0, 0, legendDummyFirst);

    QCPTextElement *legendDummyLast = new QCPTextElement(this);
    // Place dummy text element on same layer as legend
    legendDummyLast->setLayer(legend->layer());
    legendDummyLast->setText("");
    int legend_element_count = legend->elementCount();
    legend->addElement(0, legend_element_count, legendDummyLast);
}

void
CustomPlot::setCustomPlotData ( const QVector<Metric_Statistics_Descriptor> Chart_Metric_Statistics_List ) {

    clearGraphs();
    legend->clear();

    initialize_plot_private_values(Chart_Metric_Statistics_List);
    plot_datasets(Chart_Metric_Statistics_List);

    if (left_y_axis_series_count > 0) {
        yAxis->setTicks(true);
        yAxis->setTickLabels(true);
    }

    if (right_y_axis_series_count > 0) {
        yAxis2->setTicks(true);
        yAxis2->setTickLabels(true);
    }

    // set axis ranges to show all data:
    xAxis->setRange(data_min_datetime, data_max_datetime);
    if (left_y_axis_series_count > 0) yAxis->setRange(0, (data_max_value_left * 1.025));
    if (right_y_axis_series_count > 0) yAxis2->setRange(0, (data_max_value_right * 1.025));

    center_legend_items();

    replot(QCustomPlot::rpQueuedReplot);
}

void
CustomPlot::mouseMoveEvent ( QMouseEvent *event ) {
    QCPAxisRect *plotarea_rect = axisRect();
    if ((plotarea_rect->left() < event->pos().x()) and
        (event->pos().x() < plotarea_rect->right()) and
        (plotarea_rect->top() < event->pos().y()) and
        (event->pos().y() < plotarea_rect->bottom())) {
        // Cursor is inside data plotting area
        QString tooltip_text = "";
        double mousemove_left_value = 0;
        double mousemove_right_value = 0;

        qint64 mousemove_datetime_since_epoch = static_cast<qint64>(xAxis->pixelToCoord(event->pos().x()));
        QDateTime mousemove_datetime = QDateTime().fromSecsSinceEpoch(mousemove_datetime_since_epoch);
        tooltip_text += mousemove_datetime.toString("yyyy-MM-dd HH:mm");

        if (left_y_axis_series_count > 0) {
            mousemove_left_value = yAxis->pixelToCoord(event->pos().y());
            tooltip_text += QString("\n") + QString::number(mousemove_left_value, 'f', 2) + QString(" ◀");
        }

        if (right_y_axis_series_count > 0) {
            if (left_y_axis_series_count > 0) tooltip_text += QString(" ~~~ ");
            else tooltip_text += QString("\n");
            mousemove_right_value = yAxis2->pixelToCoord(event->pos().y());
            tooltip_text += QString("▶ ") + QString::number(mousemove_right_value, 'f', 2);
        }

        QPoint tooltip_pos = event->pos();
        tooltip_pos.setX(this->pos().x() + tooltip_pos.x()); // + tooltip_pos_offset_x)
        tooltip_pos.setY(this->pos().y() + tooltip_pos.y()); // + tooltip_pos_offset_y)

        QToolTip::showText(tooltip_pos, tooltip_text, this);
    }
    else QToolTip::hideText();
}

void
CustomPlot::mousePressEvent ( QMouseEvent *event ) {
    if (zoom_level == 0) {
        QCPAxisRect *plotarea_rect = axisRect();
        if ((plotarea_rect->left() < event->pos().x()) and
            (event->pos().x() < plotarea_rect->right()) and
            (plotarea_rect->top() < event->pos().y()) and
            (event->pos().y() < plotarea_rect->bottom())) {
            // Cursor is inside data plotting area
            double zoom_area_left =
                qMax((event->pos().x() - (plotarea_rect->width() / (2 * zoom_factor))), plotarea_rect->left());
            double zoom_area_top =
                qMax((event->pos().y() - (plotarea_rect->height() / (2 * zoom_factor))), plotarea_rect->top());
            double zoom_area_width = plotarea_rect->width() / zoom_factor;
            double zoom_area_height = plotarea_rect->height() / zoom_factor;
            if ((zoom_area_left + zoom_area_width) > (plotarea_rect->left() + plotarea_rect->width()))
                zoom_area_left = (plotarea_rect->left() + plotarea_rect->width()) - zoom_area_width;
            if ((zoom_area_top + zoom_area_height) > (plotarea_rect->top() + plotarea_rect->height()))
                zoom_area_top = (plotarea_rect->top() + plotarea_rect->height()) - zoom_area_height;
            double zoom_area_right = zoom_area_left + zoom_area_width;
            double zoom_area_bottom = zoom_area_top + zoom_area_height;

            // qint64 min_datetime_since_epoch = static_cast<qint64>(xAxis->pixelToCoord(zoom_area_left));
            // QDateTime zoom_min_datetime = QDateTime().fromSecsSinceEpoch(min_datetime_since_epoch);
            double zoom_min_datetime = xAxis->pixelToCoord(zoom_area_left);
            // qint64 max_datetime_since_epoch = static_cast<qint64>(xAxis->pixelToCoord(zoom_area_right));
            // QDateTime zoom_max_datetime = QDateTime().fromSecsSinceEpoch(max_datetime_since_epoch);
            double zoom_max_datetime = xAxis->pixelToCoord(zoom_area_right);

            // set axis ranges to show zoomed data:
            xAxis->setRange(zoom_min_datetime, zoom_max_datetime);
            if (left_y_axis_series_count > 0) {
                double zoom_min_left_value = yAxis->pixelToCoord(zoom_area_bottom);
                double zoom_max_left_value = yAxis->pixelToCoord(zoom_area_top);
                yAxis->setRange(zoom_min_left_value, zoom_max_left_value);
            }
            if (right_y_axis_series_count > 0) {
                double zoom_min_right_value = yAxis2->pixelToCoord(zoom_area_bottom);
                double zoom_max_right_value = yAxis2->pixelToCoord(zoom_area_top);
                yAxis2->setRange(zoom_min_right_value, zoom_max_right_value);
            }

            zoom_level += 1;

            replot(QCustomPlot::rpQueuedReplot);
        }
        else if ((plotarea_rect->left() < event->pos().x()) and
                 (event->pos().x() < plotarea_rect->right()) and
                 (event->pos().y() >= plotarea_rect->bottom())) {
            double zoom_area_left =
                qMax((event->pos().x() - (plotarea_rect->width() / (2 * zoom_factor))), plotarea_rect->left());
            double zoom_area_width = plotarea_rect->width() / zoom_factor;
            double zoom_area_right = zoom_area_left + zoom_area_width;

            // qint64 min_datetime_since_epoch = static_cast<qint64>(xAxis->pixelToCoord(zoom_area_left));
            // QDateTime zoom_min_datetime = QDateTime().fromSecsSinceEpoch(min_datetime_since_epoch);
            double zoom_min_datetime = xAxis->pixelToCoord(zoom_area_left);
            // qint64 max_datetime_since_epoch = static_cast<qint64>(xAxis->pixelToCoord(zoom_area_right));
            // QDateTime zoom_max_datetime = QDateTime().fromSecsSinceEpoch(max_datetime_since_epoch);
            double zoom_max_datetime = xAxis->pixelToCoord(zoom_area_right);

            // set axis ranges to show zoomed data:
            xAxis->setRange(zoom_min_datetime, zoom_max_datetime);

            zoom_level += 1;

            replot(QCustomPlot::rpQueuedReplot);
        }
        else if (((event->pos().x() <= plotarea_rect->left()) or
                  (event->pos().x() >= plotarea_rect->right())) and
                 (plotarea_rect->top() < event->pos().y()) and
                 (event->pos().y() < plotarea_rect->bottom())) {
            double zoom_area_top =
                qMax((event->pos().y() - (plotarea_rect->height() / (2 * zoom_factor))), plotarea_rect->top());
            double zoom_area_height = plotarea_rect->height() / zoom_factor;
            if ((zoom_area_top + zoom_area_height) > (plotarea_rect->top() + plotarea_rect->height()))
                zoom_area_top = (plotarea_rect->top() + plotarea_rect->height()) - zoom_area_height;
            double zoom_area_bottom = zoom_area_top + zoom_area_height;

            // set axis ranges to show zoomed data:
            if (left_y_axis_series_count > 0) {
                double zoom_min_left_value = yAxis->pixelToCoord(zoom_area_bottom);
                double zoom_max_left_value = yAxis->pixelToCoord(zoom_area_top);
                yAxis->setRange(zoom_min_left_value, zoom_max_left_value);
            }
            if (right_y_axis_series_count > 0) {
                double zoom_min_right_value = yAxis2->pixelToCoord(zoom_area_bottom);
                double zoom_max_right_value = yAxis2->pixelToCoord(zoom_area_top);
                yAxis2->setRange(zoom_min_right_value, zoom_max_right_value);
            }

            zoom_level += 1;

            replot(QCustomPlot::rpQueuedReplot);
        }
    }
    else {
        // set axis ranges to show all data:
        xAxis->setRange(data_min_datetime, data_max_datetime);
        if (left_y_axis_series_count > 0) yAxis->setRange(0, (data_max_value_left * 1.025));
        if (right_y_axis_series_count > 0) yAxis2->setRange(0, (data_max_value_right * 1.025));
        zoom_level -= 1;

        replot(QCustomPlot::rpQueuedReplot);
    }
}
