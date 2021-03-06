#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-

from __future__ import print_function
from __future__ import division

import kivy
kivy.require('1.9.0')

from kivy.config import Config
Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '800')

from kivy.app import App

from kivy.core.window import Window

from kivy.core.image import Image as CoreImage

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.carousel import Carousel

from kivy.clock import Clock

from os.path import join, dirname

from io import BytesIO

import datetime
import time

import boto3

import json

import re

from collections import OrderedDict

from functools import partial

cw_remote_duplex_layout = True
Force_Duplex_Layout = True

# There is a limit of 20 transactions per second for this API.
# Each GetMetricWidgetImage action has the following limits:
#     As many as 100 metrics in the graph.
#     Up to 100 KB uncompressed payload.

# If zero, no auto-refresh, if greater than zero, the auto-refresh interval in seconds
cw_remote_refresh_interval_seconds = 0 # (1 * 60)
Force_Refresh_Interval_Seconds = -1

curdir = dirname(__file__)

cw_remote_ini_file = open(join(curdir, "CW_Remote.ini"), "r")
cw_remote_ini_json = cw_remote_ini_file.read()
cw_remote_ini_file.close()

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
    widget_descriptor_list = widget_descriptor_list[:2]
else: 
    # Not duplex, make graphs "higher", i.e. more vertical resolution
    for widget_descr in widget_descriptor_list:
        widget_descr["height"] = 2 * widget_descr["height"]


ci_widget_image_list = []
for idx in range(len(widget_descriptor_list)):
    ci_widget_image_list.append(None)


# Initialize connection to CloudWatch.
cloudwatch_client = \
    boto3.client('cloudwatch',
                 aws_access_key_id=cw_remote_ini.get("aws_access_id", ''),
                 aws_secret_access_key=cw_remote_ini.get("aws_secret_key", ''),
                 region_name=cw_remote_ini.get("region_name", ''))


# Determine local wall time, this works for New York City
class Time_Zone (datetime.tzinfo):
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


# Fetch the AWS/CW Dashboard widget images
def Get_CloudWatch_Graphs ( ):
    global widget_descriptor_list, ci_widget_image_list

    for ci_widget_image in ci_widget_image_list:    
        if (ci_widget_image is not None): ci_widget_image.remove_from_cache()

    now_datetime_utc = datetime.datetime.now(UTC_Time_Zone)
    time_zone_offset_string = NYC_Wall_DateTime_Offset(now_datetime_utc)

    for idx, widget_descriptor in enumerate(widget_descriptor_list):
        widget_descriptor["timezone"] = time_zone_offset_string

        response = \
            cloudwatch_client.get_metric_widget_image(MetricWidget=json.dumps(widget_descriptor),
                                                      OutputFormat="png")

        # Avoid writing the PNG to file, load into the Image widget directly from memory
        data = BytesIO(bytearray(response["MetricWidgetImage"]))
        ci_widget_image_list[idx] = CoreImage(data, ext="png", 
                                              filename=("widget_image_" + str(idx) + ".png"))
        

# This slider extension allows the code to avoid the very expensive refreshes of ...
# ... the widget images until the user has stopped sliding the slider. Refresh then.
class Slider_Extended(Slider):
    def __init__(self, **kwargs):
        self.register_event_type('on_release')
        super(Slider_Extended, self).__init__(**kwargs)

    def on_release(self):
        pass

    def on_touch_up(self, touch):
        super(Slider_Extended, self).on_touch_up(touch)
        if touch.grab_current == self:
            self.dispatch('on_release')
            return True


