#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-

# Y axis ticks/labels optimize
# Defer refresh if zoomed

# Tried these, can't do, limitations of PySide2:
# # X axis ticks/labels optimize
# # X/Y axis subticks

# $ pyinstaller -F -w --exclude-module _tkinter --exclude-module Tkinter --exclude-module enchant --exclude-module twisted --osx-bundle-identifier com.techview.cwremote  -i CW_Remote.icns CW_Remote_Qt.py

from __future__ import print_function
from __future__ import division

from PySide2 import QtCore, QtGui, QtWidgets

from PySide2.QtCore import QPoint, Qt, QDateTime, QRect, QRectF, QSize, QMargins
from PySide2.QtGui import QPainter, QPen, QColor
from PySide2.QtCharts import QtCharts

# import PySide2.QtCore.QString as QString

import sys
import os, sys
from os.path import isfile, join, expanduser # dirname
import platform

import datetime, calendar

import boto3

import json

import copy

from collections import OrderedDict

import re


# from Graph_Index_0 import Graph_Index_0
# from Graph_Index_1 import Graph_Index_1
#
# def Parse_ISO_DateTime_String ( ISO_DateTime_String ):
#     if (ISO_DateTime_String.endswith('Z')):
#         ISO_DateTime_String = ISO_DateTime_String[:-1] + "+00:00"
#     # "2019-01-03T00:00:05.522864Z"
#     # "2017-04-27T04:02:59.008000+00:00"
#     #  00000000001111111111222222222233
#     #  01234567890123456789012345678901
#     iso_microseconds = 0
#     iso_timezone_string = ''
#     if (len(ISO_DateTime_String) == 19):
#         # No microseconds and no time zone specification
#         # Interpret this as NYC wall time
#         iso_microseconds = 0
#         iso_timezone_string = ''
#     elif ((len(ISO_DateTime_String) == 26) and (ISO_DateTime_String[19] == '.')):
#         # Microseconds but no time zone specification
#         # Interpret this as NYC wall time
#         iso_microseconds = int(ISO_DateTime_String[20:26])
#         iso_timezone_string = ''
#     elif ((ISO_DateTime_String[19] == '+') or (ISO_DateTime_String[19] == '-')):
#         # No microseconds but having time zone specification
#         iso_microseconds = 0
#         iso_timezone_string = ISO_DateTime_String[19:]
#     elif ((ISO_DateTime_String[19] == '.') and
#           ((ISO_DateTime_String[26] == '+') or (ISO_DateTime_String[26] == '-'))):
#         # Both microseconds plus time zone specification
#         iso_microseconds = int(ISO_DateTime_String[20:26])
#         iso_timezone_string = ISO_DateTime_String[26:]
#     # "2016-07-09T03:27:27-0400"
#     #  00000000001111111111222222
#     #  01234567890123456789012345
#     # "2016-07-09T03:27:27-04:00"
#     # Compute UTC offset, supporting all forms: "+0400", "-0400", "+04:00", and "-04:00"
#     if (len(iso_timezone_string) == 0):
#         # In the US, since 2007, DST starts at 2am (standard time) on the second
#         # Sunday in March, which is the first Sunday on or after Mar 8.
#         # and ends at 2am (DST time; 1am standard time) on the first Sunday of Nov.
#         begin_daylight_savings = \
#             datetime.datetime(year=int(ISO_DateTime_String[0:4]), month=3, day=8, hour=2, tzinfo=Eastern_Standard_Time_Zone)
#         begin_daylight_savings += datetime.timedelta(days=(6 - begin_daylight_savings.date().weekday()))
#
#         end_daylight_savings = \
#             datetime.datetime(year=int(ISO_DateTime_String[0:4]), month=11, day=1, hour=1, tzinfo=Eastern_Standard_Time_Zone)
#         end_daylight_savings += datetime.timedelta(days=(6 - end_daylight_savings.date().weekday()))
#
#         datetime_EST = \
#            datetime.datetime(int(ISO_DateTime_String[0:4]), # year
#                              int(ISO_DateTime_String[5:7]), # month
#                              int(ISO_DateTime_String[8:10]), # day
#                              int(ISO_DateTime_String[11:13]), # hour
#                              int(ISO_DateTime_String[14:16]), # minute
#                              int(ISO_DateTime_String[17:19]), # second
#                              iso_microseconds, # microseconds
#                              Eastern_Standard_Time_Zone)
#
#         if ((datetime_EST >= begin_daylight_savings) and (datetime_EST <= end_daylight_savings)):
#             minutes_offset = -4 * 60  # Eastern_Daylight_Time_Zone
#         else: minutes_offset = -5 * 60 # Eastern_Standard_Time_Zone
#
#     elif (iso_timezone_string[3] == ':'):
#         minutes_offset = (60 * int(iso_timezone_string[1:3])) + int(iso_timezone_string[4:6])
#     else:
#         minutes_offset = (60 * int(iso_timezone_string[1:3])) + int(iso_timezone_string[3:5])
#     if ((len(iso_timezone_string) > 0) and
#         (iso_timezone_string[0] == '-')): minutes_offset = -minutes_offset
#
#     # Return ISO_DateTime_String as UTC datetime
#     return datetime.datetime(int(ISO_DateTime_String[0:4]), # year
#                              int(ISO_DateTime_String[5:7]), # month
#                              int(ISO_DateTime_String[8:10]), # day
#                              int(ISO_DateTime_String[11:13]), # hour
#                              int(ISO_DateTime_String[14:16]), # minute
#                              int(ISO_DateTime_String[17:19]), # second
#                              iso_microseconds, # microseconds
#                              Time_Zone(minutes_offset)).astimezone(UTC_Time_Zone)
#
# def Metric_Statistics_Datapoints_Time_and_Values(Metric_Statistics_Datapoints, Y_Factor=1):
#     data_point_list = []
#     for data_point in Metric_Statistics_Datapoints:
#         data_datetime = Parse_ISO_DateTime_String(data_point["Timestamp"])
#         nyc_wall_time_offset = NYC_Wall_DateTime_Offset(data_datetime)
#         data_datetime = data_datetime + datetime.timedelta(hours=int(nyc_wall_time_offset) / 100)
#         # datetime_str = data_point["Timestamp"][:-6]
#         # format =  "yyyy-MM-ddTHH:mm:ss"
#         # data_datetime = QDateTime.fromString(datetime_str, format);
#         data_maximum = data_point["Maximum"] * Y_Factor
#         data_average = data_point["Average"] * Y_Factor
#         data_point_list.append((data_datetime, data_maximum, data_average))
#     data_point_list.sort()
#
#     data_time_max_list = [(time, max) for time, max, avg in data_point_list]
#     return data_time_max_list


