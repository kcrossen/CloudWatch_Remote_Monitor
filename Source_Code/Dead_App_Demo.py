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

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label

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

class Build_Crash_Test_Dummy ( App ):
    def __init__(self, **kwargs):
        super(Build_Crash_Test_Dummy, self).__init__(**kwargs)
        Window.bind(on_key_down=self.on_keyboard_down)

    def build(self):
        self.Crash_Test_Dummy = BoxLayout(orientation='vertical')

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

        import time
        self.Upper_Widget_Box = BoxLayout(orientation='vertical', size_hint=(1, 0.475))
        time.sleep(10)
        self.Lower_Widget_Box = BoxLayout(orientation='vertical', size_hint=(1, 0.475))
        time.sleep(10)

        self.Crash_Test_Dummy.add_widget(self.Upper_Widget_Box)
        self.Crash_Test_Dummy.add_widget(self.Control_Bar)
        self.Crash_Test_Dummy.add_widget(self.Lower_Widget_Box)

        return self.Crash_Test_Dummy
        
    def on_begin_time_value_change(self, instance, begin_value, *args):
        pass
    def on_end_time_value_change(self, instance, end_value, *args):
        pass
    def update(self, *args):
        pass
    def on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        pass

if __name__ == '__main__':
    Build_Crash_Test_Dummy().run()