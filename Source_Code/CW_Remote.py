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

from os.path import dirname, isdir, isfile, join, expanduser
import platform

from io import BytesIO

import datetime

import json

# import re

from collections import OrderedDict

from functools import partial

Testing_Bypass_Initialization = False # True # False # Should be False unless testing

if (not Testing_Bypass_Initialization):
    import boto3

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

Screen_Manager_App = True # True # False #
Function_Based_Control_Bar = True # True # False #

Defer_GetMetricWidgetImage = True # True # False #

# Class-based encapsulation doesn't work w/ Screen Manager
if (Screen_Manager_App and (not Testing_Bypass_Initialization)): Function_Based_Control_Bar = True

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

import simplejson

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
        try:
            documents_dir = "/system/storage/emulated/0/Documents"
            ini_dir = "CW_Remote"
            ini_directory = join(documents_dir, ini_dir)

            cw_remote_ini_file = open(join(ini_directory, "CW_Remote.ini"), "r")
            cw_remote_ini_json = cw_remote_ini_file.read()
            cw_remote_ini_file.close()

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


        ci_widget_image_list = []
        for idx in range(len(widget_descriptor_list)):
            ci_widget_image_list.append(None)


        if (not Testing_Bypass_Initialization):
            # Initialize connection to CloudWatch.
            cloudwatch_client = \
                boto3.client('cloudwatch',
                             aws_access_key_id=cw_remote_ini.get("aws_access_id", ''),
                             aws_secret_access_key=cw_remote_ini.get("aws_secret_key", ''),
                             region_name=cw_remote_ini.get("region_name", ''))

    except:
        # If initialization file is missing, don't build usual UI
        cw_remote_ini = None
else:
    cw_remote_ini = None


