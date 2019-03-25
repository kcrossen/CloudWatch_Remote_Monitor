#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import kivy
kivy.require('1.9.0')

from kivy.config import Config
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '800')

from kivy.lang.builder import Builder

from kivy.utils import platform as Kivy_Platform

from kivy.app import App

from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label

from kivy.uix.textinput import TextInput

from kivy.clock import Clock

from os.path import dirname, isfile, join, expanduser
import platform

from io import BytesIO

import datetime, calendar

import json

import math

# import re

from collections import OrderedDict

# from functools import partial

import boto3

import copy

# Example of supporting imported non-library modules
# import sys
# current_script_path = sys.path[0]
#
# sys.path.append(join(current_script_path, "Wall_Time"))
# from Wall_Time import NYC_Wall_DateTime_Offset, UTC_Time_Zone

cw_remote_initialization_example = \
"""
{
    "layout": "paged",
    
    "refresh_interval_seconds": 60,
    
    "initial_period_hours": 24,

    "aws_access_id": "xxxxxxxxxxxxxxxxxxxx",
    "aws_secret_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "region_name": "xxxxxxxxx",

    "metric_descriptor_list": [
        [
            {
                "MetricLabel": "xxxxxx max CPU %",
                "YAxis": "right",
                "Color": [0.84, 0.15, 0.166],
                "MetricName": "CPUUtilization",
                "Namespace": "AWS/RDS",
                "Dimensions": [{"Name": "DBInstanceIdentifier",
                                "Value": "xxxxxxxxxxxxxxxxxxx"}],
                "Statistics": ["Average", "Maximum"],
                "Unit": "Percent"
            },
            {
                "MetricLabel": "xxxxxx max CPU %",
                "YAxis": "right",
                "LabelColor": [0.9, 0.45, 0.054],
                "Color": [1.00, 0.50, 0.06],
                "MetricName": "CPUUtilization",
                "Namespace": "AWS/RDS",
                "Dimensions": [{"Name": "DBInstanceIdentifier",
                                "Value": "xxxxxxxxxxxxxxxxxxx"}],
                "Statistics": ["Average", "Maximum"],
                "Unit": "Percent"
            },
            {
                "MetricLabel": "xxxxxx max CPU %",
                "YAxis": "left",
                "LabelColor": [0.5, 0.5, 1.00],
                "Color": [0.66, 0.66, 1.00],
                "MetricName": "CPUUtilization",
                "Namespace": "AWS/RDS",
                "Dimensions": [{"Name": "DBInstanceIdentifier",
                                "Value": "xxxxxxxxxxxxxxxxxxx"}],
                "Statistics": ["Average", "Maximum"],
                "Unit": "Percent"
            }
        ],
        [
            {
                "MetricLabel": "xxxxxx max writeIOPS x1000/sec",
                "YAxis": "right",
                "YFactor": 0.001,
                "Color": [0.84, 0.15, 0.166],
                "MetricName": "WriteIOPS",
                "Namespace": "AWS/RDS",
                "Dimensions": [{"Name": "DBInstanceIdentifier",
                                "Value": "xxxxxxxxxxxxxxxxxxx"}],
                "Statistics": ["Average", "Maximum"],
                "Unit": "Count/Second"
            },
            {
                "MetricLabel": "xxxxxx max writeIOPS x1000/sec",
                "YAxis": "left",
                "YFactor": 0.001,
                "LabelColor": [0.9, 0.45, 0.054],
                "Color": [1.00, 0.50, 0.06],
                "MetricName": "WriteIOPS",
                "Namespace": "AWS/RDS",
                "Dimensions": [{"Name": "DBInstanceIdentifier",
                                "Value": "xxxxxxxxxxxxxxxxxxx"}],
                "Statistics": ["Average", "Maximum"],
                "Unit": "Count/Second"
            }
        ]
    ],

    "widget_descriptor_list": [
        {
            "metrics": [
                [ "AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "xxxxxxxxxxxxxxxxxxx", { "color": "#d62728", "stat": "Maximum", "period": 60, "yAxis": "right" } ],
                [ "...", "xxxxxxxxxxxxxxxxxxx", { "stat": "Maximum", "period": 60, "yAxis": "left", "color": "#aec7e8" } ],
                [ "...", "xxxxxxxxxxxxxxxxxxx", { "stat": "Maximum", "period": 60, "color": "#ff7f0e", "yAxis": "right" } ]
            ],
            "start": "-PT24H",
            "timezone": "-0500",
            "width": 1280,
            "height": 380,
            "view": "timeSeries",
            "stacked": false,
            "region": "xxxxxxxxx",
            "title": "New CPU (max)",
            "period": 300
        },
        {
            "metrics": [
                [ "AWS/RDS", "WriteIOPS", "DBInstanceIdentifier", "xxxxxxxxxxxxxxxxxxx", { "stat": "Maximum", "period": 60, "yAxis": "right", "color": "#d62728" } ],
                [ "AWS/RDS", "ReadIOPS", "DBInstanceIdentifier", "xxxxxxxxxxxxxxxxxxx", { "stat": "Maximum", "period": 60, "color": "#1f77b4" } ],
                [ "AWS/RDS", "ReadIOPS", "DBInstanceIdentifier", "xxxxxxxxxxxxxxxxxxx", { "stat": "Maximum", "period": 60 } ],
                [ "AWS/RDS", "WriteIOPS", "DBInstanceIdentifier", "xxxxxxxxxxxxxxxxxxx", { "stat": "Maximum", "period": 60, "yAxis": "right", "color": "#ff7f0e" } ]
            ],
            "start": "-PT24H",
            "timezone": "-0500",
            "width": 1280,
            "height": 380,
            "view": "timeSeries",
            "stacked": false,
            "region": "xxxxxxxxx",
            "title": "New IO (max)",
            "period": 300
        }
    ]
}
"""

cw_remote_duplex_layout = True
Force_Duplex_Layout = True

Force_GetMetricWidgetImage = False

Screen_Manager_App = True # True # False #

Defer_CWapi_Requests = False # True # False #
Defer_CWapi_Requests_by_Seconds = 0.5

Testing_Bypass_Initialization = False # True # False # Should be False unless testing
Testing_Bypass_Initialization_Delay_Seconds = 0 # Should be zero unless testing

# There is a limit of 20 transactions per second for this API.
# Each GetMetricWidgetImage action has the following limits:
#     As many as 100 metrics in the graph.
#     Up to 100 KB uncompressed payload.

# If zero, no auto-refresh, if greater than zero, the auto-refresh interval in seconds
cw_remote_refresh_interval_seconds = 0 # (1 * 60)
Force_Refresh_Interval_Seconds = -1

cw_remote_ini_json = ""
cw_remote_ini = None
script_directory = dirname(__file__)
os_platform = platform.system()