# Build the app screen
class Build_CloudWatch_Remote ( App ):

    Period_Buttons = []
    Period_End_Buttons = []

    Period_Value = 24
    Period_End_Value = 0

    def __init__(self, **kwargs):
        super(Build_CloudWatch_Remote, self).__init__(**kwargs)
        Window.bind(on_key_down=self.on_keyboard_down)

        # Window.size = (1280, 800)

        # Automatically size widget images to fit screen real estate
        horizontal_size, vertical_size = Window.size
        # print ("h:", horizontal_size, "v:", vertical_size)
        for widget_descriptor in widget_descriptor_list:
            widget_descriptor["width"] = horizontal_size
            if (cw_remote_duplex_layout):
                widget_descriptor["height"] = int(round(vertical_size * 0.475))
            else:
                widget_descriptor["height"] = int(round(vertical_size * 2 * 0.475))

    def build(self):
        Get_CloudWatch_Graphs()

        self.CloudWatch_Remote = BoxLayout(orientation='vertical')

        self.Control_Bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))

        # self.Begin_Time_Slider = \
        #     Slider_Extended(min=-24, max=-1, value=-24, step=1, size_hint=(0.40, 1))
        # self.Begin_Time_Slider.bind(value=self.on_begin_time_value_change)
        # self.Begin_Time_Slider.bind(on_release=self.update)

        # self.Begin_Time_Label = \
        #     Label(text=(str(int(round(self.Begin_Time_Slider.value))) + "H"),
        #           size_hint=(0.05, 1))
        self.Period_Label = Label(text=(str(self.Period_Value) + "H"), size_hint=(0.05, 1))

        # self.Control_Bar.add_widget(self.Begin_Time_Label)
        self.Control_Bar.add_widget(self.Period_Label)
        # self.Control_Bar.add_widget(self.Begin_Time_Slider)
        for button_idx, button_value in enumerate([120, 96, 72, 48, 24, 20, 16, 12, 8, 6, 5, 4, 3, 2, 1]):
            period_button = Button(text=str(button_value))
            period_button.font_size = 14
            period_button.size_hint = (0.0375, 1)
            period_button.bind(on_press=partial(self.on_set_period, button_idx, button_value))
            self.Period_Buttons.append(period_button)
            self.Control_Bar.add_widget(period_button)
        
        button_refresh = Button(text="Refresh", size_hint=(0.075, 1))
        button_refresh.font_size = 14
        button_refresh.bind(on_press=self.update)
        self.Control_Bar.add_widget(button_refresh)

        for button_idx, button_value in enumerate([-72, -48, -36, -24, -12, -10, -8, -6, -5, -4, -3, -2, -1, 0]): # -96,
            end_button = Button(text=str(button_value))
            end_button.font_size = 14
            end_button.size_hint = (0.0375, 1)
            end_button.bind(on_press=partial(self.on_set_period_end, button_idx, button_value))
            self.Period_End_Buttons.append(end_button)
            self.Control_Bar.add_widget(end_button)

        # self.End_Time_Slider = \
        #     Slider_Extended(min=-23, max=0, value=0, step=1, size_hint=(0.40, 1))
        # self.End_Time_Slider.bind(value=self.on_end_time_value_change)
        # self.End_Time_Slider.bind(on_release=self.update)

        # self.End_Time_Label = \
        #     Label(text=(str(int(round(self.End_Time_Slider.value))) + "H"),
        #           size_hint=(0.05, 1))
        self.Period_End_Label = Label(text=(str(self.Period_End_Value) + "H"), size_hint=(0.05, 1))

        # self.Control_Bar.add_widget(self.End_Time_Slider)
        # self.Control_Bar.add_widget(self.End_Time_Label)
        self.Control_Bar.add_widget(self.Period_End_Label)

        if (cw_remote_duplex_layout):
            self.Upper_Widget_Box = BoxLayout(orientation='vertical', size_hint=(1, 0.475))
            self.Lower_Widget_Box = BoxLayout(orientation='vertical', size_hint=(1, 0.475))
        
            self.Upper_Widget_Box.add_widget(Image(texture=ci_widget_image_list[0].texture))
            self.Lower_Widget_Box.add_widget(Image(texture=ci_widget_image_list[1].texture))

            self.CloudWatch_Remote.add_widget(self.Upper_Widget_Box) 
            self.CloudWatch_Remote.add_widget(self.Control_Bar)
            self.CloudWatch_Remote.add_widget(self.Lower_Widget_Box)
        elif (len(widget_descriptor_list) > 1):
            self.Carousel_Widget = Carousel(direction='bottom') 
            for ci_widget_image in ci_widget_image_list:
                self.Carousel_Widget.add_widget(Image(texture=ci_widget_image.texture))

            self.CloudWatch_Remote.add_widget(self.Control_Bar)
            self.CloudWatch_Remote.add_widget(self.Carousel_Widget) 
        else:
            self.Upper_Widget_Box = BoxLayout(orientation='vertical', size_hint=(1, (2 * 0.475)))
            self.Upper_Widget_Box.add_widget(Image(texture=ci_widget_image_list[0].texture))

            self.CloudWatch_Remote.add_widget(self.Control_Bar)
            self.CloudWatch_Remote.add_widget(self.Upper_Widget_Box)

        if (cw_remote_refresh_interval_seconds >= 1):
            Clock.schedule_interval(self.update, cw_remote_refresh_interval_seconds)

        return self.CloudWatch_Remote

    def on_set_period(self, button_index, button_value, *args):
        self.Period_Value = button_value
        self.Period_Label.text = str(self.Period_Value) + "H"
        self.update_period_start_end()

    def on_set_period_end(self, button_index, button_value, *args):
        self.Period_End_Value = button_value
        self.Period_End_Label.text = str(self.Period_End_Value) + "H"
        self.update_period_start_end()

    def update_period_start_end(self):
        for widget_descriptor in widget_descriptor_list:
            widget_descriptor["start"] = "-PT" + str(abs(self.Period_Value) + abs(self.Period_End_Value)) + "H"
            widget_descriptor["end"] = "-PT" + str(abs(self.Period_End_Value)) + "H"
        self.update()

    # def on_begin_time_value_change(self, instance, begin_value, *args):
    #     relative_start_time_value = int(round(begin_value))
    #     if (relative_start_time_value >= int(round(self.End_Time_Slider.value))):
    #         relative_start_time_value = int(round(self.End_Time_Slider.value)) - 1
    #         self.Begin_Time_Slider.value = relative_start_time_value
    #     for widget_descriptor in widget_descriptor_list:
    #         widget_descriptor["start"] = "-PT" + str(abs(relative_start_time_value)) + "H"
    #     self.Begin_Time_Label.text = str(relative_start_time_value) + "H"
    #
    # def on_end_time_value_change(self, instance, end_value, *args):
    #     relative_end_time_value = int(round(end_value))
    #     if (relative_end_time_value <= int(round(self.Begin_Time_Slider.value))):
    #         relative_end_time_value = int(round(self.Begin_Time_Slider.value)) + 1
    #         self.End_Time_Slider.value = relative_end_time_value
    #     for widget_descriptor in widget_descriptor_list:
    #         widget_descriptor["end"] = "-PT" + str(abs(relative_end_time_value)) + "H"
    #     self.End_Time_Label.text = str(relative_end_time_value) + "H"
        
    def update(self, *args):
        Get_CloudWatch_Graphs()

        if (cw_remote_duplex_layout):
            self.Upper_Widget_Box.clear_widgets()
            self.Upper_Widget_Box.add_widget(Image(texture=ci_widget_image_list[0].texture))
            self.Lower_Widget_Box.clear_widgets()
            self.Lower_Widget_Box.add_widget(Image(texture=ci_widget_image_list[1].texture))
        elif (len(widget_descriptor_list) > 1):
            self.Carousel_Widget.clear_widgets()
            for ci_widget_image in ci_widget_image_list:
                self.Carousel_Widget.add_widget(Image(texture=ci_widget_image.texture))
        else:
            self.Upper_Widget_Box.clear_widgets()
            self.Upper_Widget_Box.add_widget(Image(texture=ci_widget_image_list[0].texture))
        
        self.CloudWatch_Remote.canvas.ask_update()

    def on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        # print("\nThe key", keycode, "have been pressed")
        # print(" - text is %r" % text)
        # print(" - modifiers are %r" % modifiers)
        # Support keyboard control of carousel on OS-X
        if ((keycode == 81) or (keycode == 79)): self.Carousel_Widget.load_next()
        elif ((keycode == 82) or (keycode == 80)): self.Carousel_Widget.load_previous()


# Instantiate and run the kivy app
if __name__ == '__main__':
    Build_CloudWatch_Remote().run()
    