from kivy.app import App

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

Duplex_Layout = True
Force_Duplex_Layout = False

curdir = dirname(__file__)

cw_remote_ini_file = open(join(curdir, "CW_Remote.ini"), "r")
cw_remote_ini_json = cw_remote_ini_file.read()
cw_remote_ini_file.close()

# Load initialization from the JSON ini file
cw_remote_ini = json.loads(cw_remote_ini_json, object_pairs_hook=OrderedDict)

cw_remote_layout = cw_remote_ini.get("layout", '')
if (cw_remote_layout == "paged"): Duplex_Layout = False
elif (cw_remote_layout == "duplex"): Duplex_Layout = True

if (Force_Duplex_Layout): Duplex_Layout = True

widget_descriptor_list = []

ini_widget_descriptor_list = cw_remote_ini.get("widget_descriptor_list", [])
for widget_descr in ini_widget_descriptor_list:
    this_widget_descriptor = widget_descr.copy()
    widget_descriptor_list.append(this_widget_descriptor)

if (len(widget_descriptor_list) < 2): 
    Duplex_Layout = False

if (Duplex_Layout):
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
    def build(self):
        Get_CloudWatch_Graphs()

        self.CloudWatch_Remote = BoxLayout(orientation='vertical')

        self.Control_Bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))

        self.Begin_Time_Slider = \
            Slider_Extended(min=-24, max=-1, value=-24, step=1, size_hint=(0.40, 1))
        self.Begin_Time_Slider.bind(value=self.on_begin_time_value_change)
        self.Begin_Time_Slider.bind(on_release=self.update)

        self.Begin_Time_Label = \
            Label(text=(str(int(round(self.Begin_Time_Slider.value))) + "H"), 
                  size_hint=(0.05, 1))

        self.Control_Bar.add_widget(self.Begin_Time_Label)
        self.Control_Bar.add_widget(self.Begin_Time_Slider)
        
        button_refresh = Button(text="Refresh", size_hint=(0.1, 1))
        button_refresh.bind(on_press=self.update)
        self.Control_Bar.add_widget(button_refresh)

        self.End_Time_Slider = \
            Slider_Extended(min=-23, max=0, value=0, step=1, size_hint=(0.40, 1))
        self.End_Time_Slider.bind(value=self.on_end_time_value_change)
        self.End_Time_Slider.bind(on_release=self.update)

        self.End_Time_Label = \
            Label(text=(str(int(round(self.End_Time_Slider.value))) + "H"), 
                  size_hint=(0.05, 1))

        self.Control_Bar.add_widget(self.End_Time_Slider)
        self.Control_Bar.add_widget(self.End_Time_Label)

        if (Duplex_Layout):
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
        
        return self.CloudWatch_Remote
        
    def on_begin_time_value_change(self, instance, begin_value, *args):
        relative_start_time_value = int(round(begin_value))
        if (relative_start_time_value >= int(round(self.End_Time_Slider.value))):
            relative_start_time_value = int(round(self.End_Time_Slider.value)) - 1
            self.Begin_Time_Slider.value = relative_start_time_value
        for widget_descriptor in widget_descriptor_list:
            widget_descriptor["start"] = "-PT" + str(abs(relative_start_time_value)) + "H"
        self.Begin_Time_Label.text = str(relative_start_time_value) + "H"
        
    def on_end_time_value_change(self, instance, end_value, *args):
        relative_end_time_value = int(round(end_value))
        if (relative_end_time_value <= int(round(self.Begin_Time_Slider.value))):
            relative_end_time_value = int(round(self.Begin_Time_Slider.value)) + 1
            self.End_Time_Slider.value = relative_end_time_value
        for widget_descriptor in widget_descriptor_list:
            widget_descriptor["end"] = "-PT" + str(abs(relative_end_time_value)) + "H"
        self.End_Time_Label.text = str(relative_end_time_value) + "H"
        
    def update(self, *args):
        Get_CloudWatch_Graphs()

        if (Duplex_Layout):
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


# Instantiate and run the kivy app
if __name__ == '__main__':
    Build_CloudWatch_Remote().run()
    