# import simplejson

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


# Determine local wall time, this works for New York City
class Time_Zone ( datetime.tzinfo ):
    def __init__(self, offset_in_minutes):
        super(Time_Zone, self).__init__()
        self.offset = offset_in_minutes

    def utcoffset(self, dt):
        return datetime.timedelta(minutes=self.offset)

    def tzname(self, dt):
        return ""

    def dst(self, dt):
        return datetime.timedelta(0)

UTC_Time_Zone = Time_Zone(0)
Eastern_Daylight_Time_Zone = Time_Zone(-4 * 60)
Eastern_Standard_Time_Zone = Time_Zone(-5 * 60)

def NYC_Wall_DateTime_Offset ( Time_Zone_Aware_DateTime ):
    # In the US, since 2007, DST starts at 2am (standard time) on the second
    # Sunday in March, which is the first Sunday on or after Mar 8.
    # and ends at 2am (DST time; 1am standard time) on the first Sunday of Nov.
    datetime_nyc_wall = Time_Zone_Aware_DateTime.astimezone(Eastern_Standard_Time_Zone)

    # Test whether in primetime
    begin_daylight_savings = \
        datetime.datetime(year=datetime_nyc_wall.year, month=3, day=8, hour=2, tzinfo=Eastern_Standard_Time_Zone)
    begin_daylight_savings += datetime.timedelta(days=(6 - begin_daylight_savings.date().weekday()))

    end_daylight_savings = \
        datetime.datetime(year=datetime_nyc_wall.year, month=11, day=1, hour=1, tzinfo=Eastern_Standard_Time_Zone)
    end_daylight_savings += datetime.timedelta(days=(6 - end_daylight_savings.date().weekday()))

    if ((datetime_nyc_wall >= begin_daylight_savings) and (datetime_nyc_wall <= end_daylight_savings)):
        datetime_nyc_wall_offset = "-0400"
    else: datetime_nyc_wall_offset = "-0500"

    return datetime_nyc_wall_offset

def NYC_Wall_DateTime ( Time_Zone_Aware_DateTime ):
    # In the US, since 2007, DST starts at 2am (standard time) on the second
    # Sunday in March, which is the first Sunday on or after Mar 8.
    # and ends at 2am (DST time; 1am standard time) on the first Sunday of Nov.
    datetime_nyc_wall = Time_Zone_Aware_DateTime.astimezone(Eastern_Standard_Time_Zone)

    # Test whether in primetime
    begin_daylight_savings = \
        datetime.datetime(year=datetime_nyc_wall.year, month=3, day=8, hour=2, tzinfo=Eastern_Standard_Time_Zone)
    begin_daylight_savings += datetime.timedelta(days=(6 - begin_daylight_savings.date().weekday()))

    end_daylight_savings = \
        datetime.datetime(year=datetime_nyc_wall.year, month=11, day=1, hour=1, tzinfo=Eastern_Standard_Time_Zone)
    end_daylight_savings += datetime.timedelta(days=(6 - end_daylight_savings.date().weekday()))

    if ((datetime_nyc_wall >= begin_daylight_savings) and (datetime_nyc_wall <= end_daylight_savings)):
        datetime_nyc_wall = Time_Zone_Aware_DateTime.astimezone(Eastern_Daylight_Time_Zone)

    return datetime_nyc_wall

def Return_NYC_Wall_Time_String ( UTC_Datetime=None, NYC_Wall_Datetime=None, Time_Zone_Indicator="" ):
    if (UTC_Datetime is not None):
        datetime_NYC_Wall = NYC_Wall_DateTime(UTC_Datetime)
    elif (NYC_Wall_Datetime is not None):
        datetime_NYC_Wall = NYC_Wall_Datetime
    else:
        datetime_NYC_Wall = None

    isoformatted_datetime_NYC_Wall = datetime_NYC_Wall.isoformat()
    if (Time_Zone_Indicator == "E"):
        return isoformatted_datetime_NYC_Wall[:-6]

    if (datetime_NYC_Wall is not None):
        return (isoformatted_datetime_NYC_Wall + Time_Zone_Indicator)
    else: return "Error"


if (os_platform == "Darwin"):
    try:
        if (isfile(join(script_directory, "CW_Remote.ini"))):
            ini_directory = script_directory
        else:
            home_dir = expanduser("~")
            ini_dir = "Documents/CW_Remote"
            ini_directory = join(home_dir, ini_dir)

        cw_remote_ini_file = open(join(ini_directory, "CW_Remote.ini"), "r")
        cw_remote_ini_json = cw_remote_ini_file.read()
        cw_remote_ini_file.close()

    except:
        cw_remote_ini_json = ""

elif (os_platform == "Linux"):
    if (Kivy_Platform == "android"):
        # Pydroid 3 fails to install pycairo
        # Gtk backend requires PyGObject or pgi
        # "Pip" menu item, "Install": pygobject
        # "Running setup.py install for pycairo: finished with status 'error' "
        # ...
        # "No package 'cairo' found"
        Force_GetMetricWidgetImage = True
        try:
            # To run from Pydroid 3
            if (isfile(join(script_directory, "CW_Remote.ini"))):
                ini_directory = script_directory
            else:
                home_dir = expanduser("~")
                ini_dir = "Documents/CW_Remote"
                ini_directory = join(home_dir, ini_dir)

            cw_remote_ini_file = open(join(ini_directory, "CW_Remote.ini"), "r")
            cw_remote_ini_json = cw_remote_ini_file.read()
            cw_remote_ini_file.close()

            # documents_dir = "/system/storage/emulated/0/Documents"
            # ini_dir = "CW_Remote"
            # ini_directory = join(documents_dir, ini_dir)
            #
            # cw_remote_ini_file = open(join(ini_directory, "CW_Remote.ini"), "r")
            # cw_remote_ini_json = cw_remote_ini_file.read()
            # cw_remote_ini_file.close()

        except:
            cw_remote_ini_json = ""

elif (os_platform == "Windows"):
    cw_remote_ini_json = ""

else:
    cw_remote_ini_json = ""

if (Testing_Bypass_Initialization):
    cw_remote_ini_json = cw_remote_initialization_example