# Convenience function to bound a value
def bound ( low, high, value ):
    return max(low, min(high, value))


def Round_DateTime (Initial_DateTime, Round_to_Resolution_Seconds=60):
   seconds = (Initial_DateTime - Initial_DateTime.min).seconds
   rounding = (seconds + (Round_to_Resolution_Seconds / 2)) // Round_to_Resolution_Seconds * Round_to_Resolution_Seconds
   return Initial_DateTime + datetime.timedelta(0, (rounding - seconds), -Initial_DateTime.microsecond)


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

CW_Remote_Duplex_Layout = True
Force_Duplex_Layout = True

Force_GetMetricWidgetImage = False # True # False #

Cursor_Tracking = True # True # False #

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

Initial_Period_Duration_Hours = 24
Initial_Period_End_Hours_Ago = 0

cw_remote_ini_json = ""
cw_remote_ini = None

path_to_time_slider_cursor = ""
path_to_time_slider_cursor_disabled = ""
path_to_cwremote_screen_image = ""

execution_directory = os.path.abspath(os.path.dirname(sys.argv[0]))
execution_script = os.path.abspath(sys.argv[0])
os_platform = platform.system()

# message_text = execution_directory

# Find json initialization file and image resources
if (os_platform == "Darwin"):
    # execution_directory = execution_directory.split("CW_Remote_Qt.app")[0]
    execution_directory = re.split("/CW_Remote[0-9a-zA-Z_]*[.](?:app|py)", execution_script)[0] # [0-9a-zA-Z_]+\\.app

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

    # Config.set('kivy','window_icon', path_to_icon_image)
    # Config.write()

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
    cw_remote_ini_json = ""
    # if (Kivy_Platform == "android"):
    #     # Pydroid 3 fails to install pycairo
    #     # Gtk backend requires PyGObject or pgi
    #     # "Pip" menu item, "Install": pygobject
    #     # "Running setup.py install for pycairo: finished with status 'error' "
    #     # ...
    #     # "No package 'cairo' found"
    #     # Fix:
    #     # import matplotlib
    #     # matplotlib.use('AGG')
    #
    #     try:
    #         # To run from Pydroid 3
    #         if (isfile(join(execution_directory, "CW_Remote.ini"))):
    #             ini_directory = execution_directory
    #         else:
    #             home_dir = expanduser("~")
    #             ini_dir = "Documents/CW_Remote"
    #             ini_directory = join(home_dir, ini_dir)
    #
    #         path_to_time_slider_cursor = join(ini_directory, "data", "time_slider_cursor.png")
    #         path_to_time_slider_cursor_disabled = join(ini_directory, "data", "time_slider_cursor_disabled.png")
    #
    #         cw_remote_ini_file = open(join(ini_directory, "CW_Remote.ini"), "r")
    #         cw_remote_ini_json = cw_remote_ini_file.read()
    #         cw_remote_ini_file.close()
    #
    #         # documents_dir = "/system/storage/emulated/0/Documents"
    #         # ini_dir = "CW_Remote"
    #         # ini_directory = join(documents_dir, ini_dir)
    #         #
    #         # cw_remote_ini_file = open(join(ini_directory, "CW_Remote.ini"), "r")
    #         # cw_remote_ini_json = cw_remote_ini_file.read()
    #         # cw_remote_ini_file.close()
    #
    #     except:
    #         cw_remote_ini_json = ""

elif (os_platform == "Windows"):
    cw_remote_ini_json = ""

else:
    cw_remote_ini_json = ""

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

        Alarm_Name_List = cw_remote_ini.get("alarm_name_list", [])

        Metric_Descriptor_List = []
        ini_metric_descriptor_list = cw_remote_ini.get("metric_descriptor_list", [])
        for metric_descr in ini_metric_descriptor_list:
            # metric_descr is itself a list, potentially with one element, or with two
            this_metric_descriptor = copy.deepcopy(metric_descr)
            Metric_Descriptor_List.append(this_metric_descriptor)

        Widget_Image_Descriptor_List = []
        ini_widget_descriptor_list = cw_remote_ini.get("widget_descriptor_list", [])
        for widget_descr in ini_widget_descriptor_list:
            this_widget_descriptor = widget_descr.copy()
            Widget_Image_Descriptor_List.append(this_widget_descriptor)

        if (len(Widget_Image_Descriptor_List) < 2):
            CW_Remote_Duplex_Layout = False

        if (CW_Remote_Duplex_Layout):
            pass
        else:
            # Not duplex, make graphs "higher", i.e. more vertical resolution
            for widget_descr in Widget_Image_Descriptor_List:
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


from threading import Thread


def Describe_Alarm_History ( Alarm_Name, Alarm_History_Results ):
    datetime_now_utc = datetime.datetime.now(UTC_Time_Zone)
    datetime_yesterday_utc = datetime_now_utc - datetime.timedelta(days=1)

    alarm_history = \
        cloudwatch_client.describe_alarm_history(AlarmName=Alarm_Name,
                                                 HistoryItemType="StateUpdate", # 'StateUpdate' | 'Action',
                                                 StartDate=datetime_yesterday_utc,
                                                 EndDate=datetime_now_utc,
                                                 MaxRecords=100,
                                                 NextToken='')

    Alarm_History_Results[Alarm_Name] = alarm_history

def Alarm_History ( ):
    if (len(Alarm_Name_List) == 0): return {}

    alarm_history_threads = [ None ] * len(Alarm_Name_List)
    alarm_history_results = { }

    for alarm_index, alarm_name in enumerate(Alarm_Name_List):
        alarm_history_threads[alarm_index] = \
            Thread(target=Describe_Alarm_History, args=(alarm_name, alarm_history_results))
        alarm_history_threads[alarm_index].start()

    for alarm_index in range(len(Alarm_Name_List)):
        alarm_history_threads[alarm_index].join()

    return alarm_history_results


def Optimize_DataPoint_Summary_Seconds ( Period_Hours ):
    datapoint_summary_seconds = 60

    # The maximum number of data points returned from a single call is 1,440.
    # The period for each datapoint can be 1, 5, 10, 30, 60, or any multiple of 60 seconds.

    datapoint_count = (Period_Hours * 60 * 60) / datapoint_summary_seconds
    while (datapoint_count > 1440):
        datapoint_summary_seconds += 60
        datapoint_count = (Period_Hours * 60 * 60) / datapoint_summary_seconds

    return datapoint_summary_seconds