def bound ( low, high, value ):
    return max(low, min(high, value))


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
        self._period_value = 24
        self._period_end_value = 0
        super(Control_Bar, self).__init__(**kwargs)

    def build ( self, update_with_parameters_function ):
        self.update_with_parameters_function = update_with_parameters_function

        # No effect here, but leave as reminder
        self.control_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))

        self.period_label = \
            Label(text=self.period_value_display(self._period_value), size_hint=(0.075, 1))

        self.period_slider = \
            Slider_Extended(min=-1000, max=-1,
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
            Slider_Extended(min=-1000, max=0, value=0, step=1,
                            border_horizontal=[0, 0, 0, 0], padding=12, size_hint=(0.4, 1))
        self.period_end_slider.bind(value=self.on_period_end_value_change)
        self.period_end_slider.bind(on_release=self.trigger_on_release)

        self.period_end_label = \
            Label(text=(self.period_value_display(self._period_end_value) + " ago"), size_hint=(0.075, 1))

        self.control_bar.add_widget(self.period_label)
        self.control_bar.add_widget(self.period_slider)

        self.control_bar.add_widget(button_refresh)

        self.control_bar.add_widget(self.period_end_slider)
        self.control_bar.add_widget(self.period_end_label)

        return self.control_bar

    def period_value_display ( self, Period_Value ):
        period_value_string = ""
        if ((Period_Value // 24) > 0): period_value_string += str(Period_Value // 24) + "D"
        if (((Period_Value % 24) > 0) or (len(period_value_string) == 0)):
            if (len(period_value_string) > 0): period_value_string += " "
            period_value_string += str(Period_Value % 24) + "H"
        return period_value_string

    def on_period_value_change ( self, instance, period_slider_value, *args ):
        period_value_index = int(round(len(self.Period_Value_Steps) * (abs(period_slider_value) / 999)))
        self._period_value = self.Period_Value_Steps[bound(0, (len(self.Period_Value_Steps) -1), period_value_index)]
        self.period_label.text = (self.period_value_display(self._period_value))
        return True

    def on_period_end_value_change ( self, instance, period_end_slider_value, *args ):
        period_end_value_index = int(round(len(self.Period_End_Value_Steps) * (abs(period_end_slider_value) / 1000)))
        self._period_end_value = self.Period_End_Value_Steps[bound(0, (len(self.Period_End_Value_Steps) -1), period_end_value_index)]
        self.period_end_label.text = (self.period_value_display(self._period_end_value) + " ago")
        return True

    def trigger_on_release ( self, *args ):
        parameters = (self._period_value, self._period_end_value)
        self.update_with_parameters_function(*parameters)
        return True


# Build the app screen
class CW_Remote ( App ):

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

    def build_control_bar ( self ):
        control_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))

        period_label = \
            Label(text=self.display_period_value_text(self.Period_Value), size_hint=(0.075, 1),
                  id="period_label")

        period_slider = \
            Slider_Extended(min=-1000, max=-1,
                            value=-(999 * (self.Period_Value_Steps.index(self.Period_Value) /
                                           len(self.Period_Value_Steps))),
                            step=1,
                            border_horizontal=[0, 0, 0, 0], padding=12, size_hint=(0.4, 1),
                            id="period_slider")
        period_slider.bind(value=partial(self.on_period_value_change, period_label))
        period_slider.bind(on_release=self.update)

        button_refresh = Button(text="Refresh", size_hint=(0.05, 1))
        button_refresh.font_size = 14
        button_refresh.bind(on_press=self.update)

        period_end_slider = \
            Slider_Extended(min=-1000, max=0, value=0, step=1,
                            border_horizontal=[0, 0, 0, 0], padding=12, size_hint=(0.4, 1),
                            id="period_end_slider")
        period_end_label = \
            Label(text=(self.display_period_value_text(self.Period_End_Value) + " ago"), size_hint=(0.075, 1),
                  id="period_end_label")
        period_end_slider.bind(value=partial(self.on_period_end_value_change, period_end_label))
        period_end_slider.bind(on_release=self.update)

        control_bar.add_widget(period_label)
        control_bar.add_widget(period_slider)

        control_bar.add_widget(button_refresh)

        control_bar.add_widget(period_end_slider)
        control_bar.add_widget(period_end_label)

        return control_bar


    def build ( self ):
        self.title = "CW_Remote"

        self.Period_Value = 24
        self.Period_End_Value = 0

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
            self.Vertical_Graph_Height = vertical_size * Vertical_Graph_Height_Factor
            # print ("h:", horizontal_size, "v:", vertical_size)
            for widget_descriptor in widget_descriptor_list:
                widget_descriptor["width"] = int(round(horizontal_size * 0.98))
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

                # Neither of these encapsulation alternatives work w/ the screen manager
                if (Function_Based_Control_Bar):
                    # Function-based encapsulation
                    self.Control_Bar = self.build_control_bar()
                else:
                    # Class-based encapsulation
                    # Not as reliable when siblings are removed from parent.
                    self.Control_Bar = Control_Bar().build(self.update_with_parameters)
                self.Control_Bar.size_hint = (1, 0.04)


                self.Graph_Widget_Box =  BoxLayout(orientation='vertical', size_hint=(1, 0.96))

                self.Duplex_Upper_Graph_Box = BoxLayout(orientation='vertical', size_hint=(1, 0.5))
                self.Duplex_Lower_Graph_Box = BoxLayout(orientation='vertical', size_hint=(1, 0.5))

                self.Simplex_Lower_Graph_Box = BoxLayout(orientation='vertical', size_hint=(1, 1))

                if (self.Visible_Graph_Count == 2):
                    if (not Defer_GetMetricWidgetImage):
                        self.Duplex_Upper_Graph_Box.add_widget(Image(texture=self.get_cloudwatch_graph(self.Graph_Offset + 0).texture))
                        self.Duplex_Lower_Graph_Box.add_widget(Image(texture=self.get_cloudwatch_graph(self.Graph_Offset + 1).texture))

                    self.Graph_Widget_Box.add_widget(self.Duplex_Upper_Graph_Box)
                    self.Graph_Widget_Box.add_widget(self.Duplex_Lower_Graph_Box)

                    self.Visible_Graph_Count = 2

                else:
                    if (not Defer_GetMetricWidgetImage):
                        self.Simplex_Lower_Graph_Box.add_widget(Image(texture=self.get_cloudwatch_graph(self.Graph_Offset + 0).texture))

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

                if (Function_Based_Control_Bar):
                    # Function-based encapsulation
                    self.Duplex_Control_Bar = self.build_control_bar()
                else:
                    # Class-based encapsulation
                    self.Duplex_Control_Bar = Control_Bar().build(self.update_with_parameters)
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

                if (Function_Based_Control_Bar):
                    # Function-based encapsulation
                    self.Simplex_Control_Bar = self.build_control_bar()
                else:
                    # Class-based encapsulation
                    self.Simplex_Control_Bar = Control_Bar().build(self.update_with_parameters)
                self.Simplex_Control_Bar.size_hint = (1, 0.04)

                # Duplex
                self.Duplex_Upper_Graph_Box = BoxLayout(orientation='vertical', size_hint=(1, 0.48))
                self.Duplex_Lower_Graph_Box = BoxLayout(orientation='vertical', size_hint=(1, 0.48))

                if (not Defer_GetMetricWidgetImage):
                    self.Duplex_Upper_Graph_Box.add_widget(Image(texture=self.get_cloudwatch_graph(self.Graph_Offset + 0).texture))
                    self.Duplex_Lower_Graph_Box.add_widget(Image(texture=self.get_cloudwatch_graph(self.Graph_Offset + 1).texture))

                self.Duplex_CloudWatch_Remote_Panel.add_widget(self.Duplex_Upper_Graph_Box)
                self.Duplex_CloudWatch_Remote_Panel.add_widget(self.Duplex_Control_Bar)
                self.Duplex_CloudWatch_Remote_Panel.add_widget(self.Duplex_Lower_Graph_Box)

                self.CloudWatch_Remote_Duplex.add_widget(self.Duplex_Tab_Bar)
                self.CloudWatch_Remote_Duplex.add_widget(self.Duplex_CloudWatch_Remote_Panel)

                self.CloudWatch_Remote_Duplex_Screen.add_widget(self.CloudWatch_Remote_Duplex)
                self.CloudWatch_Remote.add_widget(self.CloudWatch_Remote_Duplex_Screen)

                # Simplex
                self.Simplex_Lower_Graph_Box = BoxLayout(orientation='vertical', size_hint=(1, (2 * 0.48)))
                if ((not Defer_GetMetricWidgetImage) and False):
                    self.Simplex_Lower_Graph_Box.add_widget(Image(texture=self.get_cloudwatch_graph(self.Graph_Offset + 0).texture))

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

    def on_period_value_change ( self, period_slider_value_label, instance, period_slider_value, *args ):
        period_value_index = int(round(len(self.Period_Value_Steps) * (abs(period_slider_value) / 999)))
        self.Period_Value = self.Period_Value_Steps[bound(0, (len(self.Period_Value_Steps) -1), period_value_index)]
        value_text = self.display_period_value_text(self.Period_Value)
        period_slider_value_label.text = value_text

    def on_period_end_value_change ( self, period_end_slider_value_label, instance, period_end_slider_value, *args ):
        period_end_value_index = int(round(len(self.Period_End_Value_Steps) * (abs(period_end_slider_value) / 1000)))
        self.Period_End_Value = self.Period_End_Value_Steps[bound(0, (len(self.Period_End_Value_Steps) -1), period_end_value_index)]
        value_text = self.display_period_value_text(self.Period_End_Value)
        period_end_slider_value_label.text = value_text + " ago"

    def update_with_parameters ( self, period_value, period_end_value, *args ):
        # print ("update_params:", period_value, period_end_value)
        self.Period_Value = period_value
        self.Period_End_Value = period_end_value
        self.update()

    def update ( self, *args ):
        if (not Testing_Bypass_Initialization):
            if (self.Visible_Graph_Count == 2):
                self.Duplex_Upper_Graph_Box.clear_widgets()
                self.Duplex_Upper_Graph_Box.add_widget(Image(texture=self.get_cloudwatch_graph(self.Graph_Offset + 0).texture))
                self.Duplex_Lower_Graph_Box.clear_widgets()
                self.Duplex_Lower_Graph_Box.add_widget(Image(texture=self.get_cloudwatch_graph(self.Graph_Offset + 1).texture))
            elif (self.Visible_Graph_Count == 1):
                self.Simplex_Lower_Graph_Box.clear_widgets()
                self.Simplex_Lower_Graph_Box.add_widget(Image(texture=self.get_cloudwatch_graph(self.Graph_Offset + 0).texture))

        self.CloudWatch_Remote.canvas.ask_update()

    # Fetch the AWS/CW Dashboard widget images
    def get_cloudwatch_graph ( self, Graph_Index ):
        global widget_descriptor_list, ci_widget_image_list

        # print ("graph:", Graph_Index)

        period_value = self.Period_Value
        period_end_value = self.Period_End_Value

        ci_widget_image = ci_widget_image_list[Graph_Index]
        if (ci_widget_image is not None): ci_widget_image.remove_from_cache()

        now_datetime_utc = datetime.datetime.now(UTC_Time_Zone)
        time_zone_offset_string = NYC_Wall_DateTime_Offset(now_datetime_utc)

        widget_descriptor = widget_descriptor_list[Graph_Index]
        widget_descriptor["start"] = "-PT" + str(abs(period_value) + abs(period_end_value)) + "H"
        widget_descriptor["end"] = "-PT" + str(abs(period_end_value)) + "H"

        widget_descriptor["timezone"] = time_zone_offset_string

        response = \
            cloudwatch_client.get_metric_widget_image(MetricWidget=json.dumps(widget_descriptor),
                                                      OutputFormat="png")

        # Avoid writing the PNG to file, load into the Image widget directly from memory
        data = BytesIO(bytearray(response["MetricWidgetImage"]))
        ci_widget_image_list[Graph_Index] = CoreImage(data, ext="png",
                                                      filename=("widget_image_" + str(Graph_Index) + ".png"))
        return ci_widget_image_list[Graph_Index]

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
                destination_child.value = -(999 * (self.Period_Value_Steps.index(self.Period_Value) /
                                                   len(self.Period_Value_Steps)))
            elif (destination_child.id == "period_end_slider"):
                destination_child.value = -(1000 * (self.Period_End_Value_Steps.index(self.Period_End_Value) /
                                                    len(self.Period_End_Value_Steps)))
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
        # if (self.Graph_Offset > 0):
        #     self.Graph_Offset -= 1
        # else:
        #     self.Graph_Offset = 0
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

        # if ((self.Graph_Offset + 1) < len(widget_descriptor_list)):
        #     self.Graph_Offset += 1
        self.update()

    def on_help ( self, *args ):
        print ("Help at the highest level")

    def on_keyboard_down ( self, instance, keyboard, keycode, text, modifiers ):
        # print("\nThe key", keycode, "have been pressed")
        # print(" - text is %r" % text)
        # print(" - modifiers are %r" % modifiers)
        # Support keyboard control of carousel on OS-X
        if (keycode == 44):
            self.toggle_duplex_versus_simplex()
        elif ((keycode == 81) or (keycode == 79)):
            self.on_next()
        elif ((keycode == 82) or (keycode == 80)):
            self.on_previous()

    def on_start(self, **kwargs):
        # print ("APP LOADED")
        if (Defer_GetMetricWidgetImage and (cw_remote_ini is not None)): Clock.schedule_once(self.update, 0.25)

# Instantiate and run the kivy app
if __name__ == '__main__':
    CW_Remote().run()
    