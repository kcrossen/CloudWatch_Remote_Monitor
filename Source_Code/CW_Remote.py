#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import kivy
kivy.require('1.10.1')

Initialize_Window_Width = 1280
Initialize_Window_Height = 800

from kivy.config import Config
Config.set('graphics', 'width', str(Initialize_Window_Width))
Config.set('graphics', 'height', str(Initialize_Window_Height))

from kivy.lang.builder import Builder

from kivy.utils import platform as Kivy_Platform

from kivy.app import App

from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image # , AsyncImage

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label

from kivy.uix.textinput import TextInput

from kivy.graphics import Rectangle, Line, Color

from kivy.clock import Clock

from kivy.properties import ListProperty
from kivy.factory import Factory

import os, sys
from os.path import isfile, join, expanduser # dirname
import platform

from io import BytesIO

import datetime, calendar

from collections import OrderedDict

import boto3

import json

import copy

import math

# from functools import partial
# import re

# Example of supporting imported non-library modules
# import sys
# current_script_path = sys.path[0]
#
# sys.path.append(join(current_script_path, "Wall_Time"))
# from Wall_Time import NYC_Wall_DateTime_Offset, UTC_Time_Zone

execution_directory = os.path.abspath(os.path.dirname(sys.argv[0]))
os_platform = platform.system()

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
Initialization_Example_Label_text = \
    "CW_Remote requires an initialization file 'CW_Remote.ini' to function, see example below:"

CW_Remote_Duplex_Layout = True
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

# There can only ever be two graphs at one time
graph_widget_list = [None, None]
graph_plot_metric_statistics_list = [None, None]

path_to_time_slider_cursor = ""
path_to_time_slider_cursor_disabled = ""
path_to_cwremote_screen_image = ""


# import simplejson
#
# def json_serial(obj):
#     """JSON serializer for objects not serializable by default json code"""
#
#     if isinstance(obj, datetime.datetime):
#         serial = obj.isoformat()
#         return serial
#     raise TypeError("Type not serializable")


# Convenience function to bound a value
def bound ( low, high, value ):
    return max(low, min(high, value))


# Local wall time, this works for New York City
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

def Period_Span_NYC_Wall_Time ( Period_Hours, Period_End_Hours_Ago ):
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


# Find json initialization file and image resources
if (os_platform == "Darwin"):
    execution_directory = execution_directory.split("CW_Remote.app")[0]

    def resource_path ( relative_path ):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = execution_directory

        return os.path.join(base_path, relative_path)

    path_to_icon_image = resource_path(os.path.join("data", "cwremote-icon-512.png"))
    path_to_time_slider_cursor = resource_path(os.path.join("data", "time_slider_cursor.png"))
    path_to_time_slider_cursor_disabled = resource_path(os.path.join("data", "time_slider_cursor_disabled.png"))
    path_to_cwremote_screen_image = resource_path(os.path.join("data", "CW_Remote_Screen.png"))

    Config.set('kivy','window_icon', path_to_icon_image)
    Config.write()

    # Initialization_Example_Label_text = path_to_icon_image + ": isfile == " + str(isfile(path_to_icon_image))

    try:
        if (isfile(join(execution_directory, "CW_Remote.ini"))):
            ini_directory = execution_directory
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
        # Fix:
        # import matplotlib
        # matplotlib.use('AGG')

        try:
            # To run from Pydroid 3
            if (isfile(join(execution_directory, "CW_Remote.ini"))):
                ini_directory = execution_directory
            else:
                home_dir = expanduser("~")
                ini_dir = "Documents/CW_Remote"
                ini_directory = join(home_dir, ini_dir)

            path_to_time_slider_cursor = join(ini_directory, "data", "time_slider_cursor.png")
            path_to_time_slider_cursor_disabled = join(ini_directory, "data", "time_slider_cursor_disabled.png")

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

# Apply initialization ...
# ... json has been loaded as nested structure of dictionaries and lists
if (len(cw_remote_ini_json) > 0):
    # This should be the same for any OS platform, ...
    # ... but may still fail by being ill-structured
    try:
        # Load initialization from the JSON ini file
        cw_remote_ini = json.loads(cw_remote_ini_json, object_pairs_hook=OrderedDict)

        cw_remote_layout = cw_remote_ini.get("layout", '')
        if (cw_remote_layout == "paged"): CW_Remote_Duplex_Layout = False
        elif (cw_remote_layout == "duplex"): CW_Remote_Duplex_Layout = True

        cw_api = cw_remote_ini.get("cw_api", "image") # "image" or "statistics"
        if (cw_api == "image"): Force_GetMetricWidgetImage = True

        if ("refresh_interval_seconds" in cw_remote_ini):
            cw_remote_refresh_interval_seconds = cw_remote_ini["refresh_interval_seconds"]
        if (Force_Refresh_Interval_Seconds >= 0):
            cw_remote_refresh_interval_seconds = Force_Refresh_Interval_Seconds
        # Fractional seconds not supported
        cw_remote_refresh_interval_seconds = int(round(cw_remote_refresh_interval_seconds))

        if (Force_Duplex_Layout): CW_Remote_Duplex_Layout = True

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
            CW_Remote_Duplex_Layout = False

        if (CW_Remote_Duplex_Layout):
            # No way to page through these, reduce fetch effort/time
            # widget_descriptor_list = widget_descriptor_list[:2]
            pass
        else:
            # Not duplex, make graphs "higher", i.e. more vertical resolution
            for widget_descr in widget_descriptor_list:
                widget_descr["height"] = 2 * widget_descr["height"]

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