if (len(cw_remote_ini_json) > 0):
    # This should be the same for any OS platform, ...
    # ... but may still fail by being ill-structured
    try:
        # Load initialization from the JSON ini file
        cw_remote_ini = json.loads(cw_remote_ini_json, object_pairs_hook=OrderedDict)

        cw_remote_layout = cw_remote_ini.get("layout", '')
        if (cw_remote_layout == "paged"): cw_remote_duplex_layout = False
        elif (cw_remote_layout == "duplex"): cw_remote_duplex_layout = True

        if ("refresh_interval_seconds" in cw_remote_ini):
            cw_remote_refresh_interval_seconds = cw_remote_ini["refresh_interval_seconds"]
        if (Force_Refresh_Interval_Seconds >= 0):
            cw_remote_refresh_interval_seconds = Force_Refresh_Interval_Seconds
        # Fractional seconds not supported
        cw_remote_refresh_interval_seconds = int(round(cw_remote_refresh_interval_seconds))

        if (Force_Duplex_Layout): cw_remote_duplex_layout = True

        metric_descriptor_list = []
        ini_metric_descriptor_list = cw_remote_ini.get("metric_descriptor_list", [])
        for metric_descr in ini_metric_descriptor_list:
            # metric_descr is itself a list, potentially with one element, or with two
            this_metric_descriptor = copy.deepcopy(metric_descr)
            metric_descriptor_list.append(this_metric_descriptor)

        widget_descriptor_list = []
        ini_widget_descriptor_list = cw_remote_ini.get("widget_descriptor_list", [])
        for widget_descr in ini_widget_descriptor_list:
            this_widget_descriptor = widget_descr.copy()
            widget_descriptor_list.append(this_widget_descriptor)

        if (len(widget_descriptor_list) < 2):
            cw_remote_duplex_layout = False

        if (cw_remote_duplex_layout):
            # No way to page through these, reduce fetch effort/time
            # widget_descriptor_list = widget_descriptor_list[:2]
            pass
        else:
            # Not duplex, make graphs "higher", i.e. more vertical resolution
            for widget_descr in widget_descriptor_list:
                widget_descr["height"] = 2 * widget_descr["height"]

        fw_widget_figure_list = []
        for idx in range(len(metric_descriptor_list)):
            fw_widget_figure_list.append(None)

        ci_widget_image_list = []
        for idx in range(len(widget_descriptor_list)):
            ci_widget_image_list.append(None)

        # Initialize connection to CloudWatch.
        cloudwatch_client = \
            boto3.client('cloudwatch',
                         aws_access_key_id=cw_remote_ini.get("aws_access_id", ''),
                         aws_secret_access_key=cw_remote_ini.get("aws_secret_key", ''),
                         region_name=cw_remote_ini.get("region_name", ''))

    except:
    # except Exception, e:
        # If initialization file is missing, don't build usual UI
        cw_remote_ini = None
else:
    cw_remote_ini = None


def bound ( low, high, value ):
    return max(low, min(high, value))