# These are specific to cw_remote, parameters for generating figures, etc. ...
# There can be a maximum of two figures per page (duplex), or only one (simplex)
_graph_plot_metric_statistics_list = [None, None]


def get_Graph_Plot_Metric_Statistics(Plot_Figure_Index):
    global _graph_plot_metric_statistics_list
    return _graph_plot_metric_statistics_list[Plot_Figure_Index]


def set_Graph_Plot_Metric_Statistics(Plot_Figure_Index, Graph_Plot_Metric_Statistics):
    global _graph_plot_metric_statistics_list
    _graph_plot_metric_statistics_list[Plot_Figure_Index] = Graph_Plot_Metric_Statistics
# ... These are specific to cw_remote, parameters for generating figures, etc.


# Code specific to AWS API, fetch data and render into matplotlib friendly form
def Get_Metric_Statistics ( Metric_Descriptor, Metric_Statistics_List, Metric_Statistics_Index ):
    raw_metric_statistics = \
        cloudwatch_client.get_metric_statistics(MetricName=Metric_Descriptor["MetricName"],
                                                Namespace=Metric_Descriptor["Namespace"],
                                                Dimensions=Metric_Descriptor["Dimensions"],
                                                StartTime=Metric_Descriptor["StartTime"],
                                                EndTime=Metric_Descriptor["EndTime"],
                                                Period=Metric_Descriptor["Period"],
                                                Statistics=Metric_Descriptor["Statistics"],
                                                Unit=Metric_Descriptor["Unit"])

    raw_metric_statistics_datapoints = raw_metric_statistics.get("Datapoints", [])
    nyc_wall_time_offset = NYC_Wall_DateTime_Offset(Metric_Descriptor["EndTime"])
    nyc_wall_datetime_offset = datetime.timedelta(hours=int(nyc_wall_time_offset) / 100)
    y_factor = Metric_Descriptor.get("YFactor", 1)

    data_point_list = []
    for data_point in raw_metric_statistics_datapoints:
        data_datetime = data_point["Timestamp"]
        # This will return some wrong local time values ...
        # ... if StartTime and EndTime straddle standard <=> daylight savings
        # The alternative will cause graph to have discontinuity (worse), ...
        # ... or duplicates of time values (fatal)
        data_datetime = data_datetime + nyc_wall_datetime_offset
        data_maximum = data_point["Maximum"] * y_factor
        data_average = data_point["Average"] * y_factor
        data_point_list.append((data_datetime, data_maximum, data_average))
    data_point_list.sort()

    data_time_max_list = [(time, max) for time, max, avg in data_point_list]
    data_time_avg_list = [(time, avg) for time, max, avg in data_point_list]

    prepared_metric_statistics = {}
    prepared_metric_statistics["Datapoints_Maximum_List"] = data_time_max_list
    prepared_metric_statistics["Datapoints_Average_List"] = data_time_avg_list

    prepared_metric_statistics["MetricDescriptor"] = Metric_Descriptor

    Metric_Statistics_List[Metric_Statistics_Index] = prepared_metric_statistics

Cache_Page_Metrics = True # False # True #
Cache_Page_Metric_Statistics = []

def Page_Get_Metric_Statistics_Datapoints ( Metric_Index_List, Period_End_UTC, Period_Hours ):
    global Cache_Page_Metric_Statistics

    if (len(Metric_Index_List) == 0): return False

    Cache_Page_Metric_Statistics = []

    if (not Cache_Page_Metrics): return False

    # start_time = time.clock()

    period_begin_utc = Period_End_UTC - datetime.timedelta(hours=Period_Hours)
    datapoint_summary_seconds = Optimize_DataPoint_Summary_Seconds(Period_Hours)

    page_metric_descriptor_list = {}

    for list_index, metric_index in enumerate(Metric_Index_List):
        metric_descr_list = Metric_Descriptor_List[metric_index]
        metric_statistics_list = [None] * len(metric_descr_list)
        for descr_index, metric_descr in enumerate(metric_descr_list):
            page_metric_descriptor_list[(list_index, descr_index)] = metric_descr
        # Graph placeholder metric_statistics_list contain a placeholder ...
        # ... for each line on the graph, each line representing one metric statistics.
        Cache_Page_Metric_Statistics.append(metric_statistics_list)
        # For each graph on this page (either one or two) ...
        # ... there must be one graph placeholder in the cache.

    get_metric_statistics_threads = []

    for list_descr_key, metric_descr in page_metric_descriptor_list.items():
        list_index, descr_index = list_descr_key
        metric_descr["StartTime"] = period_begin_utc
        metric_descr["EndTime"] = Period_End_UTC
        metric_descr["Period"] = datapoint_summary_seconds
        this_thread = Thread(target=Get_Metric_Statistics,
                             args=(metric_descr, Cache_Page_Metric_Statistics[list_index], descr_index))
        # print ("start (", len(get_metric_statistics_threads), "):", (time.clock() - start_time), sep='')
        this_thread.start()
        get_metric_statistics_threads.append(this_thread)

    for thread_index, this_thread in enumerate(get_metric_statistics_threads):
        this_thread.join()
        # print("end (", thread_index, "):", (time.clock() - start_time), sep='')