# Functions to plot data graphs with matplotlib ...
# ... the alternative is server-plotted graphs returned as png byte streams
if (not Force_GetMetricWidgetImage):
    import matplotlib
    matplotlib.use('AGG')

    from matplotlib_backend_kivyagg import FigureCanvasKivyAgg as FigureCanvas
    import matplotlib.pyplot as plotter
    from matplotlib.dates import MinuteLocator, HourLocator, DayLocator, DateFormatter

    graph_plot_figure_list = [None, None]

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
    every_twelve_hours = tuple([(12 * hour) for hour in range(24//12)])

    every_five_minutes_labeled = tuple([(5 * minute) for minute in range(60//5) if (minute > 0)])
    every_ten_minutes_labeled = tuple([(10 * minute) for minute in range(60//10) if (minute > 0)])
    every_fifteen_minutes_labeled = tuple([(15 * minute) for minute in range(60//15) if (minute > 0)])
    every_thirty_minutes_labeled = tuple([(30 * minute) for minute in range(60//30) if (minute > 0)])
    every_thirty_minutes = tuple([(30 * minute) for minute in range(60//30)])

    def Prepare_Get_Metric_Statistics_Figure ( Plot_Figure_Index,
                                               Mertric_Statistics_List,
                                               Graph_Width, Graph_Height,
                                               Time_Axis_Limit_Offset_Ratios=(0, 1),
                                               Value_Axis_Limit_Offset_Ratios=(0, 1) ):

        global graph_plot_figure_list

        existing_plot_figure = graph_plot_figure_list[Plot_Figure_Index]
        # Reusing plot_figure leaves accumulated trash from previous plotting, recycle it!
        if (existing_plot_figure is not None): plotter.close(existing_plot_figure)

        plot_figure = plotter.figure(figsize=((Graph_Width / 100), (Graph_Height / 100)), dpi=100)

        line_width = 0.75

        # Trim off real estate wasting margins
        left_trim_ratio = 0.06
        bottom_trim_ratio = 0.13
        right_trim_ratio = 0.94
        top_trim_ratio = 0.98

        axes = plot_figure.gca()
        axis_2 = axes.twinx()

        # Store tuples of (text, text_color) for the two axes
        # There could be none, one, or two
        left_y_axis_labels = []
        right_y_axis_labels = []

        minimum_time = None
        maximum_time = None

        left_axis_minimum_value = None
        left_axis_maximum_value = None

        right_axis_minimum_value = None
        right_axis_maximum_value = None

        require_right_y_axis = False

        for metric_stats in reversed(Mertric_Statistics_List):
            metric_stats_descriptor = metric_stats.get("MetricDescriptor", {})
            metric_stats_datapoints = metric_stats.get("Datapoints", [])
            datapoints_time, datapoints_max, datapoints_avg = \
                Metric_Statistics_Datapoints_Time_and_Values(metric_stats_datapoints,
                                                             metric_stats_descriptor.get("YFactor", 1))

            if ((minimum_time is None) and (maximum_time is None)):
                # cpu_time is sorted, so this can work
                minimum_time = datapoints_time[0]
                maximum_time = datapoints_time[-1]
            else:
                # cpu_time is sorted, so this can work
                minimum_time = min(minimum_time, datapoints_time[0])
                maximum_time = max(maximum_time, datapoints_time[-1])

            line_color = metric_stats_descriptor.get("Color", [0, 0, 0])

            this_y_axis_label = (metric_stats_descriptor.get("MetricLabel", " "),
                                 tuple(metric_stats_descriptor.get("LabelColor", line_color)))
            y_axis = metric_stats_descriptor.get("YAxis", "left")
            if (y_axis == "left"):
                left_y_axis_labels.append(this_y_axis_label)
                this_axis = axes

                if ((left_axis_minimum_value is None) and (left_axis_maximum_value is None)):
                    left_axis_minimum_value = min(datapoints_max)
                    left_axis_maximum_value = max(datapoints_max)
                else:
                    left_axis_minimum_value = min(left_axis_minimum_value, min(datapoints_max))
                    left_axis_maximum_value = max(left_axis_maximum_value, max(datapoints_max))
            else:
                right_y_axis_labels.append(this_y_axis_label)
                this_axis = axis_2
                require_right_y_axis = True

                if ((right_axis_minimum_value is None) and (right_axis_maximum_value is None)):
                    right_axis_minimum_value = min(datapoints_max)
                    right_axis_maximum_value = max(datapoints_max)
                else:
                    right_axis_minimum_value = min(right_axis_minimum_value, min(datapoints_max))
                    right_axis_maximum_value = max(right_axis_maximum_value, max(datapoints_max))

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

        # Potentially adjust time scale to zoom ...
        minimum_time_offset_ratio, maximum_time_offset_ratio = Time_Axis_Limit_Offset_Ratios
        minimum_time_offset_ratio = \
            max((minimum_time_offset_ratio - left_trim_ratio) / (right_trim_ratio - left_trim_ratio), 0)
        maximum_time_offset_ratio = \
            min((maximum_time_offset_ratio - left_trim_ratio) / (right_trim_ratio - left_trim_ratio), 1)

        if (not ((minimum_time_offset_ratio == 0) and (maximum_time_offset_ratio == 1))):
            delta_time_seconds = (maximum_time - minimum_time).total_seconds()
            maximum_time = minimum_time + datetime.timedelta(seconds=(delta_time_seconds * maximum_time_offset_ratio))
            # MUST calculate maximum_time BEFORE minimum_time, otherwise minimum_time is "corrupted"
            minimum_time = minimum_time + datetime.timedelta(seconds=(delta_time_seconds * minimum_time_offset_ratio))
        # ... Potentially adjust time scale to zoom

        axes.set_xlim(minimum_time, maximum_time)

        # Potentially adjust value scale to zoom ...
        minimum_value_offset_ratio, maximum_value_offset_ratio = Value_Axis_Limit_Offset_Ratios
        minimum_value_offset_ratio = \
            max((minimum_value_offset_ratio - bottom_trim_ratio) / (top_trim_ratio - bottom_trim_ratio), 0)
        maximum_value_offset_ratio = \
            min((maximum_value_offset_ratio - bottom_trim_ratio) / (top_trim_ratio - bottom_trim_ratio), 1)

        if (not ((minimum_value_offset_ratio == 0) and (maximum_value_offset_ratio == 1))):
            left_delta_value = left_axis_maximum_value - left_axis_minimum_value
            left_axis_maximum_value = left_axis_minimum_value + (left_delta_value * maximum_value_offset_ratio)
            # MUST calculate maximum_value BEFORE minimum_value, otherwise minimum_value is "corrupted"
            left_axis_minimum_value = left_axis_minimum_value + (left_delta_value * minimum_value_offset_ratio)
        # ... Potentially adjust value scale to zoom

        axes.set_ylim(left_axis_minimum_value, left_axis_maximum_value)

        if (require_right_y_axis):
            # Potentially adjust value scale to zoom ...
            if (not ((minimum_value_offset_ratio == 0) and (maximum_value_offset_ratio == 1))):
                right_delta_value = right_axis_maximum_value - right_axis_minimum_value
                right_axis_maximum_value = right_axis_minimum_value + (right_delta_value * maximum_value_offset_ratio)
                # MUST calculate maximum_value BEFORE minimum_value, otherwise minimum_value is "corrupted"
                right_axis_minimum_value = right_axis_minimum_value + (right_delta_value * minimum_value_offset_ratio)
            # ... Potentially adjust value scale to zoom

            axis_2.set_ylim(right_axis_minimum_value, right_axis_maximum_value)

        # Attempt optimum x axis (date/time) tic labeling, complicated, heuristic
        major_minor_formatter = "hour"

        time_axis_hours = int(round((maximum_time - minimum_time).total_seconds() / (60 * 60)))

        # Adaptive time axis tics and tic labels
        if ((time_axis_hours >= 1) and (time_axis_hours < 3)):
            axes.xaxis.set_major_locator(HourLocator(every_hour))
            axes.xaxis.set_minor_locator(MinuteLocator(every_five_minutes_labeled))
            major_minor_formatter = "hour/minute"
        elif ((time_axis_hours >= 3) and (time_axis_hours < 6)):
            axes.xaxis.set_major_locator(HourLocator(every_hour))
            axes.xaxis.set_minor_locator(MinuteLocator(every_ten_minutes_labeled))
            major_minor_formatter = "hour/minute"
        elif ((time_axis_hours >= 6) and (time_axis_hours < 8)):
            axes.xaxis.set_major_locator(HourLocator(every_hour))
            axes.xaxis.set_minor_locator(MinuteLocator(every_fifteen_minutes_labeled))
            major_minor_formatter = "hour/minute"
        elif ((time_axis_hours >= 8) and (time_axis_hours < 16)):
            axes.xaxis.set_major_locator(HourLocator(every_hour))
            axes.xaxis.set_minor_locator(MinuteLocator(every_thirty_minutes_labeled))
            major_minor_formatter = "hour/minute"
        elif ((time_axis_hours >= 16) and (time_axis_hours < 24)):
            axes.xaxis.set_major_locator(HourLocator(every_hour))
            axes.xaxis.set_minor_locator(MinuteLocator(every_thirty_minutes))

        elif ((time_axis_hours >= 24) and (time_axis_hours < (24 + 12))):
            axes.xaxis.set_major_locator(HourLocator(every_two_hours))
            axes.xaxis.set_minor_locator(HourLocator(every_hour))

        elif ((time_axis_hours >= (24 + 12)) and (time_axis_hours < (48 + 12))):
            axes.xaxis.set_major_locator(HourLocator(every_three_hours))
            axes.xaxis.set_minor_locator(HourLocator(every_hour))

        elif ((time_axis_hours >= (48 + 12)) and (time_axis_hours < (72 + 12))):
            axes.xaxis.set_major_locator(HourLocator(every_four_hours))
            axes.xaxis.set_minor_locator(HourLocator(every_hour))

        elif ((time_axis_hours >= (72 + 12)) and (time_axis_hours < (96 + 12))):
            axes.xaxis.set_major_locator(HourLocator(every_six_hours))
            axes.xaxis.set_minor_locator(HourLocator(every_three_hours))

        elif ((time_axis_hours >= (96 + 12)) and (time_axis_hours < (120 + 12))):
            axes.xaxis.set_major_locator(HourLocator(every_twelve_hours))
            axes.xaxis.set_minor_locator(HourLocator(every_six_hours))

        elif ((time_axis_hours >= (120 + 12)) and (time_axis_hours < (144 + 12))):
            axes.xaxis.set_major_locator(DayLocator(every_day))
            axes.xaxis.set_minor_locator(HourLocator(every_four_hours))
            major_minor_formatter = "day"

        elif ((time_axis_hours >= (144 + 12)) and (time_axis_hours < (168 + 12))):
            axes.xaxis.set_major_locator(DayLocator(every_day))
            axes.xaxis.set_minor_locator(HourLocator(every_six_hours))
            major_minor_formatter = "day"

        if (major_minor_formatter == "hour/minute"):
            axes.xaxis.set_major_formatter(DateFormatter("%H:00\n%m/%d"))
            axes.xaxis.set_minor_formatter(DateFormatter("%M"))
        elif (major_minor_formatter == "hour"):
                axes.xaxis.set_major_formatter(DateFormatter("%H:00\n%m/%d"))
        elif (major_minor_formatter == "day"):
            axes.xaxis.set_major_formatter(DateFormatter("%H:00\n%m/%d"))

        plotter.setp(axes.get_xticklabels(), rotation=0, ha="center")

        axes.grid(True)

        # Trim off real estate wasting margins
        plotter.subplots_adjust(left=left_trim_ratio, bottom=bottom_trim_ratio,
                                right=right_trim_ratio, top=top_trim_ratio, wspace=0, hspace=0)

        canvas = FigureCanvas(plot_figure)
        canvas.draw()

        graph_plot_figure_list[Plot_Figure_Index] = plot_figure

        return canvas


# Since this is a "static" widget, it's more convenient to create as kv
Builder.load_string(
"""
<VerticalTabBarBoxLayout>:
    orientation: 'vertical'
    
    canvas:
        Color:
            rgba: 0.75, 0.95, 1, 1
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

class VerticalTabBarBoxLayout ( BoxLayout ):

    def __init__(self, **kwargs):
        super(VerticalTabBarBoxLayout, self).__init__(**kwargs)
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
class SliderExtended ( Slider ):
    def __init__(self, **kwargs):
        self.register_event_type('on_release')
        super(SliderExtended, self).__init__(**kwargs)

    def on_release ( self ):
        pass
    # Because there appears to be no event for touch_up, ...
    # ... override on_touch_up and create a custom event
    def on_touch_up ( self, touch ):
        super(SliderExtended, self).on_touch_up(touch)
        if (touch.grab_current == self):
            self.dispatch('on_release')
            return True

# Since this is a relatively complicated "dynamic" widget, ...
# ... it's more convenient to render as Python code.
class TimeSpanControlBar ( BoxLayout ):

    Period_Duration_Steps = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24,  # 18
                             26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48,  # 12
                             50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72,  # 12
                             74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 96,  # 12
                             100, 104, 108, 112, 116, 120,  # 6
                             124, 128, 132, 136, 140, 144,  # 6
                             148, 152, 156, 160, 164, 168]  # 6

    Period_Hours_Ago_Steps = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24,  # 19
                              26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48,  # 12
                              50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72,  # 12
                              74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 96,  # 12
                              100, 104, 108, 112, 116, 120,  # 6
                              124, 128, 132, 136, 140, 144,  # 6
                              148, 152, 156, 160, 164, 168]  # 6

    def __init__(self, **kwargs):
        self.register_event_type('on_release')

        self._period_duration_hours = 24
        self._period_end_hours_ago = 0

        slider_minimum_value = -1000

        period_duration_slider_maximum_value = -1
        self.period_duration_slider_value_span = period_duration_slider_maximum_value - slider_minimum_value

        period_end_slider_maximum_value = 0
        self.period_end_slider_value_span = period_end_slider_maximum_value - slider_minimum_value

        super(TimeSpanControlBar, self).__init__(**kwargs)

        self.period_duration_label = Label(text="proxy", size_hint=(0.075, 1))

        self.period_duration_slider = \
            SliderExtended(cursor_image=path_to_time_slider_cursor,
                           cursor_disabled_image=path_to_time_slider_cursor_disabled,
                           cursor_height=28,
                           border_horizontal=[0, 0, 0, 0], padding=12,
                           min=slider_minimum_value, max=period_duration_slider_maximum_value,
                           value=period_duration_slider_maximum_value, step=1, size_hint=(0.4, 1))
        self.period_duration_slider.bind(value=self._on_period_duration_value_change)
        self.period_duration_slider.bind(on_release=self._trigger_on_release)

        refresh_button = Button(text="Refresh", size_hint=(0.05, 1))
        refresh_button.font_size = 14
        refresh_button.bind(on_press=self._trigger_on_release)

        self.period_end_slider = \
            SliderExtended(cursor_image=path_to_time_slider_cursor,
                           cursor_disabled_image=path_to_time_slider_cursor_disabled,
                           cursor_height=28,
                           border_horizontal=[0, 0, 0, 0], padding=12,
                           min=slider_minimum_value, max=period_end_slider_maximum_value,
                           value=period_end_slider_maximum_value, step=1, size_hint=(0.4, 1))
        self.period_end_slider.bind(value=self._on_period_end_value_change)
        self.period_end_slider.bind(on_release=self._trigger_on_release)

        self.period_end_label = Label(text="proxy", size_hint=(0.075, 1))

        self.add_widget(self.period_duration_label)
        self.add_widget(self.period_duration_slider)

        self.add_widget(refresh_button)

        self.add_widget(self.period_end_slider)
        self.add_widget(self.period_end_label)

        self.set_period_duration_value(self._period_duration_hours)
        self.set_period_end_value(self._period_end_hours_ago)

    # Public functions (used to synchronize multiple TimeSpanControlBars) ...
    def set_period_duration_value ( self, period_duration_value, *args ):
        self._period_duration_hours = period_duration_value
        self.period_duration_label.text = (self._period_value_display(self._period_duration_hours))
        self.period_duration_slider.value = -(self.period_duration_slider_value_span *
                                              (self.Period_Duration_Steps.index(self._period_duration_hours) /
                                               len(self.Period_Duration_Steps)))

    def set_period_end_value ( self, period_end_value, *args ):
        self._period_end_hours_ago = period_end_value
        self.period_end_slider.value = -(self.period_end_slider_value_span *
                                         (self.Period_Hours_Ago_Steps.index(self._period_end_hours_ago) /
                                          len(self.Period_Hours_Ago_Steps)))
        self.period_end_label.text = (self._period_value_display(self._period_end_hours_ago) + " ago")
    # ... Public functions  (used to synchronize multiple TimeSpanControlBars)

    # Private functions ...
    def _period_value_display ( self, Period_Value ):
        period_value_string = ""
        if ((Period_Value // 24) > 0): period_value_string += str(Period_Value // 24) + "D"
        if (((Period_Value % 24) > 0) or (len(period_value_string) == 0)):
            if (len(period_value_string) > 0): period_value_string += " "
            period_value_string += str(Period_Value % 24) + "H"
        return period_value_string

    def _on_period_duration_value_change ( self, instance, period_duration_slider_value, *args ):
        # print (period_duration_slider_value)
        period_value_index = \
            int(round(len(self.Period_Duration_Steps) *
                      (abs(period_duration_slider_value) / self.period_duration_slider_value_span)))
        self._period_duration_hours = \
            self.Period_Duration_Steps[bound(0, (len(self.Period_Duration_Steps) - 1), period_value_index)]
        self.period_duration_label.text = (self._period_value_display(self._period_duration_hours))
        # print (period_duration_slider_value, period_value_index, self._period_duration_hours, self.period_duration_label.text)
        return True

    def _on_period_end_value_change ( self, instance, period_end_slider_value, *args ):
        period_end_value_index = \
            int(round(len(self.Period_Hours_Ago_Steps) *
                      (abs(period_end_slider_value) / self.period_end_slider_value_span)))
        self._period_end_hours_ago = \
            self.Period_Hours_Ago_Steps[bound(0, (len(self.Period_Hours_Ago_Steps) -1), period_end_value_index)]
        self.period_end_label.text = (self._period_value_display(self._period_end_hours_ago) + " ago")
        return True
    # ... Private functions

    # Proxy for public event
    def on_release(self, *args):
        pass

    # Private function
    def _trigger_on_release ( self, *args ):
        self.dispatch('on_release', self._period_duration_hours, self._period_end_hours_ago)
        return True


Builder.load_string("""
<LabelExtended>:
  background_color: 1, 1, 1, 1
  canvas.before:
    Color:
      rgba: self.background_color
    Rectangle:
      pos: self.pos
      size: self.size
""")

class LabelExtended(Label):
    background_color = ListProperty([1, 1, 1, 1])

Factory.register('KivyExtended', module='LabelExtended')


class GridLayoutExtended ( GridLayout ):
    def __init__(self, **kwargs):
        # Gotta be able to do its business
        super(GridLayoutExtended, self).__init__(**kwargs)

        with self.canvas.before:
            Color(1, 0, 0, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


def Build_Help_GridLayout ( on_help_escape_callback ):
    cloudwatch_remote_help = \
        GridLayoutExtended(cols=1, padding=[2, 2, 0, 2], spacing=0,
                           size_hint=(None, None), width=Initialize_Window_Width)

    cwremote_screen_image = \
        Image(source=path_to_cwremote_screen_image,
              size=((Initialize_Window_Width - 4), 815), size_hint=(None, None))
    cloudwatch_remote_help.add_widget(cwremote_screen_image)

    help_escape_button = Button(text="Return to graphs", bold=True,
                                background_color=[1, 0, 0, 1],
                                size=((Initialize_Window_Width - 4), 28), size_hint=(None, None))
    help_escape_button.bind(on_press=on_help_escape_callback)
    cloudwatch_remote_help.add_widget(help_escape_button)

    CW_Remote_Help_Text_Paragraphs = [
        "The red '[b][color=ff0000]A[/color][/b]' marks the slider that adjusts the duration of the period for which the graphed data will appear. " +
        "It can adjust from 1 hour to 7 days (168 hours). " +
        "The label to the left of the this slider displays the current period duration in days and hours. " +
        "This slider is logarithmic, it is increasingly sensitive toward the right end of the scale. ",

        "The red '[b][color=ff0000]B[/color][/b]' marks the slider that adjusts the hours before now that the graphed period ends. " +
        "It can adjust from 0 hours to 7 days (168 hours). " +
        "The label to the right of the this slider displays the days and hours before now that the graphed period ends. " +
        "This slider is logarithmic, it is increasingly sensitive toward the right end of the scale. "
    ]

    # Add help text paragraphs to grid.
    for help_text_paragraph in CW_Remote_Help_Text_Paragraphs:
        help_txt_para = LabelExtended(text=help_text_paragraph, markup=True, text_size=(1272, None),
                                      color=[0, 0, 0, 1], padding_x=2,
                                      width=(Initialize_Window_Width - 4), size_hint=(None, None))
        help_txt_para.height = math.ceil(len(help_text_paragraph) * (1.33 / 255)) * 25
        cloudwatch_remote_help.add_widget(help_txt_para)

        cloudwatch_remote_help.bind(minimum_height=cloudwatch_remote_help.setter('height'))

    return cloudwatch_remote_help


# Build the app screen
class CW_Remote ( App ):

    def build ( self ):
        self.title = "CW_Remote"

        self.Period_Duration_Hours = 24
        self.Period_End_Hours_Ago = 0

        self.Image_Widget = Force_GetMetricWidgetImage # Force_GetMetricWidgetImage # True # False #

        if (CW_Remote_Duplex_Layout):
            self.Visible_Graph_Count = 2
        else:
            self.Visible_Graph_Count = 1

        if ((cw_remote_ini is not None) or Testing_Bypass_Initialization):
            self.Graph_Offset = 0

            self.clear_touch()

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

            # Build the App UI two different ways, with screen manager ...
            # ... and by "swapping" widgets to achieve similar effect.
            # Via the screen manager, the two different data views, simplex and duplex ...
            # ... can have the visible TimeSpanControlBar in two different locations.
            # By the "swapping" widgets method, that's harder to achieve.
            # Ordinarily, pick one or the other, but this is a tutorial of sorts.
            if (not Screen_Manager_App):
                self.CloudWatch_Remote = BoxLayout(orientation='horizontal')

                self.Tab_Bar = VerticalTabBarBoxLayout()
                self.Tab_Bar.bind(on_press_previous=self.on_previous)
                self.Tab_Bar.bind(on_press_next=self.on_next)

                self.Tab_Bar.bind(on_press_simplex=self.on_simplex)
                self.Tab_Bar.bind(on_press_duplex=self.on_duplex)

                self.Tab_Bar.bind(on_press_help=self.on_help)

                self.CloudWatch_Remote_Panel = BoxLayout(orientation='vertical', size_hint=(0.98, 1))

                self.TimeSpanControlBar = TimeSpanControlBar()
                self.TimeSpanControlBar.bind(on_release=self.update_with_parameters)
                self.TimeSpanControlBar.size_hint = (1, 0.04)

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

                self.CloudWatch_Remote_Panel.add_widget(self.TimeSpanControlBar)
                self.CloudWatch_Remote_Panel.add_widget(self.Graph_Widget_Box)

                self.CloudWatch_Remote.add_widget(self.Tab_Bar)
                self.CloudWatch_Remote.add_widget(self.CloudWatch_Remote_Panel)

            elif (Screen_Manager_App): # Redundant explicit test is note-to-self
                self.CloudWatch_Remote = ScreenManager(transition=NoTransition())

                # Duplex
                self.CloudWatch_Remote_Duplex_Screen = Screen(name="duplex")
                self.CloudWatch_Remote_Duplex = BoxLayout(orientation='horizontal')

                self.Duplex_Tab_Bar = VerticalTabBarBoxLayout()

                self.Duplex_Tab_Bar.bind(on_press_previous=self.on_previous)
                self.Duplex_Tab_Bar.bind(on_press_next=self.on_next)

                self.Duplex_Tab_Bar.bind(on_press_simplex=self.on_simplex)
                self.Duplex_Tab_Bar.bind(on_press_duplex=self.on_duplex)

                self.Duplex_Tab_Bar.bind(on_press_help=self.on_help)

                self.Duplex_CloudWatch_Remote_Panel = BoxLayout(orientation='vertical', size_hint=(0.98, 1))

                self.Duplex_TimeSpanControlBar = TimeSpanControlBar()
                self.Duplex_TimeSpanControlBar.bind(on_release=self.update_with_parameters)
                self.Duplex_TimeSpanControlBar.size_hint = (1, 0.04)

                # Simplex
                self.CloudWatch_Remote_Simplex_Screen = Screen(name="simplex")
                self.CloudWatch_Remote_Simplex = BoxLayout(orientation='horizontal')

                self.Simplex_Tab_Bar = VerticalTabBarBoxLayout()

                self.Simplex_Tab_Bar.bind(on_press_previous=self.on_previous)
                self.Simplex_Tab_Bar.bind(on_press_next=self.on_next)

                self.Simplex_Tab_Bar.bind(on_press_simplex=self.on_simplex)
                self.Simplex_Tab_Bar.bind(on_press_duplex=self.on_duplex)

                self.Simplex_Tab_Bar.bind(on_press_help=self.on_help)

                self.Simplex_CloudWatch_Remote_Panel = BoxLayout(orientation='vertical', size_hint=(0.98, 1))

                self.Simplex_TimeSpanControlBar = TimeSpanControlBar()
                self.Simplex_TimeSpanControlBar.bind(on_release=self.update_with_parameters)
                self.Simplex_TimeSpanControlBar.size_hint = (1, 0.04)

                # Duplex duplex screen
                self.Duplex_Upper_Graph_Box = BoxLayout(id="Duplex_Upper_Graph_Box", orientation='vertical', size_hint=(1, 0.48))
                self.Duplex_Upper_Graph_Box.bind(on_touch_down=self.on_touch_down)
                self.Duplex_Upper_Graph_Box.bind(on_touch_move=self.on_touch_move)
                self.Duplex_Upper_Graph_Box.bind(on_touch_up=self.on_touch_up)

                self.Duplex_Lower_Graph_Box = BoxLayout(id="Duplex_Lower_Graph_Box", orientation='vertical', size_hint=(1, 0.48))
                self.Duplex_Lower_Graph_Box.bind(on_touch_down=self.on_touch_down)
                self.Duplex_Lower_Graph_Box.bind(on_touch_move=self.on_touch_move)
                self.Duplex_Lower_Graph_Box.bind(on_touch_up=self.on_touch_up)

                self.Duplex_CloudWatch_Remote_Panel.add_widget(self.Duplex_Upper_Graph_Box)
                self.Duplex_CloudWatch_Remote_Panel.add_widget(self.Duplex_TimeSpanControlBar)
                self.Duplex_CloudWatch_Remote_Panel.add_widget(self.Duplex_Lower_Graph_Box)

                self.CloudWatch_Remote_Duplex.add_widget(self.Duplex_Tab_Bar)
                self.CloudWatch_Remote_Duplex.add_widget(self.Duplex_CloudWatch_Remote_Panel)

                self.CloudWatch_Remote_Duplex_Screen.add_widget(self.CloudWatch_Remote_Duplex)
                self.CloudWatch_Remote.add_widget(self.CloudWatch_Remote_Duplex_Screen)

                # Simplex screen
                self.Simplex_Lower_Graph_Box = BoxLayout(id="Simplex_Lower_Graph_Box", orientation='vertical', size_hint=(1, (2 * 0.48)))
                self.Simplex_Lower_Graph_Box.bind(on_touch_down=self.on_touch_down)
                self.Simplex_Lower_Graph_Box.bind(on_touch_move=self.on_touch_move)
                self.Simplex_Lower_Graph_Box.bind(on_touch_up=self.on_touch_up)

                self.Simplex_CloudWatch_Remote_Panel.add_widget(self.Simplex_TimeSpanControlBar)
                self.Simplex_CloudWatch_Remote_Panel.add_widget(self.Simplex_Lower_Graph_Box)

                self.CloudWatch_Remote_Simplex.add_widget(self.Simplex_Tab_Bar)
                self.CloudWatch_Remote_Simplex.add_widget(self.Simplex_CloudWatch_Remote_Panel)

                self.CloudWatch_Remote_Simplex_Screen.add_widget(self.CloudWatch_Remote_Simplex)
                self.CloudWatch_Remote.add_widget(self.CloudWatch_Remote_Simplex_Screen)

                # Help screen
                self.CloudWatch_Remote_Help_Screen = Screen(name="help")

                self.CloudWatch_Remote_Help = Build_Help_GridLayout(self.on_help_escape)

                self.CloudWatch_Remote_Help_ScrollView = \
                    ScrollView(size_hint=(None, None), size=(Initialize_Window_Width, Initialize_Window_Height),
                               bar_width=5, bar_color=[1, 0, 0, 0.5], bar_inactive_color=[1, 0, 0, 0.2],
                               do_scroll_x=False)
                self.CloudWatch_Remote_Help_ScrollView.add_widget(self.CloudWatch_Remote_Help)

                self.CloudWatch_Remote_Help_Screen.add_widget(self.CloudWatch_Remote_Help_ScrollView)
                self.CloudWatch_Remote.add_widget(self.CloudWatch_Remote_Help_Screen)

            if (cw_remote_refresh_interval_seconds >= 1):
                Clock.schedule_interval(self.update, cw_remote_refresh_interval_seconds)

            return self.CloudWatch_Remote

        else:
            # Can't find json initialization file, or it's ill-structured
            self.CloudWatch_Remote = BoxLayout(orientation='vertical')

            cw_remote_initialization_example_label = \
                Label(text=Initialization_Example_Label_text, size_hint=(1, 0.03))

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
        if ((period_value == self.Period_Duration_Hours) and
            (period_end_value == self.Period_End_Hours_Ago)): return True
        # Don't bother with update if values haven't changed
        self.Period_Duration_Hours = period_value
        self.Period_End_Hours_Ago = period_end_value
        self.force_update()

    def force_update ( self, *args ):
        self.clear_touch()
        self.update()

    def update ( self, *args ):
        # Only "scheduled" updates arrive directly here, ignore if currently zoomed
        if (self.Touch_Down_Instance_Id is not None): return True

        self.title = "CW_Remote" + " (" + Period_Span_NYC_Wall_Time(self.Period_Duration_Hours,
                                                                     self.Period_End_Hours_Ago) + ")"
        if (cw_remote_ini is not None):
            if (self.Visible_Graph_Count == 2):
                self.Duplex_Upper_Graph_Box.clear_widgets()
                self.Duplex_Lower_Graph_Box.clear_widgets()

                self.get_cloudwatch_graph(self.Graph_Offset + 0)
                self.get_cloudwatch_graph(self.Graph_Offset + 1)

                if (self.Image_Widget):
                    self.Duplex_Upper_Graph_Box.add_widget(Image(texture=graph_widget_list[0].texture))
                    self.Duplex_Lower_Graph_Box.add_widget(Image(texture=graph_widget_list[1].texture))
                else:
                    self.Duplex_Upper_Graph_Box.add_widget(graph_widget_list[0])
                    self.Duplex_Lower_Graph_Box.add_widget(graph_widget_list[1])

            elif (self.Visible_Graph_Count == 1):
                self.Simplex_Lower_Graph_Box.clear_widgets()

                self.get_cloudwatch_graph(self.Graph_Offset + 0)

                if (self.Image_Widget):
                    self.Simplex_Lower_Graph_Box.add_widget(Image(texture=graph_widget_list[0].texture))
                else:
                    self.Simplex_Lower_Graph_Box.add_widget(graph_widget_list[0])

        self.CloudWatch_Remote.canvas.ask_update()
        return True

    # Fetch the AWS/CW Dashboard widget images
    def get_cloudwatch_graph ( self, Graph_Index ):
        global widget_descriptor_list
        global graph_plot_metric_statistics_list
        global graph_widget_list

        graph_widget_list_index = Graph_Index - self.Graph_Offset

        if (self.Image_Widget):
            ci_widget_image = graph_widget_list[graph_widget_list_index]
            if (ci_widget_image is not None): ci_widget_image.remove_from_cache()
            graph_widget_list[graph_widget_list_index] = None

            now_datetime_utc = datetime.datetime.now(UTC_Time_Zone)
            time_zone_offset_string = NYC_Wall_DateTime_Offset(now_datetime_utc)

            widget_descriptor = widget_descriptor_list[Graph_Index]
            widget_descriptor["start"] = "-PT" + str(abs(self.Period_Duration_Hours) +
                                                     abs(self.Period_End_Hours_Ago)) + "H"
            widget_descriptor["end"] = "-PT" + str(abs(self.Period_End_Hours_Ago)) + "H"

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
                data = io.BytesIO(open(join(execution_directory, "kivy-icon-512.png"), "rb").read())
                # ... but allows arbitrary latency to be simulated
                time.sleep(Testing_Bypass_Initialization_Delay_Seconds)
            # Park the coreimage widget for deferred inclusion in UI
            graph_widget_list[graph_widget_list_index] = \
                CoreImage(data, ext="png", filename=("widget_image_" + str(Graph_Index) + ".png"))

        else: # Figure_Widget
            graph_widget_list[graph_widget_list_index] = None
            graph_plot_metric_statistics_list[graph_widget_list_index] = None

            datetime_now_utc = datetime.datetime.now(UTC_Time_Zone)
            period_end_utc = datetime_now_utc - datetime.timedelta(hours=self.Period_End_Hours_Ago)

            graph_width = self.Horizontal_Graph_Width
            graph_height = self.Vertical_Graph_Height

            if (self.Visible_Graph_Count == 2):
                graph_height = int(round(self.Vertical_Graph_Height / 2.0))
            elif (self.Visible_Graph_Count == 1):
                graph_height = int(round(self.Vertical_Graph_Height))

            metric_statistics_list = \
                Get_Metric_Statistics_Datapoints(Graph_Index, period_end_utc, self.Period_Duration_Hours)

            # Preserve for potential zoom
            graph_plot_metric_statistics_list[graph_widget_list_index] = metric_statistics_list

            metric_figure_widget = \
                Prepare_Get_Metric_Statistics_Figure(graph_widget_list_index,
                                                     metric_statistics_list,
                                                     graph_width, graph_height)

            # Park the figure widget for deferred inclusion in UI
            graph_widget_list[graph_widget_list_index] = metric_figure_widget

    def zoom_cloudwatch_graph ( self, Widget_List_Index,
                                Time_Axis_Zoom_Offset_Ratios=(0, 1), Value_AxisZoom_Offset_Ratios=(0, 1) ):
        global graph_plot_metric_statistics_list
        global graph_widget_list

        graph_widget_list_index = Widget_List_Index

        # Figure_Widget
        graph_widget_list[graph_widget_list_index] = None

        graph_width = self.Horizontal_Graph_Width
        graph_height = self.Vertical_Graph_Height

        if (self.Visible_Graph_Count == 2):
            graph_height = int(round(self.Vertical_Graph_Height / 2.0))
        elif (self.Visible_Graph_Count == 1):
            graph_height = int(round(self.Vertical_Graph_Height))

        # Preserve for potential zoom
        metric_statistics_list = graph_plot_metric_statistics_list[graph_widget_list_index]

        metric_figure_widget = \
            Prepare_Get_Metric_Statistics_Figure(graph_widget_list_index,
                                                 metric_statistics_list,
                                                 graph_width, graph_height,
                                                 Time_Axis_Limit_Offset_Ratios=Time_Axis_Zoom_Offset_Ratios,
                                                 Value_Axis_Limit_Offset_Ratios=Value_AxisZoom_Offset_Ratios)

        # Park the figure widget for deferred inclusion in UI
        graph_widget_list[graph_widget_list_index] = metric_figure_widget


    def on_touch_down ( self, instance, touch, *args ):
        if ((not instance.collide_point(touch.x, touch.y)) or
            # Only plots can be zoomed, images cannot
            (self.Image_Widget)): return False

        self.Touch_Down_X = touch.x
        self.Touch_Down_Y = touch.y

        instance_left, instance_bottom = instance.pos
        self.Touch_Down_Ratio_Horizontal = bound(0, 1, ((touch.x - instance_left) / instance.width))
        self.Touch_Down_Ratio_Vertical = bound(0, 1, ((touch.y - instance_bottom) / instance.height))

        self.Touch_Down_Instance_Id = instance.id
        if (instance.id == "Duplex_Upper_Graph_Box"):
            self.Touch_Down_Index = 0
        elif (instance.id == "Duplex_Lower_Graph_Box"):
            self.Touch_Down_Index = 1
        elif (instance.id == "Simplex_Lower_Graph_Box"):
            self.Touch_Down_Index = 0
        else:
            self.Touch_Down_Instance_Id = None
            self.Touch_Down_Index = None

        if (self.Touch_Down_Instance_Id is not None):
            with instance.canvas:
                Color(0, 0, 0, .5, mode='rgba')
                self.line = Line(points=(touch.x, touch.y, self.Touch_Down_X, touch.y,
                                         self.Touch_Down_X, self.Touch_Down_Y, touch.x, self.Touch_Down_Y,
                                         touch.x, touch.y),
                                 width=1)
            instance.canvas.ask_update()

        return True

    def on_touch_move ( self, instance, touch, *args ):
        if ((not instance.collide_point(touch.x, touch.y)) or
            # Only plots can be zoomed, images cannot
            (self.Image_Widget)): return False

        # Exit if no touch down or incomplete touch down recorded
        if ((self.Touch_Down_Instance_Id is None) or
            (self.Touch_Down_Index is None) or
            (self.Touch_Down_Ratio_Horizontal is None) or
            (self.Touch_Down_Ratio_Vertical is None)): return False

        # Exit if inconsistent touch down recorded
        if (not (instance.id == self.Touch_Down_Instance_Id)): return False
        if (not (((instance.id == "Duplex_Upper_Graph_Box") and (self.Touch_Down_Index == 0)) or
                 ((instance.id == "Duplex_Lower_Graph_Box") and (self.Touch_Down_Index == 1)) or
                 ((instance.id == "Simplex_Lower_Graph_Box") and (self.Touch_Down_Index == 0)))): return False

        with instance.canvas:
            self.line.points=(touch.x, touch.y, self.Touch_Down_X, touch.y,
                              self.Touch_Down_X, self.Touch_Down_Y, touch.x, self.Touch_Down_Y,
                              touch.x, touch.y)
        instance.canvas.ask_update()

    def on_touch_up ( self, instance, touch, *args ):
        if ((not instance.collide_point(touch.x, touch.y)) or
            # Only plots can be zoomed, images cannot
            (self.Image_Widget)): return False

        # Exit if no touch down or incomplete touch down recorded
        if ((self.Touch_Down_Instance_Id is None) or
            (self.Touch_Down_Index is None) or
            (self.Touch_Down_Ratio_Horizontal is None) or
            (self.Touch_Down_Ratio_Vertical is None)): return False

        # Exit if inconsistent touch down recorded
        if (not (instance.id == self.Touch_Down_Instance_Id)): return False
        if (not (((instance.id == "Duplex_Upper_Graph_Box") and (self.Touch_Down_Index == 0)) or
                 ((instance.id == "Duplex_Lower_Graph_Box") and (self.Touch_Down_Index == 1)) or
                 ((instance.id == "Simplex_Lower_Graph_Box") and (self.Touch_Down_Index == 0)))): return False

        instance_left, instance_bottom = instance.pos
        touch_up_ratio_horizontal = bound(0, 1, ((touch.x - instance_left) / instance.width))
        touch_up_ratio_vertical = bound(0, 1, ((touch.y - instance_bottom) / instance.height))

        horizontal_ratio_list = [self.Touch_Down_Ratio_Horizontal, touch_up_ratio_horizontal]
        vertical_ratio_list = [self.Touch_Down_Ratio_Vertical, touch_up_ratio_vertical]
        time_axis_zoom_offset_ratios = tuple(sorted(horizontal_ratio_list))
        value_axis_zoom_offset_ratios = tuple(sorted(vertical_ratio_list))

        graph_widget_list_index = self.Touch_Down_Index
        self.zoom_cloudwatch_graph(graph_widget_list_index,
                                   Time_Axis_Zoom_Offset_Ratios=time_axis_zoom_offset_ratios,
                                   Value_AxisZoom_Offset_Ratios=value_axis_zoom_offset_ratios)

        if (instance.id == "Duplex_Upper_Graph_Box"):
            self.Duplex_Upper_Graph_Box.clear_widgets()
            self.Duplex_Upper_Graph_Box.add_widget(graph_widget_list[0])

        elif (instance.id == "Duplex_Lower_Graph_Box"):
            self.Duplex_Lower_Graph_Box.clear_widgets()
            self.Duplex_Lower_Graph_Box.add_widget(graph_widget_list[1])

        elif (instance.id == "Simplex_Lower_Graph_Box"):
            self.Simplex_Lower_Graph_Box.clear_widgets()
            self.Simplex_Lower_Graph_Box.add_widget(graph_widget_list[0])

        self.CloudWatch_Remote.canvas.ask_update()
        return True

    def escape_graph_zoom ( self ):
        graph_widget_list_index = self.Touch_Down_Index
        self.zoom_cloudwatch_graph(graph_widget_list_index)

        if (self.Touch_Down_Instance_Id == "Duplex_Upper_Graph_Box"):
            self.Duplex_Upper_Graph_Box.clear_widgets()
            self.Duplex_Upper_Graph_Box.add_widget(graph_widget_list[0])

        elif (self.Touch_Down_Instance_Id == "Duplex_Lower_Graph_Box"):
            self.Duplex_Lower_Graph_Box.clear_widgets()
            self.Duplex_Lower_Graph_Box.add_widget(graph_widget_list[1])

        elif (self.Touch_Down_Instance_Id == "Simplex_Lower_Graph_Box"):
            self.Simplex_Lower_Graph_Box.clear_widgets()
            self.Simplex_Lower_Graph_Box.add_widget(graph_widget_list[0])

        self.clear_touch()

        self.CloudWatch_Remote.canvas.ask_update()
        return True


    def adjust_graph_height ( self ):
        if (self.Visible_Graph_Count == 2):
            for widget_descriptor in widget_descriptor_list:
                widget_descriptor["height"] = int(round(self.Vertical_Graph_Height / 2.0))
        elif (self.Visible_Graph_Count == 1):
            for widget_descriptor in widget_descriptor_list:
                widget_descriptor["height"] = int(round(self.Vertical_Graph_Height))

    def on_simplex ( self, *args ):
        if (self.Visible_Graph_Count == 2): self.toggle_duplex_versus_simplex()
        return True

    def on_duplex ( self, *args ):
        if (self.Visible_Graph_Count == 1): self.toggle_duplex_versus_simplex()
        return True

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

            self.force_update()

        elif (Screen_Manager_App): # Redundant explicit test is note-to-self
            if (self.CloudWatch_Remote.current == "duplex"):
                self.synchronize_control_bar_values(self.Simplex_TimeSpanControlBar)
                self.Visible_Graph_Count = 1
                self.adjust_graph_height()
                self.CloudWatch_Remote.current = "simplex"
            elif (self.CloudWatch_Remote.current == "simplex"):
                self.synchronize_control_bar_values(self.Duplex_TimeSpanControlBar)
                self.Visible_Graph_Count = 2
                self.adjust_graph_height()
                self.CloudWatch_Remote.current = "duplex"

            self.force_update()

    def synchronize_control_bar_values ( self, target_control_bar ):
        for destination_child in target_control_bar.children:
            target_control_bar.set_period_duration_value(self.Period_Duration_Hours)
            target_control_bar.set_period_end_value(self.Period_End_Hours_Ago)

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
        self.force_update()
        return True

    def on_next ( self, *args ):
        if (self.Image_Widget): descriptor_list_length = len(widget_descriptor_list)
        else: descriptor_list_length = len(metric_descriptor_list)

        if (self.Visible_Graph_Count == 2):
            # We are displaying two graphs, must account for second graph after skipping ahead
            if ((self.Graph_Offset + 2 + 1) < descriptor_list_length):
                self.Graph_Offset += 2
            elif ((self.Graph_Offset + 1 + 1) < descriptor_list_length):
                # If at at the end save one graph, move ahead by one for odd alignment
                self.Graph_Offset += 1
        else:
            if ((self.Graph_Offset + 1) < descriptor_list_length):
                self.Graph_Offset += 1
        self.force_update()
        return True

    def clear_touch ( self ):
        self.Touch_Down_Instance_Id = None
        self.Touch_Down_Index = None
        self.Touch_Down_Ratio_Horizontal = None
        self.Touch_Down_Ratio_Vertical = None
        self.Touch_Down_X = None
        self.Touch_Down_Y = None

    def on_help ( self, *args ):
        self.CloudWatch_Remote.current = "help"
        return True

    def on_help_escape ( self, *args ):
        if (self.CloudWatch_Remote.current == "help"):
            if (self.Visible_Graph_Count == 2):
                self.CloudWatch_Remote.current = "duplex"
            elif (self.Visible_Graph_Count == 1):
                self.CloudWatch_Remote.current = "simplex"

    def on_keyboard_down ( self, instance, keyboard, keycode, text, modifiers ):
        # print ("keyboard:", keyboard, "keycode:", keycode, ", text:", text, ", modifiers:", modifiers)
        if (keycode == 44):
            if (not (self.CloudWatch_Remote.current == "help")):
                self.toggle_duplex_versus_simplex()
        elif ((keyboard == 27) or (keycode == 41)):
            if (not (self.CloudWatch_Remote.current == "help")):
                self.escape_graph_zoom()
            else: self.on_help_escape()
        elif ((keycode == 81) or (keycode == 79)):
            if (not (self.CloudWatch_Remote.current == "help")):
                self.on_next()
        elif ((keycode == 82) or (keycode == 80)):
            if (not (self.CloudWatch_Remote.current == "help")):
                self.on_previous()
        return True

    def on_start ( self, **kwargs ):
        if (Defer_CWapi_Requests): Clock.schedule_once(self.force_update, Defer_CWapi_Requests_by_Seconds)
        else: self.force_update()
        return True

# Instantiate and run the kivy app
if __name__ == '__main__':
    CW_Remote().run()
    