if (not Force_GetMetricWidgetImage):
    from matplotlib_backend_kivyagg import FigureCanvasKivyAgg as FigureCanvas
    import matplotlib.pyplot as plotter
    from matplotlib.dates import MinuteLocator, HourLocator, DayLocator, DateFormatter

    def Get_Metric_Statistics_Datapoints ( Metric_Index, Perion_End_UTC, Period_Hours ):
        period_begin_utc = Perion_End_UTC - datetime.timedelta(hours=Period_Hours)

        datapoint_summary_seconds = 60

        # The maximum number of data points returned from a single call is 1,440.
        # The period for each datapoint can be 1, 5, 10, 30, 60, or any multiple of 60 seconds.

        datapoint_count = (Period_Hours * 60 * 60) / datapoint_summary_seconds
        while (datapoint_count > 1440):
            datapoint_summary_seconds += 60
            datapoint_count = (Period_Hours * 60 * 60) / datapoint_summary_seconds

        metric_statistics_list = []

        metric_descr_list = metric_descriptor_list[Metric_Index]

        for metric_descr in metric_descr_list:
            these_metric_statistics = \
                cloudwatch_client.get_metric_statistics(MetricName=metric_descr["MetricName"],
                                                        Namespace=metric_descr["Namespace"],
                                                        Dimensions=metric_descr["Dimensions"],
                                                        StartTime=period_begin_utc,
                                                        EndTime=Perion_End_UTC,
                                                        Period=datapoint_summary_seconds,
                                                        Statistics=metric_descr["Statistics"],
                                                        Unit=metric_descr["Unit"])
            these_metric_statistics["MetricDescriptor"] = metric_descr

            metric_statistics_list.append(these_metric_statistics)

        return metric_statistics_list

    def Metric_Statistics_Datapoints_Time_and_Values ( Metric_Statistics_Datapoints, Y_Factor ):
        data_point_list = []
        for data_point in Metric_Statistics_Datapoints:
            data_datetime = data_point["Timestamp"]
            nyc_wall_time_offset = NYC_Wall_DateTime_Offset(data_datetime)
            data_datetime = data_datetime + datetime.timedelta(hours=int(nyc_wall_time_offset) / 100)
            data_maximum = data_point["Maximum"] * Y_Factor
            data_average = data_point["Average"] * Y_Factor
            data_point_list.append((data_datetime, data_maximum, data_average))
        data_point_list.sort()

        data_time_list = [time for time, max, avg in data_point_list]
        data_max_list = [max for time, max, avg in data_point_list]
        data_avg_list = [avg for time, max, avg in data_point_list]
        return (data_time_list, data_max_list, data_avg_list)

    every_day = tuple([day for day in range(31)])

    every_hour = tuple([hour for hour in range(24)])
    every_two_hours = tuple([(2 * hour) for hour in range(24//2)])
    every_three_hours = tuple([(3 * hour) for hour in range(24//3)])
    every_four_hours = tuple([(4 * hour) for hour in range(24//4)])
    every_six_hours = tuple([(6 * hour) for hour in range(24//6)])

    every_five_minutes = tuple([(5 * minute) for minute in range(60//5)])
    every_ten_minutes = tuple([(10 * minute) for minute in range(60//10)])
    every_fifteen_minutes = tuple([(15 * minute) for minute in range(60//15)])

    def Prepare_Get_Metric_Statistics_Figure ( Mertric_Statistics_List,
                                               Period_Value, Graph_Width, Graph_Height ):

        line_width = 0.75

        plot_figure = plotter.figure(figsize=((Graph_Width / 100), (Graph_Height / 100)), dpi=100)

        axes = plot_figure.gca()
        axis_2 = axes.twinx()

        # Store tuples of (text, text_color) for the two axes
        # There could be none, one, or two
        left_y_axis_labels = []
        right_y_axis_labels = []

        minimum_time = None
        maximum_time = None

        for metric_stats in reversed(Mertric_Statistics_List):
            metric_stats_descriptor = metric_stats.get("MetricDescriptor", {})
            metric_stats_datapoints = metric_stats.get("Datapoints", [])
            datapoints_time, datapoints_max, datapoints_avg = \
                Metric_Statistics_Datapoints_Time_and_Values(metric_stats_datapoints,
                                                             metric_stats_descriptor.get("YFactor", 1))
            if ((minimum_time is None) and (maximum_time is None)):
                minimum_time = datapoints_time[0]
                maximum_time = datapoints_time[-1]
            else:
                minimum_time = min(minimum_time, datapoints_time[0])
                maximum_time = max(maximum_time, datapoints_time[-1])

            line_color = metric_stats_descriptor.get("Color", [0, 0, 0])

            this_y_axis_label = (metric_stats_descriptor.get("MetricLabel", " "),
                                 tuple(metric_stats_descriptor.get("LabelColor", line_color)))
            y_axis = metric_stats_descriptor.get("YAxis", "left")
            if (y_axis == "left"):
                left_y_axis_labels.append(this_y_axis_label)
                this_axis = axes
            else:
                right_y_axis_labels.append(this_y_axis_label)
                this_axis = axis_2

            this_axis.plot(datapoints_time, datapoints_max, linewidth=line_width, color=tuple(line_color))
            this_axis.tick_params('y', colors="black")

        # Now draw left y axis labels and ...
        if (len(left_y_axis_labels) > 0):
            # Darker y-axis label text for legibility
            label_text, label_color = left_y_axis_labels[0]
            axes.set_ylabel(label_text, fontsize="large", color=label_color)

            if (len(left_y_axis_labels) > 1):
                label_text, label_color = left_y_axis_labels[1]
                plotter.gcf().text(0.02, 0.55, label_text,
                                       rotation="vertical", verticalalignment="center",
                                       fontsize="large", color=label_color)
        # ... right y axis labels
        if (len(right_y_axis_labels) > 0):
            # Darker y-axis label text for legibility
            label_text, label_color = right_y_axis_labels[0]
            axis_2.set_ylabel(label_text, fontsize="large", color=label_color)

            if (len(right_y_axis_labels) > 1):
                label_text, label_color = right_y_axis_labels[1]
                plotter.gcf().text(0.98, 0.55, label_text,
                                       rotation="vertical", verticalalignment="center",
                                       fontsize="large", color=label_color)

        # Attempt optimum x axis (date/time) tic labeling, complicated, heuristic
        major_formatter = "hour"

        # Adaptive time axis tics and tic labels
        if ((Period_Value >= 1) and (Period_Value < 6)):
            axes.xaxis.set_major_locator(HourLocator(every_hour))
            axes.xaxis.set_minor_locator(MinuteLocator(every_five_minutes))
        elif ((Period_Value >= 6) and (Period_Value < 12)):
            axes.xaxis.set_major_locator(HourLocator(every_hour))
            axes.xaxis.set_minor_locator(MinuteLocator(every_ten_minutes))
        elif ((Period_Value >= 12) and (Period_Value < 18)):
            axes.xaxis.set_major_locator(HourLocator(every_hour))
            axes.xaxis.set_minor_locator(MinuteLocator(every_fifteen_minutes))
        elif ((Period_Value >= 18) and (Period_Value < 24)):
            axes.xaxis.set_major_locator(HourLocator(every_hour))
            axes.xaxis.set_minor_locator(MinuteLocator((0, 30)))
        elif ((Period_Value >= 24) and (Period_Value < (24 + 12))):
            axes.xaxis.set_major_locator(HourLocator(every_two_hours))
            axes.xaxis.set_minor_locator(HourLocator(every_hour))
        elif ((Period_Value >= (24 + 12)) and (Period_Value < (48 + 12))):
            axes.xaxis.set_major_locator(HourLocator(every_three_hours))
            axes.xaxis.set_minor_locator(HourLocator(every_hour))

        elif ((Period_Value >= (48 + 12)) and (Period_Value < (72 + 12))):
            axes.xaxis.set_major_locator(HourLocator(every_four_hours))
            axes.xaxis.set_minor_locator(HourLocator(every_hour))

        elif ((Period_Value >= (72 + 12)) and (Period_Value < (96 + 12))):
            axes.xaxis.set_major_locator(HourLocator(every_six_hours))
            axes.xaxis.set_minor_locator(HourLocator(every_three_hours))

        elif ((Period_Value >= (96 + 12)) and (Period_Value < (120 + 12))):
            axes.xaxis.set_major_locator(HourLocator((0, 12)))
            axes.xaxis.set_minor_locator(HourLocator(every_six_hours))

        elif ((Period_Value >= (120 + 12)) and (Period_Value < (144 + 12))):
            axes.xaxis.set_major_locator(DayLocator(every_day))
            axes.xaxis.set_minor_locator(HourLocator(every_four_hours))
            major_formatter = "day"

        elif ((Period_Value >= (144 + 12)) and (Period_Value < (168 + 12))):
            axes.xaxis.set_major_locator(DayLocator(every_day))
            axes.xaxis.set_minor_locator(HourLocator(every_six_hours))
            major_formatter = "day"

        if (major_formatter == "hour"):
            axes.xaxis.set_major_formatter(DateFormatter("%H:00\n%m/%d"))
        elif (major_formatter == "day"):
            axes.xaxis.set_major_formatter(DateFormatter("%H:00\n%m/%d"))

        # axes.xaxis.set_minor_formatter(DateFormatter("%M"))
        plotter.setp(axes.get_xticklabels(), rotation=0, ha="center")

        # cpu_time is sorted, so this can work
        axes.set_xlim(minimum_time, maximum_time)
        axes.grid(True)

        # Trim off real estate wasting margins
        plotter.subplots_adjust(left=0.06, bottom=0.13, right=0.94, top=0.98, wspace=0, hspace=0)

        canvas = FigureCanvas(plot_figure)
        canvas.draw()

        return canvas


Builder.load_string(
"""
<Tab_Bar_BoxLayout>:
    orientation: 'vertical'
    
    canvas:
        Color:
            rgba: 0.5, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    size_hint: (0.02, 1)
    
    Widget:
        Button:
            padding: (15, 5)
            on_press: root.trigger_on_press_previous()
            center_x: self.parent.center_x
            center_y: self.parent.top - (self.texture_size[0] / 2.0)
            size: self.texture_size
            canvas.before:
                PushMatrix
                Rotate:
                    angle: 90
                    origin: self.center
            canvas.after:
                PopMatrix
            text: "Previous"

        Button:
            padding: (15, 5)
            on_press: root.trigger_on_press_simplex()
            center_x: self.parent.center_x
            center_y: self.parent.top - (self.parent.height * 0.3)
            size: self.texture_size
            canvas.before:
                PushMatrix
                Rotate:
                    angle: 90
                    origin: self.center
            canvas.after:
                PopMatrix
            text: "Simplex"
            
        Button:
            padding: (15, 5)
            on_press: root.trigger_on_press_help()
            center: self.parent.center
            size: self.texture_size
            canvas.before:
                PushMatrix
                Rotate:
                    angle: 90
                    origin: self.center
            canvas.after:
                PopMatrix
            text: "Help"

        Button:
            padding: (15, 5)
            on_press: root.trigger_on_press_duplex()
            center_x: self.parent.center_x
            center_y: self.parent.top - (self.parent.height * 0.7)
            size: self.texture_size
            canvas.before:
                PushMatrix
                Rotate:
                    angle: 90
                    origin: self.center
            canvas.after:
                PopMatrix
            text: "Duplex"
            
        Button:
            padding: (15, 5)
            on_press: root.trigger_on_press_next()
            center_x: self.parent.center_x
            center_y: self.parent.top - self.parent.height + (self.texture_size[0] / 2.0)
            size: self.texture_size
            canvas.before:
                PushMatrix
                Rotate:
                    angle: 90
                    origin: self.center
            canvas.after:
                PopMatrix
            text: "Next"
""")

class Tab_Bar_BoxLayout ( BoxLayout ):

    def __init__(self, **kwargs):
        super(Tab_Bar_BoxLayout, self).__init__(**kwargs)
        self.register_event_type('on_press_previous')
        self.register_event_type('on_press_next')

        self.register_event_type('on_press_simplex')
        self.register_event_type('on_press_duplex')

        self.register_event_type('on_press_help')

    def trigger_on_press_previous ( self, *args ):
        self.dispatch('on_press_previous')
    def on_press_previous ( self, *args ):
        pass

    def trigger_on_press_next ( self, *args ):
        self.dispatch('on_press_next')
    def on_press_next ( self, *args ):
        pass

    def trigger_on_press_simplex ( self, *args ):
        self.dispatch('on_press_simplex')
    def on_press_simplex ( self, *args ):
        pass

    def trigger_on_press_duplex ( self, *args ):
        self.dispatch('on_press_duplex')
    def on_press_duplex ( self, *args ):
        pass

    def trigger_on_press_help ( self, *args ):
        self.dispatch('on_press_help')
    def on_press_help ( self, *args ):
        pass


# This slider extension allows the code to avoid the very expensive refreshes of ...
# ... the widget images until the user has stopped sliding the slider. Refresh then.
class Slider_Extended ( Slider ):
    def __init__(self, **kwargs):
        self.register_event_type('on_release')
        super(Slider_Extended, self).__init__(**kwargs)

    def on_release ( self ):
        pass
    # Because there appears to be no event for touch_up, ...
    # ... override on_touch_up and create a custom event
    def on_touch_up ( self, touch ):
        super(Slider_Extended, self).on_touch_up(touch)
        if (touch.grab_current == self):
            self.dispatch('on_release')
            return True

class Control_Bar ( BoxLayout ):
    # self.Period_Value = cw_remote_ini.get("initial_period_hours", 24)
    Period_Value_Steps = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24,  # 18
                          26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48,  # 12
                          50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72,  # 12
                          74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 96,  # 12
                          100, 104, 108, 112, 116, 120,  # 6
                          124, 128, 132, 136, 140, 144,  # 6
                          148, 152, 156, 160, 164, 168]  # 6

    Period_End_Value_Steps = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24,  # 19
                              26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48,  # 12
                              50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72,  # 12
                              74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 96,  # 12
                              100, 104, 108, 112, 116, 120,  # 6
                              124, 128, 132, 136, 140, 144,  # 6
                              148, 152, 156, 160, 164, 168]  # 6

    def __init__(self, **kwargs):
        self.register_event_type('on_release')

        self._period_value = 24
        self._period_end_value = 0

        super(Control_Bar, self).__init__(**kwargs)

        self.period_label = \
            Label(id="period_label",
                  text=self.period_value_display(self._period_value), size_hint=(0.075, 1))

        self.period_slider = \
            Slider_Extended(id="period_slider",
                            min=-1000, max=-1,
                            value=-(999 * (self.Period_Value_Steps.index(self._period_value) /
                                           len(self.Period_Value_Steps))),
                            step=1,
                            border_horizontal=[0, 0, 0, 0], padding=12, size_hint=(0.4, 1))
        self.period_slider.bind(value=self.on_period_value_change)
        self.period_slider.bind(on_release=self.trigger_on_release)

        button_refresh = Button(text="Refresh", size_hint=(0.05, 1))
        button_refresh.font_size = 14
        button_refresh.bind(on_press=self.trigger_on_release)

        self.period_end_slider = \
            Slider_Extended(id="period_end_slider",
                            min=-1000, max=0, value=0, step=1,
                            border_horizontal=[0, 0, 0, 0], padding=12, size_hint=(0.4, 1))
        self.period_end_slider.bind(value=self.on_period_end_value_change)
        self.period_end_slider.bind(on_release=self.trigger_on_release)

        self.period_end_label = \
            Label(id="period_end_label",
                  text=(self.period_value_display(self._period_end_value) + " ago"), size_hint=(0.075, 1))

        self.add_widget(self.period_label)
        self.add_widget(self.period_slider)

        self.add_widget(button_refresh)

        self.add_widget(self.period_end_slider)
        self.add_widget(self.period_end_label)

    def period_value_display ( self, Period_Value ):
        period_value_string = ""
        if ((Period_Value // 24) > 0): period_value_string += str(Period_Value // 24) + "D"
        if (((Period_Value % 24) > 0) or (len(period_value_string) == 0)):
            if (len(period_value_string) > 0): period_value_string += " "
            period_value_string += str(Period_Value % 24) + "H"
        return period_value_string

    def set_period_value ( self, period_value, *args ):
        self._period_value = period_value
        self.period_slider.value = -(999 * (self.Period_Value_Steps.index(self._period_value) /
                                            len(self.Period_Value_Steps)))

    def on_period_value_change ( self, instance, period_slider_value, *args ):
        # print (period_slider_value)
        period_value_index = int(round(len(self.Period_Value_Steps) * (abs(period_slider_value) / 999)))
        self._period_value = self.Period_Value_Steps[bound(0, (len(self.Period_Value_Steps) -1), period_value_index)]
        self.period_label.text = (self.period_value_display(self._period_value))
        # print (period_slider_value, period_value_index, self._period_value, self.period_label.text)
        return True

    def set_period_end_value ( self, period_end_value, *args ):
        self._period_end_value = period_end_value
        self.period_end_slider.value = -(1000 * (self.Period_End_Value_Steps.index(self._period_end_value) /
                                                 len(self.Period_End_Value_Steps)))

    def on_period_end_value_change ( self, instance, period_end_slider_value, *args ):
        period_end_value_index = int(round(len(self.Period_End_Value_Steps) * (abs(period_end_slider_value) / 1000)))
        self._period_end_value = self.Period_End_Value_Steps[bound(0, (len(self.Period_End_Value_Steps) -1), period_end_value_index)]
        self.period_end_label.text = (self.period_value_display(self._period_end_value) + " ago")
        return True

    def on_release(self, *args):
        pass

    def trigger_on_release ( self, *args ):
        self.dispatch('on_release', self._period_value, self._period_end_value)
        return True


def period_begin_NYC_wall_time ( Period_Hours, Period_End_Hours_Ago ):
    datetime_now_utc = datetime.datetime.now(UTC_Time_Zone)
    period_end_utc = datetime_now_utc - datetime.timedelta(hours=Period_End_Hours_Ago)
    period_begin_utc = period_end_utc - datetime.timedelta(hours=Period_Hours)

    period_begin_NYC_Wall = NYC_Wall_DateTime(period_begin_utc)
    period_end_NYC_Wall = NYC_Wall_DateTime(period_end_utc)

    period_begin_nyc_wall_string = \
        Return_NYC_Wall_Time_String(NYC_Wall_Datetime=period_begin_NYC_Wall, Time_Zone_Indicator="E")[:-10].replace("T", " ")
    period_end_nyc_wall_string = \
        Return_NYC_Wall_Time_String(NYC_Wall_Datetime=period_end_NYC_Wall, Time_Zone_Indicator="E")[:-10].replace("T", " ")

    return (calendar.day_abbr[period_begin_NYC_Wall.weekday()] + " " + period_begin_nyc_wall_string + "NYC to " +
            calendar.day_abbr[period_end_NYC_Wall.weekday()] + " " + period_end_nyc_wall_string + "NYC")

# Build the app screen
class CW_Remote ( App ):

    def build ( self ):
        self.Period_Value = 24
        self.Period_End_Value = 0

        self.title = "CW_Remote" + " (" + period_begin_NYC_wall_time(self.Period_Value, self.Period_End_Value) + ")"

        self.Image_Widget = Force_GetMetricWidgetImage # Force_GetMetricWidgetImage # True # False #

        if (cw_remote_duplex_layout):
            self.Visible_Graph_Count = 2
        else:
            self.Visible_Graph_Count = 1

        if ((cw_remote_ini is not None) or Testing_Bypass_Initialization):
            self.Graph_Offset = 0

            Window.bind(on_key_down=self.on_keyboard_down)

            Vertical_Graph_Height_Factor = 0.96

            # Automatically size widget images to fit screen real estate
            horizontal_size, vertical_size = Window.size
            self.Horizontal_Graph_Width = int(round(horizontal_size * 0.98))
            self.Vertical_Graph_Height = vertical_size * Vertical_Graph_Height_Factor
            # print ("h:", horizontal_size, "v:", vertical_size)
            for widget_descriptor in widget_descriptor_list:
                widget_descriptor["width"] = self.Horizontal_Graph_Width
                if (self.Visible_Graph_Count == 2):
                    widget_descriptor["height"] = int(round(self.Vertical_Graph_Height / 2.0))
                else:
                    widget_descriptor["height"] = int(round(self.Vertical_Graph_Height))

            if (not Screen_Manager_App):
                self.CloudWatch_Remote = BoxLayout(orientation='horizontal')

                self.Tab_Bar = Tab_Bar_BoxLayout()
                self.Tab_Bar.bind(on_press_previous=self.on_previous)
                self.Tab_Bar.bind(on_press_next=self.on_next)

                self.Tab_Bar.bind(on_press_simplex=self.on_simplex)
                self.Tab_Bar.bind(on_press_duplex=self.on_duplex)

                self.Tab_Bar.bind(on_press_help=self.on_help)

                self.CloudWatch_Remote_Panel = BoxLayout(orientation='vertical', size_hint=(0.98, 1))

                # Class-based encapsulation
                self.Control_Bar = Control_Bar()
                self.Control_Bar.bind(on_release=self.update_with_parameters)
                self.Control_Bar.size_hint = (1, 0.04)

                self.Graph_Widget_Box =  BoxLayout(orientation='vertical', size_hint=(1, 0.96))

                self.Duplex_Upper_Graph_Box = BoxLayout(orientation='vertical', size_hint=(1, 0.5))
                self.Duplex_Lower_Graph_Box = BoxLayout(orientation='vertical', size_hint=(1, 0.5))

                self.Simplex_Lower_Graph_Box = BoxLayout(orientation='vertical', size_hint=(1, 1))

                if (self.Visible_Graph_Count == 2):
                    self.Graph_Widget_Box.add_widget(self.Duplex_Upper_Graph_Box)
                    self.Graph_Widget_Box.add_widget(self.Duplex_Lower_Graph_Box)

                    self.Visible_Graph_Count = 2

                else:
                    self.Graph_Widget_Box.add_widget(self.Simplex_Lower_Graph_Box)

                    self.Visible_Graph_Count = 1

                self.CloudWatch_Remote_Panel.add_widget(self.Control_Bar)
                self.CloudWatch_Remote_Panel.add_widget(self.Graph_Widget_Box)

                self.CloudWatch_Remote.add_widget(self.Tab_Bar)
                self.CloudWatch_Remote.add_widget(self.CloudWatch_Remote_Panel)

            if (Screen_Manager_App):
                self.CloudWatch_Remote = ScreenManager(transition=NoTransition())

                # Duplex
                self.CloudWatch_Remote_Duplex_Screen = Screen(name="duplex")
                self.CloudWatch_Remote_Duplex = BoxLayout(orientation='horizontal')

                self.Duplex_Tab_Bar = Tab_Bar_BoxLayout()

                self.Duplex_Tab_Bar.bind(on_press_previous=self.on_previous)
                self.Duplex_Tab_Bar.bind(on_press_next=self.on_next)

                self.Duplex_Tab_Bar.bind(on_press_simplex=self.on_simplex)
                self.Duplex_Tab_Bar.bind(on_press_duplex=self.on_duplex)

                self.Duplex_Tab_Bar.bind(on_press_help=self.on_help)

                self.Duplex_CloudWatch_Remote_Panel = BoxLayout(orientation='vertical', size_hint=(0.98, 1))

                # Class-based encapsulation
                self.Duplex_Control_Bar = Control_Bar()
                self.Duplex_Control_Bar.bind(on_release=self.update_with_parameters)
                self.Duplex_Control_Bar.size_hint = (1, 0.04)

                # Simplex
                self.CloudWatch_Remote_Simplex_Screen = Screen(name="simplex")
                self.CloudWatch_Remote_Simplex = BoxLayout(orientation='horizontal')

                self.Simplex_Tab_Bar = Tab_Bar_BoxLayout()

                self.Simplex_Tab_Bar.bind(on_press_previous=self.on_previous)
                self.Simplex_Tab_Bar.bind(on_press_next=self.on_next)

                self.Simplex_Tab_Bar.bind(on_press_simplex=self.on_simplex)
                self.Simplex_Tab_Bar.bind(on_press_duplex=self.on_duplex)

                self.Simplex_Tab_Bar.bind(on_press_help=self.on_help)

                self.Simplex_CloudWatch_Remote_Panel = BoxLayout(orientation='vertical', size_hint=(0.98, 1))

                # Class-based encapsulation
                self.Simplex_Control_Bar = Control_Bar()
                self.Simplex_Control_Bar.bind(on_release=self.update_with_parameters)
                self.Simplex_Control_Bar.size_hint = (1, 0.04)

                # Duplex
                self.Duplex_Upper_Graph_Box = BoxLayout(orientation='vertical', size_hint=(1, 0.48))
                self.Duplex_Lower_Graph_Box = BoxLayout(orientation='vertical', size_hint=(1, 0.48))

                self.Duplex_CloudWatch_Remote_Panel.add_widget(self.Duplex_Upper_Graph_Box)
                self.Duplex_CloudWatch_Remote_Panel.add_widget(self.Duplex_Control_Bar)
                self.Duplex_CloudWatch_Remote_Panel.add_widget(self.Duplex_Lower_Graph_Box)

                self.CloudWatch_Remote_Duplex.add_widget(self.Duplex_Tab_Bar)
                self.CloudWatch_Remote_Duplex.add_widget(self.Duplex_CloudWatch_Remote_Panel)

                self.CloudWatch_Remote_Duplex_Screen.add_widget(self.CloudWatch_Remote_Duplex)
                self.CloudWatch_Remote.add_widget(self.CloudWatch_Remote_Duplex_Screen)

                # Simplex
                self.Simplex_Lower_Graph_Box = BoxLayout(orientation='vertical', size_hint=(1, (2 * 0.48)))

                self.Simplex_CloudWatch_Remote_Panel.add_widget(self.Simplex_Control_Bar)
                self.Simplex_CloudWatch_Remote_Panel.add_widget(self.Simplex_Lower_Graph_Box)

                self.CloudWatch_Remote_Simplex.add_widget(self.Simplex_Tab_Bar)
                self.CloudWatch_Remote_Simplex.add_widget(self.Simplex_CloudWatch_Remote_Panel)

                self.CloudWatch_Remote_Simplex_Screen.add_widget(self.CloudWatch_Remote_Simplex)
                self.CloudWatch_Remote.add_widget(self.CloudWatch_Remote_Simplex_Screen)

            if (cw_remote_refresh_interval_seconds >= 1):
                Clock.schedule_interval(self.update, cw_remote_refresh_interval_seconds)

            return self.CloudWatch_Remote

        else:
            # Can't find initialization file, or it's ill-structured
            self.CloudWatch_Remote = BoxLayout(orientation='vertical')

            cw_remote_initialization_example_label = \
                Label(text="CW_Remote requires an initialization file 'CW_Remote.ini' to function, see example below:", size_hint=(1, 0.03))

            cw_remote_initialization_example_textinput = \
                TextInput(text=cw_remote_initialization_example.rstrip(),
                          multiline=True, readonly=True, allow_copy=True, size_hint=(1, 0.97))

            self.CloudWatch_Remote.add_widget(cw_remote_initialization_example_label)
            self.CloudWatch_Remote.add_widget(cw_remote_initialization_example_textinput)

            return self.CloudWatch_Remote

    def display_period_value_text ( self, Display_Period_Value ):
        period_value_string = ""
        if ((Display_Period_Value // 24) > 0): period_value_string += str(Display_Period_Value // 24) + "D"
        if (((Display_Period_Value % 24) > 0) or (len(period_value_string) == 0)):
            if (len(period_value_string) > 0): period_value_string += " "
            period_value_string += str(Display_Period_Value % 24) + "H"
        return period_value_string

    def update_with_parameters ( self, instance, period_value, period_end_value, *args ):
        # print ("update_params:", period_value, period_end_value)
        self.Period_Value = period_value
        self.Period_End_Value = period_end_value
        self.update()

    def update ( self, *args ):
        self.title = "CW_Remote" + " (" + period_begin_NYC_wall_time(self.Period_Value, self.Period_End_Value) + ")"
        if (cw_remote_ini is not None):
            if (self.Visible_Graph_Count == 2):
                self.Duplex_Upper_Graph_Box.clear_widgets()
                ci_widget_image_list[self.Graph_Offset + 0] = None
                fw_widget_figure_list[self.Graph_Offset + 0] = None

                self.Duplex_Lower_Graph_Box.clear_widgets()
                ci_widget_image_list[self.Graph_Offset + 1] = None
                fw_widget_figure_list[self.Graph_Offset + 1] = None

                self.get_cloudwatch_graph(self.Graph_Offset + 0)
                self.get_cloudwatch_graph(self.Graph_Offset + 1)

                if (self.Image_Widget):
                    self.Duplex_Upper_Graph_Box.add_widget(Image(texture=ci_widget_image_list[self.Graph_Offset + 0].texture))
                    self.Duplex_Lower_Graph_Box.add_widget(Image(texture=ci_widget_image_list[self.Graph_Offset + 0].texture))
                else:
                    self.Duplex_Upper_Graph_Box.add_widget(fw_widget_figure_list[self.Graph_Offset + 0])
                    self.Duplex_Lower_Graph_Box.add_widget(fw_widget_figure_list[self.Graph_Offset + 1])

            elif (self.Visible_Graph_Count == 1):
                self.Simplex_Lower_Graph_Box.clear_widgets()
                ci_widget_image_list[self.Graph_Offset + 0] = None
                fw_widget_figure_list[self.Graph_Offset + 0] = None

                self.get_cloudwatch_graph(self.Graph_Offset + 0)

                if (self.Image_Widget):
                    self.Simplex_Lower_Graph_Box.add_widget(Image(texture=ci_widget_image_list[self.Graph_Offset + 0].texture))
                else:
                    self.Simplex_Lower_Graph_Box.add_widget(fw_widget_figure_list[self.Graph_Offset + 0])

        self.CloudWatch_Remote.canvas.ask_update()

    # Fetch the AWS/CW Dashboard widget images
    def get_cloudwatch_graph ( self, Graph_Index ):
        global widget_descriptor_list, fw_widget_figure_list, ci_widget_image_list

        # print ("graph:", Graph_Index)

        period_value = self.Period_Value
        period_hours_duration = self.Period_Value
        period_end_value = self.Period_End_Value

        if (self.Image_Widget):
            ci_widget_image = ci_widget_image_list[Graph_Index]
            if (ci_widget_image is not None): ci_widget_image.remove_from_cache()

            now_datetime_utc = datetime.datetime.now(UTC_Time_Zone)
            time_zone_offset_string = NYC_Wall_DateTime_Offset(now_datetime_utc)

            widget_descriptor = widget_descriptor_list[Graph_Index]
            widget_descriptor["start"] = "-PT" + str(abs(period_value) + abs(period_end_value)) + "H"
            widget_descriptor["end"] = "-PT" + str(abs(period_end_value)) + "H"

            widget_descriptor["timezone"] = time_zone_offset_string

            if (Testing_Bypass_Initialization_Delay_Seconds == 0):
                response = \
                    cloudwatch_client.get_metric_widget_image(MetricWidget=json.dumps(widget_descriptor),
                                                              OutputFormat="png")

                # Avoid writing the PNG to file, load into the Image widget directly from memory
                data = BytesIO(bytearray(response["MetricWidgetImage"]))
            else:
                # Test code that avoids the aws/cw metrics request/response latency ...
                import io
                import time
                data = io.BytesIO(open(join(script_directory, "kivy-icon-512.png"), "rb").read())
                # ... but allows arbitrary latency to be simulated
                time.sleep(Testing_Bypass_Initialization_Delay_Seconds)
            # Park the coreimage widget for deferred inclusion in UI
            ci_widget_image_list[Graph_Index] = CoreImage(data, ext="png",
                                                          filename=("widget_image_" + str(Graph_Index) + ".png"))

        else: # Figure_Widget
            datetime_now_utc = datetime.datetime.now(UTC_Time_Zone)
            period_end_utc = datetime_now_utc - datetime.timedelta(hours=period_end_value)

            graph_width = self.Horizontal_Graph_Width
            graph_height = self.Vertical_Graph_Height

            if (self.Visible_Graph_Count == 2):
                graph_height = int(round(self.Vertical_Graph_Height / 2.0))
            elif (self.Visible_Graph_Count == 1):
                graph_height = int(round(self.Vertical_Graph_Height))

            metric_statistics_list = \
                Get_Metric_Statistics_Datapoints(Graph_Index, period_end_utc, period_hours_duration)
            metric_figure_widget = \
                Prepare_Get_Metric_Statistics_Figure(metric_statistics_list,
                                                     period_hours_duration, graph_width, graph_height)
            # Park the figure widget for deferred inclusion in UI
            fw_widget_figure_list[Graph_Index] = metric_figure_widget


    def adjust_graph_height ( self ):
        if (self.Visible_Graph_Count == 2):
            for widget_descriptor in widget_descriptor_list:
                widget_descriptor["height"] = int(round(self.Vertical_Graph_Height / 2.0))
        elif (self.Visible_Graph_Count == 1):
            for widget_descriptor in widget_descriptor_list:
                widget_descriptor["height"] = int(round(self.Vertical_Graph_Height))

    def synchronize_control_bar_values ( self, target_control_bar ):
        for destination_child in target_control_bar.children:
            if (destination_child.id == "period_label"):
                destination_child.text = self.display_period_value_text(self.Period_Value)
            elif (destination_child.id == "period_slider"):
                target_control_bar.set_period_value(self.Period_Value)
            elif (destination_child.id == "period_end_slider"):
                target_control_bar.set_period_end_value(self.Period_End_Value)
            elif (destination_child.id == "period_end_label"):
                destination_child.text = self.display_period_value_text(self.Period_End_Value)

    def on_simplex ( self, *args ):
        if (self.Visible_Graph_Count == 2): self.toggle_duplex_versus_simplex()

    def on_duplex ( self, *args ):
        if (self.Visible_Graph_Count == 1): self.toggle_duplex_versus_simplex()

    def toggle_duplex_versus_simplex ( self ):
        if (not Screen_Manager_App):
            if (self.Visible_Graph_Count == 2):
                self.Graph_Widget_Box.clear_widgets()

                self.Visible_Graph_Count = 1
                self.adjust_graph_height()

                self.Graph_Widget_Box.add_widget(self.Simplex_Lower_Graph_Box)

            elif (self.Visible_Graph_Count == 1):
                self.Graph_Widget_Box.clear_widgets()

                self.Visible_Graph_Count = 2
                self.adjust_graph_height()

                self.Graph_Widget_Box.add_widget(self.Duplex_Upper_Graph_Box)
                self.Graph_Widget_Box.add_widget(self.Duplex_Lower_Graph_Box)

            self.update()

        elif (Screen_Manager_App):
            if (self.CloudWatch_Remote.current == "duplex"):
                self.synchronize_control_bar_values(self.Simplex_Control_Bar)
                self.Visible_Graph_Count = 1
                self.adjust_graph_height()
                self.CloudWatch_Remote.current = "simplex"
            elif (self.CloudWatch_Remote.current == "simplex"):
                self.synchronize_control_bar_values(self.Duplex_Control_Bar)
                self.Visible_Graph_Count = 2
                self.adjust_graph_height()
                self.CloudWatch_Remote.current = "duplex"

            self.update()

    def on_previous ( self, *args ):
        if (self.Visible_Graph_Count == 2):
            if ((self.Graph_Offset % 2) == 1):
                # If odd, then 1, 3, 5 ..., move back to even alignment
                self.Graph_Offset -= 1
            elif (self.Graph_Offset > 1):
                self.Graph_Offset -= 2
            else: self.Graph_Offset = 0
        else:
            if (self.Graph_Offset > 0):
                self.Graph_Offset -= 1
            else: self.Graph_Offset = 0
        self.update()

    def on_next ( self, *args ):
        if (self.Visible_Graph_Count == 2):
            if ((self.Graph_Offset + 2) < len(widget_descriptor_list)):
                self.Graph_Offset += 2
            elif ((self.Graph_Offset + 1) < len(widget_descriptor_list)):
                # If at at the end save one graph, move ahead by one for odd alignment
                self.Graph_Offset += 1
        else:
            if ((self.Graph_Offset + 1) < len(widget_descriptor_list)):
                self.Graph_Offset += 1
        self.update()

    def on_help ( self, *args ):
        print ("Help at the highest level")

    def on_keyboard_down ( self, instance, keyboard, keycode, text, modifiers ):
        # print("\nThe key", keycode, "have been pressed")
        # print(" - text is %r" % text)
        # print(" - modifiers are %r" % modifiers)
        if (keycode == 44):
            self.toggle_duplex_versus_simplex()
        elif ((keycode == 81) or (keycode == 79)):
            self.on_next()
        elif ((keycode == 82) or (keycode == 80)):
            self.on_previous()

    def on_start ( self, **kwargs ):
        if (Defer_CWapi_Requests): Clock.schedule_once(self.update, Defer_CWapi_Requests_by_Seconds)
        else: self.update()

# Instantiate and run the kivy app
if __name__ == '__main__':
    CW_Remote().run()
    