class Control_Bar ( QtWidgets.QFrame ):

    metricsUpdate = QtCore.Signal()
    metricsPrevious = QtCore.Signal()
    metricsNext = QtCore.Signal()
    metricsDuplex = QtCore.Signal()
    metricsSimplex = QtCore.Signal()

    Period_Duration_Hours_Steps = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24,  # 18
                                   26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48,  # 12
                                   50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72,  # 12
                                   74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 96,  # 12
                                   100, 104, 108, 112, 116, 120,  # 6
                                   124, 128, 132, 136, 140, 144,  # 6
                                   148, 152, 156, 160, 164, 168]  # 6

    Period_End_Hours_Ago_Steps = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24,  # 19
                                  26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48,  # 12
                                  50, 52, 54, 56, 58, 60, 62, 64, 66, 68, 70, 72,  # 12
                                  74, 76, 78, 80, 82, 84, 86, 88, 90, 92, 94, 96,  # 12
                                  100, 104, 108, 112, 116, 120,  # 6
                                  124, 128, 132, 136, 140, 144,  # 6
                                  148, 152, 156, 160, 164, 168]  # 6

    def __init__(self, **kwargs):
        super(Control_Bar, self).__init__(**kwargs)

        self._tooltip = QtWidgets.QToolTip()
        self.setMouseTracking(True)

        self.__period_duration_hours = Initial_Period_Duration_Hours
        self.__period_end_hours_ago = Initial_Period_End_Hours_Ago

        slider_minimum_value = 0

        period_duration_slider_maximum_value = 999
        self.period_duration_slider_value_span = period_duration_slider_maximum_value - slider_minimum_value

        period_end_slider_maximum_value = 1000
        self.period_end_slider_value_span = period_end_slider_maximum_value - slider_minimum_value

        self.setContentsMargins(0, 0, 0, 0)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setAutoFillBackground(True)
        self.setLineWidth(0)
        self.setMaximumHeight(32)
        # self.setFrameStyle(QtWidgets.QFrame.Plain)

        control_bar_layout = QtWidgets.QHBoxLayout()
        control_bar_layout.setMargin(0)
        control_bar_layout.setContentsMargins(0, 0, 0, 0)
        control_bar_layout.setSpacing(2)
        control_bar_layout.setAlignment(Qt.AlignCenter)

        self.__previous_pushbutton = QtWidgets.QPushButton("⬆", parent=self)
        self.__previous_pushbutton.setFixedWidth(56)
        self.__previous_pushbutton.clicked.connect(self.__emit_previous_signal)
        self.__previous_pushbutton.setMouseTracking(True)
        control_bar_layout.addWidget(self.__previous_pushbutton)

        self.__period_duration_hours_label = QtWidgets.QLabel("24H", parent=self)
        self.__period_duration_hours_label.setFixedWidth(76)
        self.__period_duration_hours_label.setAlignment(Qt.AlignCenter)
        control_bar_layout.addWidget(self.__period_duration_hours_label)

        self.__period_duration_hours_slider = QtWidgets.QSlider(Qt.Horizontal, parent=self)
        self.__period_duration_hours_slider.setMinimumWidth(360) # 5 pixels per step, 72 steps
        self.__period_duration_hours_slider.setMinimum(slider_minimum_value)
        self.__period_duration_hours_slider.setMaximum(period_duration_slider_maximum_value)
        self.__period_duration_hours_slider.setValue(slider_minimum_value)
        self.__period_duration_hours_slider.valueChanged.connect(self.__on_period_duration_hours_value_change)
        self.__period_duration_hours_slider.sliderReleased.connect(self.__emit_update_signal)
        self.__period_duration_hours_slider.setMouseTracking(True)
        control_bar_layout.addWidget(self.__period_duration_hours_slider)

        # min = slider_minimum_value, max = period_duration_slider_maximum_value,
        # value = period_duration_slider_maximum_value, step = 1, size_hint = (0.4, 1))

        self.__duplex_pushbutton = QtWidgets.QPushButton("2", parent=self)
        self.__duplex_pushbutton.clicked.connect(self.__emit_duplex_signal)
        self.__duplex_pushbutton.setFixedWidth(32)
        self.__duplex_pushbutton.setDown(True)
        self.__duplex_pushbutton.setMouseTracking(True)
        control_bar_layout.addWidget(self.__duplex_pushbutton)

        refresh_pushbutton = QtWidgets.QPushButton("Refresh", parent=self)
        refresh_pushbutton.clicked.connect(self.__emit_update_signal)
        refresh_pushbutton.setFixedWidth(104)
        control_bar_layout.addWidget(refresh_pushbutton)

        self.__simplex_pushbutton = QtWidgets.QPushButton("1", parent=self)
        self.__simplex_pushbutton.clicked.connect(self.__emit_simplex_signal)
        self.__simplex_pushbutton.setFixedWidth(32)
        self.__simplex_pushbutton.setMouseTracking(True)
        control_bar_layout.addWidget(self.__simplex_pushbutton)

        self.__period_end_hours_ago_slider = QtWidgets.QSlider(Qt.Horizontal, parent=self)
        self.__period_end_hours_ago_slider.setMinimumWidth(360) # 5 pixels per step, 72 steps
        self.__period_end_hours_ago_slider.setMinimum(slider_minimum_value)
        self.__period_end_hours_ago_slider.setMaximum(period_end_slider_maximum_value)
        self.__period_end_hours_ago_slider.setValue(period_end_slider_maximum_value)
        self.__period_end_hours_ago_slider.valueChanged.connect(self.__on_period_end_hours_ago_value_change)
        self.__period_end_hours_ago_slider.sliderReleased.connect(self.__emit_update_signal)
        self.__period_end_hours_ago_slider.setMouseTracking(True)
        control_bar_layout.addWidget(self.__period_end_hours_ago_slider)

        # min = slider_minimum_value, max = period_end_slider_maximum_value,
        # value = period_end_slider_maximum_value, step = 1, size_hint = (0.4, 1))

        self.__period_end_hours_ago_label = QtWidgets.QLabel("0H ago", parent=self)
        self.__period_end_hours_ago_label.setFixedWidth(76)
        self.__period_end_hours_ago_label.setAlignment(Qt.AlignCenter)
        control_bar_layout.addWidget(self.__period_end_hours_ago_label)

        self.__next_pushbutton = QtWidgets.QPushButton("⬇", parent=self)
        self.__next_pushbutton.setFixedWidth(56)
        self.__next_pushbutton.clicked.connect(self.__emit_next_signal)
        self.__next_pushbutton.setMouseTracking(True)
        control_bar_layout.addWidget(self.__next_pushbutton)

        self.setLayout(control_bar_layout)

        self.set_period_duration_hours_value(self.__period_duration_hours)
        self.set_period_end_hours_ago_value(self.__period_end_hours_ago)

    # Public functions (used to synchronize multiple TimeSpanControlBars) ...
    def get_period_duration_hours_value ( self ):
        return self.__period_duration_hours

    def set_period_duration_hours_value ( self, period_duration_hours_value, *args ):
        self.__period_duration_hours = period_duration_hours_value
        self.__period_duration_hours_label.setText(self.__period_value_display(self.__period_duration_hours))
        self.__period_duration_hours_slider.setValue \
            (1000 - int(round(self.period_duration_slider_value_span *
                              (self.Period_Duration_Hours_Steps.index(self.__period_duration_hours) /
                               len(self.Period_Duration_Hours_Steps)))))

    def get_period_end_hours_ago_value ( self ):
        return self.__period_end_hours_ago

    def set_period_end_hours_ago_value ( self, period_end_hours_ago_value, *args ):
        self.__period_end_hours_ago = period_end_hours_ago_value
        self.__period_end_hours_ago_slider.setValue \
            (1000 - int(round(self.period_end_slider_value_span *
                              (self.Period_End_Hours_Ago_Steps.index(self.__period_end_hours_ago) /
                               len(self.Period_End_Hours_Ago_Steps)))))
        self.__period_end_hours_ago_label.text = (self.__period_value_display(self.__period_end_hours_ago) + " ago")
    # ... Public functions  (used to synchronize multiple TimeSpanControlBars)

    # Private functions ...
    def __period_value_display ( self, Period_Value ):
        period_value_string = ""
        if ((Period_Value // 24) > 0): period_value_string += str(Period_Value // 24) + "D"
        if (((Period_Value % 24) > 0) or (len(period_value_string) == 0)):
            if (len(period_value_string) > 0): period_value_string += " "
            period_value_string += str(Period_Value % 24) + "H"
        return period_value_string

    def __on_period_duration_hours_value_change ( self, period_duration_slider_value, *args ):
        # print (period_duration_slider_value)
        period_value_index = \
            int(round(len(self.Period_Duration_Hours_Steps) *
                      (abs(period_duration_slider_value - 1000) / self.period_duration_slider_value_span)))
        self.__period_duration_hours = \
            self.Period_Duration_Hours_Steps[bound(0, (len(self.Period_Duration_Hours_Steps) - 1), period_value_index)]
        self.__period_duration_hours_label.setText(self.__period_value_display(self.__period_duration_hours))
        # print (period_duration_slider_value, period_value_index, self.__period_duration_hours, self.period_duration_label.text)
        return True

    def __on_period_end_hours_ago_value_change ( self, period_end_slider_value, *args ):
        period_end_value_index = \
            int(round(len(self.Period_End_Hours_Ago_Steps) *
                      (abs(period_end_slider_value - 1000) / self.period_end_slider_value_span)))
        self.__period_end_hours_ago = \
            self.Period_End_Hours_Ago_Steps[bound(0, (len(self.Period_End_Hours_Ago_Steps) -1), period_end_value_index)]
        self.__period_end_hours_ago_label.setText(self.__period_value_display(self.__period_end_hours_ago) + " ago")
        return True
    # ... Private functions

    def __emit_update_signal ( self ):
        self.metricsUpdate.emit()

    def __emit_previous_signal ( self ):
        self.metricsPrevious.emit()

    def __emit_next_signal ( self ):
        self.metricsNext.emit()

    def __emit_duplex_signal ( self ):
        if (not self.__duplex_pushbutton.isDown()):
            self.__duplex_pushbutton.setDown(True)
            self.__simplex_pushbutton.setDown(False)
            self.metricsDuplex.emit()

    def __emit_simplex_signal ( self ):
        if (not self.__simplex_pushbutton.isDown()):
            self.__duplex_pushbutton.setDown(False)
            self.__simplex_pushbutton.setDown(True)
            self.metricsSimplex.emit()

    def mouseMoveEvent ( self, event ):
        if (self.rect().contains(event.pos())):
            control_bar_pos = self.pos()

            tooltip_pos = event.pos()
            tooltip_pos.setX(control_bar_pos.x() + tooltip_pos.x())
            tooltip_pos.setY(control_bar_pos.y() + tooltip_pos.y() + 100)

            if (self.__previous_pushbutton.geometry().contains(event.pos())):
                self._tooltip.showText(tooltip_pos, "Previous graph page")
            elif (self.__period_duration_hours_slider.geometry().contains(event.pos())):
                self._tooltip.showText(tooltip_pos, "Adjust period of displayed metrics in hours")
            elif (self.__duplex_pushbutton.geometry().contains(event.pos())):
                self._tooltip.showText(tooltip_pos, "Duplex page (two graphs)")
            elif (self.__simplex_pushbutton.geometry().contains(event.pos())):
                self._tooltip.showText(tooltip_pos, "Simplex page (one graph)")
            elif (self.__period_end_hours_ago_slider.geometry().contains(event.pos())):
                self._tooltip.showText(tooltip_pos, "Adjust hours ago of end of displayed metrics period")
            elif (self.__next_pushbutton.geometry().contains(event.pos())):
                self._tooltip.showText(tooltip_pos, "Next graph page")
            else: self._tooltip.hideText()
        else: self._tooltip.hideText()


class Zoomable_Chart ( QtCharts.QChartView ):
    def __init__(self, Chart_Metric_Statistics_List, **kwargs):
        super(Zoomable_Chart, self).__init__(**kwargs)

        self.setContentsMargins(0, 0, 0, 0)

        self._zoom_level = 0
        self._zoom_factor = 4

        self._tooltip = QtWidgets.QToolTip()

        self._chart = QtCharts.QChart()
        self._chart.setBackgroundRoundness(0)
        self._chart.layout().setContentsMargins(0, 0, 0, 0)
        chart_margins = self._chart.margins()
        chart_margins.setTop(0)
        chart_margins.setBottom(0)
        self._chart.setMargins(chart_margins)

        self._axisX = QtCharts.QDateTimeAxis()
        self._chart.addAxis(self._axisX, Qt.AlignBottom)

        self._axisY_left = QtCharts.QValueAxis()
        self._chart.addAxis(self._axisY_left, Qt.AlignLeft)

        self._axisY_right = QtCharts.QValueAxis()
        self._chart.addAxis(self._axisY_right, Qt.AlignRight)

        # metric_statistics_list = Graph_Index_0
        self.__chart_data_load(Chart_Metric_Statistics_List)

        self.setChart(self._chart)
        self.setRenderHint(QPainter.Antialiasing)

    def setChartData ( self, Chart_Metric_Statistics_List ):
        self._chart.removeAllSeries()
        # Axes "remember" their previous state, ...
        # ... if not removed, previous min/max values will displayed
        self._chart.removeAxis(self._axisX)
        if (self._axisY_left is not None):
            self._chart.removeAxis(self._axisY_left)
        if (self._axisY_right is not None):
            self._chart.removeAxis(self._axisY_right)

        # Replace with new "stateless" axes
        self._axisX = QtCharts.QDateTimeAxis()
        self._chart.addAxis(self._axisX, Qt.AlignBottom)

        self._axisY_left = QtCharts.QValueAxis()
        self._chart.addAxis(self._axisY_left, Qt.AlignLeft)

        self._axisY_right = QtCharts.QValueAxis()
        self._chart.addAxis(self._axisY_right, Qt.AlignRight)

        self.__chart_data_load(Chart_Metric_Statistics_List)

        # self.repaint()

    def __chart_data_load (self, Chart_Metric_Statistics_List ):

        data_min_datetime = None
        data_max_datetime = None
        data_min_value_left = None
        data_max_value_left = None
        data_min_value_right = None
        data_max_value_right = None

        metric_statistics = Chart_Metric_Statistics_List[0]
        datapoints = metric_statistics.get("Datapoints_Maximum_List", [])

        # series_data = Metric_Statistics_Datapoints_Time_and_Values(datapoints)
        # data_min_datetime = series_data[0][0]
        # data_max_datetime = series_data[-1][0]

        data_min_datetime = datapoints[0][0]
        data_max_datetime = datapoints[-1][0]

        data_min_datetime_quantized = \
            data_min_datetime - datetime.timedelta(minutes=data_min_datetime.minute,
                                                   seconds=data_min_datetime.second)
        data_max_datetime_quantized = \
            data_max_datetime + datetime.timedelta(minutes=((60 - data_max_datetime.minute) % 60),
                                                   seconds=((60 - data_max_datetime.second) % 60))

        workaround_line_series = QtCharts.QLineSeries()
        workaround_line_series.append(QDateTime(data_min_datetime_quantized).toMSecsSinceEpoch(), 0)
        workaround_line_series.append(QDateTime(data_max_datetime_quantized).toMSecsSinceEpoch(), 0)
        pen = workaround_line_series.pen()
        pen.setWidth(1)
        pen.setColor("lightgray")
        workaround_line_series.setPen(pen)

        self._chart.addSeries(workaround_line_series)
        workaround_line_series.attachAxis(self._axisX)
        workaround_line_series.attachAxis(self._axisY_left)

        left_y_axis_series_count = 0
        right_y_axis_series_count = 0

        for metric_index, metric_statistics in enumerate(reversed(Chart_Metric_Statistics_List)):
            metric_statistics_descriptor = metric_statistics.get("MetricDescriptor", {})
            datapoints = metric_statistics.get("Datapoints_Maximum_List", [])

            which_y_axis = metric_statistics_descriptor.get("YAxis", "left")
            if (which_y_axis == "left"):
                left_y_axis_series_count += 1
            elif (which_y_axis == "right"):
                right_y_axis_series_count += 1

            # datapoints = metric_statistics.get("Datapoints", [])
            # series_data = Metric_Statistics_Datapoints_Time_and_Values(datapoints)

            if ((data_min_datetime is None) or (datapoints[0][0] < data_min_datetime)):
                data_min_datetime = datapoints[0][0]
            if ((data_max_datetime is None) or (datapoints[-1][0] > data_max_datetime)):
                data_max_datetime = datapoints[-1][0]

            data_min_datetime_quantized = \
                data_min_datetime - datetime.timedelta(minutes=data_min_datetime.minute,
                                                       seconds=data_min_datetime.second)
            data_max_datetime_quantized = \
                data_max_datetime + datetime.timedelta(minutes=((60 - data_max_datetime.minute) % 60),
                                                       seconds=((60 - data_max_datetime.second) % 60))

            line_series = QtCharts.QLineSeries()

            for point_time, point_value in datapoints:
                if (which_y_axis == "right"):
                    if ((data_min_value_right is None) or (point_value < data_min_value_right)):
                        data_min_value_right = point_value
                    if ((data_max_value_right is None) or (point_value > data_max_value_right)):
                        data_max_value_right = point_value
                elif (which_y_axis == "left"):
                    if ((data_min_value_left is None) or (point_value < data_min_value_left)):
                        data_min_value_left = point_value
                    if ((data_max_value_left is None) or (point_value > data_max_value_left)):
                        data_max_value_left = point_value

                line_series.append(QDateTime(point_time).toMSecsSinceEpoch(), point_value)

            line_color = tuple([int(255 * color_value)
                                for color_value in metric_statistics_descriptor.get("Color", [0, 0, 0])])
            pen = line_series.pen()
            pen.setWidth(0)
            pen.setColor(QColor(*line_color))
            line_series.setPen(pen)

            self._chart.addSeries(line_series)
            line_series.attachAxis(self._axisX)
            if (which_y_axis == "right"):
                line_series.attachAxis(self._axisY_right)
            elif (which_y_axis == "left"):
                line_series.attachAxis(self._axisY_left)

            line_series.setName(metric_statistics_descriptor.get("MetricLabel", " "))


        self._axisX.setMin(QDateTime(data_max_datetime_quantized).toMSecsSinceEpoch())
        self._axisX.setMax(QDateTime(data_max_datetime_quantized).toMSecsSinceEpoch())

        delta_hours = (data_max_datetime_quantized - data_min_datetime_quantized).total_seconds() // (60 * 60)
        delta_ticks = 12
        for factor in [13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]:
            if ((delta_hours % factor) == 0):
                delta_ticks = factor
                break

        self._axisX.setTickCount(delta_ticks + 1)
        self._axisX.setFormat("hh:mm'\n'MM/dd")

        if (left_y_axis_series_count == 0):
            self._chart.removeAxis(self._axisY_left)
            self._axisY_left = None
        else:
            # self._axisY_left.setTickAnchor(0)
            # self._axisY_left.setTickInterval(1)
            scale_factor = self._compute_optimal_axis_scale_factor(data_max_value_left)
            data_max_value_left_scaled = int(round(((data_max_value_left * 1.025) / scale_factor) + 0.5))
            self._axisY_left.setTickCount(data_max_value_left_scaled + 1)
            self._axisY_left.setRange(0, (scale_factor * data_max_value_left_scaled))
            pen_color = self._axisY_left.linePen().color()
            pen_color.setNamedColor("#ccccff")
            self._axisY_left.setLinePenColor(pen_color)
            self._axisY_left.setGridLineColor(pen_color)

            # self._axisY_left.setTickType(QtCharts.QValueAxis.TicksDynamic)
            # self._axisY_left.setTickAnchor(0)
            # unit_interval = 10**math.floor(math.log10(1.025 * data_max_value_left))
            # for unit_interval_scale in [1, 2, 4, 5, 8]:
            #     if ((data_max_value_left / (unit_interval / unit_interval_scale)) >= 4):
            #         unit_interval = unit_interval / unit_interval_scale
            #         break
            # self._axisY_left.setTickInterval(unit_interval)
            # self._axisY_left.setRange(0, (1.025 * data_max_value_left))
            #
            # # scale_factor = self._compute_optimal_axis_scale_factor(data_max_value_left)
            # # data_max_value_left_scaled = int(round(((data_max_value_left * 1.025) / scale_factor) + 0.5))
            # # self._axisY_left.setTickCount(data_max_value_left_scaled + 1)
            # # self._axisY_left.setRange(0, (scale_factor * data_max_value_left_scaled))

        if (right_y_axis_series_count == 0):
            self._chart.removeAxis(self._axisY_right)
            self._axisY_right = None
        else:
            # self._axisY_right.setTickAnchor(0)
            # self._axisY_right.setTickInterval(1)
            scale_factor = self._compute_optimal_axis_scale_factor(data_max_value_right)
            data_max_value_right_scaled = int(round(((data_max_value_right * 1.025) / scale_factor) + 0.5))
            self._axisY_right.setTickCount(data_max_value_right_scaled + 1)
            self._axisY_right.setRange(0, (scale_factor * data_max_value_right_scaled))
            pen_color = self._axisY_right.linePen().color()
            pen_color.setNamedColor("#ffcccc")
            self._axisY_right.setLinePenColor(pen_color)
            self._axisY_right.setGridLineColor(pen_color)

        # self._chart.legend().setVisible(False)
        legend = self._chart.legend()
        legend.markers(workaround_line_series)[0].setVisible(False)
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignTop)
        legend.setContentsMargins(0, 0, 0, 0)
        legend.layout().setContentsMargins(0, 0, 0, 0)

    def _compute_optimal_axis_scale_factor ( self, data_maximum_value ):
        scale_factor = 0
        scale_factor_power = 1 / (10 * 1000 * 1000)
        while ((scale_factor == 0) and (scale_factor_power <= (1000 * 1000))):
            scale_factor_power *= 10
            for scale_factor_multiplier in [1, 2, 4, 5, 8]:
                scale_factor_ceiling = scale_factor_power * scale_factor_multiplier
                if (data_maximum_value <= scale_factor_ceiling):
                    scale_factor = scale_factor_ceiling / 10
                    break

        if (scale_factor == 0): scale_factor = (1000 * 1000)

        return scale_factor

    def mousePressEvent ( self, event ):
        if (self._zoom_level == 0):
            # chart_rect = self._rect()
            # mouse_press_position = event.pos()
            plotarea_rect = self._chart.plotArea()
            zoom_area_left = \
                max((event.pos().x() - (plotarea_rect.width() / (2 * self._zoom_factor))), plotarea_rect.left())
            zoom_area_top = \
                max((event.pos().y() - (plotarea_rect.height() / (2 * self._zoom_factor))), plotarea_rect.top())
            zoom_area_width = plotarea_rect.width() / self._zoom_factor
            zoom_area_height = plotarea_rect.height() / self._zoom_factor
            if ((zoom_area_left + zoom_area_width) > (plotarea_rect.left() + plotarea_rect.width())):
                zoom_area_left = (plotarea_rect.left() + plotarea_rect.width()) - zoom_area_width
            if ((zoom_area_top + zoom_area_height) > (plotarea_rect.top() + plotarea_rect.height())):
                zoom_area_top = (plotarea_rect.top() + plotarea_rect.height()) - zoom_area_height
            zoom_rect = QRectF(zoom_area_left, zoom_area_top, zoom_area_width, zoom_area_height)
            self._chart.zoomIn(zoom_rect)
            self._zoom_level += 1
        else:
            self._chart.zoomReset()
            self._zoom_level -= 1

    def mouseMoveEvent ( self, event ):
        self_pos = self.pos()
        plotarea_rect = self._chart.plotArea()
        if (not plotarea_rect.contains(event.pos())):
            self._tooltip.hideText()
        else:
            mouse_move_position = event.pos()

            tooltip_text = ''

            chart_series_list = self._chart.series()
            # First series is workaround for datetime axis labeling issue
            mouse_move_point_left = self._chart.mapToValue(mouse_move_position, chart_series_list[1])
            mouse_move_point_right = self._chart.mapToValue(mouse_move_position, chart_series_list[-1])

            mouse_move_datetime = QDateTime()
            mouse_move_datetime.setMSecsSinceEpoch(mouse_move_point_right.x())
            tooltip_text += mouse_move_datetime.toString("yyyy-MM-dd HH:mm")
            tooltip_text += '\n' + "L: " + str(round(mouse_move_point_left.y(), 2))
            tooltip_text += "   R: " + str(round(mouse_move_point_right.y(), 2))

            mouse_move_plotarea_x = mouse_move_position.x() - plotarea_rect.left()
            if (mouse_move_plotarea_x < (plotarea_rect.width() / 2)):
                tooltip_pos_offset_x = 100
            else:
                tooltip_pos_offset_x = -25

            mouse_move_plotarea_y = mouse_move_position.y() - plotarea_rect.top()
            if (mouse_move_plotarea_y < (plotarea_rect.height() / 2)):
                tooltip_pos_offset_y = 125
            else:
                tooltip_pos_offset_y = 50

            tooltip_pos = event.pos()
            tooltip_pos.setX(self_pos.x() + tooltip_pos.x() + tooltip_pos_offset_x)
            tooltip_pos.setY(self_pos.y() + tooltip_pos.y() + tooltip_pos_offset_y)
            self._tooltip.showText(tooltip_pos, tooltip_text)

            # chart_rect = self.rect()
            # plotarea_rect = self._chart.plotArea()

            # for chart_series in chart_series_list[1:]: # First series workaround for datetime axis labeling issue
            #     point_list = chart_series.points()

    # def  mouseReleaseEvent ( self, event ):
    #      pass


class CW_Remote_Screen ( QtWidgets.QWidget ):
    def __init__(self, **kwargs):
        super(CW_Remote_Screen, self).__init__(**kwargs)

        self.Visible_Graph_Count = 2
        self.Graph_Offset = 0

        self.setContentsMargins(0, 0, 0, 0)

        self.Period_Duration_Hours = Initial_Period_Duration_Hours
        self.Period_End_Hours_Ago = Initial_Period_End_Hours_Ago

        datetime_now_utc = datetime.datetime.now(UTC_Time_Zone)
        period_end_utc = datetime_now_utc - datetime.timedelta(hours=self.Period_End_Hours_Ago)

        Page_Get_Metric_Statistics_Datapoints([(self.Graph_Offset + 0), (self.Graph_Offset + 1)],
                                              period_end_utc, self.Period_Duration_Hours)

        main_window_layout = QtWidgets.QVBoxLayout()
        main_window_layout.setMargin(0)
        main_window_layout.setContentsMargins(0, 0, 0, 0)
        main_window_layout.setSpacing(0)

        self.__empty_label = QtWidgets.QLabel('')
        self.__empty_label.setMaximumHeight(1)
        # main_window_layout.addWidget(self.__empty_label)

        # message_label = QtWidgets.QLabel(message_text)
        # main_window_layout.addWidget(message_label)

        if (Cache_Page_Metrics and (len(Cache_Page_Metric_Statistics) > 0)):
            metric_statistics_list = Cache_Page_Metric_Statistics[0]
            self.__zoomable_chart_upper = Zoomable_Chart(metric_statistics_list)
            main_window_layout.addWidget(self.__zoomable_chart_upper, stretch=0.5)

        self.__control_bar = Control_Bar()
        self.__control_bar.metricsUpdate.connect(self.__update_page_metrics)
        self.__control_bar.metricsPrevious.connect(self.__previous_page_metrics)
        self.__control_bar.metricsNext.connect(self.__next_page_metrics)
        self.__control_bar.metricsDuplex.connect(self.__duplex_metrics)
        self.__control_bar.metricsSimplex.connect(self.__simplex_metrics)
        main_window_layout.addWidget(self.__control_bar, stretch=0)

        if (Cache_Page_Metrics and (len(Cache_Page_Metric_Statistics) > 1)):
            metric_statistics_list = Cache_Page_Metric_Statistics[1]
            self.__zoomable_chart_lower = Zoomable_Chart(metric_statistics_list)
            main_window_layout.addWidget(self.__zoomable_chart_lower, stretch=0.5)

        self.setLayout(main_window_layout)

        self.__timer = QtCore.QTimer()
        self.__timer.timeout.connect(self.__update_page_metrics)
        self.__timer.start(60000) # 60 seconds in milliseconds

    def __update_page_metrics ( self, *args ):
        self.Period_Duration_Hours = self.__control_bar.get_period_duration_hours_value()
        self.Period_End_Hours_Ago = self.__control_bar.get_period_end_hours_ago_value()

        self.set_main_window_title()

        datetime_now_utc = datetime.datetime.now(UTC_Time_Zone)
        period_end_utc = datetime_now_utc - datetime.timedelta(hours=self.Period_End_Hours_Ago)

        Page_Get_Metric_Statistics_Datapoints([(self.Graph_Offset + 0), (self.Graph_Offset + 1)],
                                              period_end_utc, self.Period_Duration_Hours)

        if (Cache_Page_Metrics and (len(Cache_Page_Metric_Statistics) > 0)):
            metric_statistics_list = Cache_Page_Metric_Statistics[0]
            self.__zoomable_chart_upper.setChartData(metric_statistics_list)

        if (Cache_Page_Metrics and (len(Cache_Page_Metric_Statistics) > 1)):
            metric_statistics_list = Cache_Page_Metric_Statistics[1]
            self.__zoomable_chart_lower.setChartData(metric_statistics_list)

    def __previous_page_metrics ( self, *args ):
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
        self.__update_page_metrics()

    def __next_page_metrics ( self, *args ):
        descriptor_list_length = len(Metric_Descriptor_List)
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
        self.__update_page_metrics()

    def __duplex_metrics ( self, *args ):
        # self.__zoomable_chart_upper.show()
        main_window_layout = self.layout()
        main_window_layout.replaceWidget(self.__empty_label, self.__zoomable_chart_upper, options=Qt.FindDirectChildrenOnly)
        self.__zoomable_chart_lower.setMaximumHeight(self.__zoomable_chart_lower_height)
        self.__zoomable_chart_upper.setMaximumHeight(self.__zoomable_chart_upper_height)
        self.Graph_Offset = max((self.Graph_Offset - 1), 0)
        self.Visible_Graph_Count = 2
        # self.__update_page_metrics()
        self.update()

    def __simplex_metrics(self, *args):
        descriptor_list_length = len(Metric_Descriptor_List)
        self.__zoomable_chart_upper_height = self.__zoomable_chart_upper.height()
        self.__zoomable_chart_lower_height = self.__zoomable_chart_lower.height()
        main_window_layout = self.layout()
        main_window_layout.replaceWidget(self.__zoomable_chart_upper, self.__empty_label, options=Qt.FindDirectChildrenOnly)
        self.Graph_Offset = min((self.Graph_Offset + 1), (descriptor_list_length - 1))
        self.Visible_Graph_Count = 1
        self.update()

    def set_main_window_title ( self ):
        main_window = QtWidgets.QApplication.activeWindow()
        if (main_window is not None):
            main_window.setWindowTitle("CW_Remote" + " (" +
                                       Period_Span_NYC_Wall_Time(self.Period_Duration_Hours,
                                                                 self.Period_End_Hours_Ago) + ")")


class Main_Window ( QtWidgets.QMainWindow ):

    def __init__(self, **kwargs):
        super(Main_Window, self).__init__(**kwargs)

        self.setWindowTitle("CW_Remote" + " (" +
                            Period_Span_NYC_Wall_Time(Initial_Period_Duration_Hours,
                                                      Initial_Period_End_Hours_Ago) + ")")

        self.setContentsMargins(0, 0, 0, 0)
        self.cw_remote_screen_widget = CW_Remote_Screen(parent=self)
        self.cw_remote_screen_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.cw_remote_screen_widget)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = Main_Window()

    window.setContentsMargins(0, 0, 0, 0)

    window.resize(1280, 800)

    # window_size = window.frameSize()
    # desktop_geometry = PySide2.QtWidgets.QDesktopWidget().screenGeometry()
    # window.move((desktop_geometry.width() / 2) - (window_size.width() / 2),
    #             (desktop_geometry.height() / 2) - (window_size.height() / 2))

    window_rect = window.frameGeometry()
    desktop_center = QtWidgets.QDesktopWidget().screenGeometry().center()
    window_rect.moveCenter(desktop_center)
    window.move(window_rect.topLeft())

    window.show()

    sys.exit(app.exec_())
