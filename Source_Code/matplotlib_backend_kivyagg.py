'''
Backend KivyAgg
=====

.. image:: images/backend_agg_example.jpg
    :align: right

The :class:`FigureCanvasKivyAgg` widget is used to create a matplotlib graph.
The render will cover the whole are of the widget unless something different is
specified using a :meth:`blit`.
When you are creating a FigureCanvasKivyAgg widget, you must at least
initialize it with a matplotlib figure object. This class uses agg to get a
static image of the plot and then the image is render using a
:class:`~kivy.graphics.texture.Texture`. See backend_kivy documentation for
more information since both backends can be used in the exact same way.


Examples
--------

Example of a simple Hello world matplotlib App::

    fig, ax = plt.subplots()
    ax.text(0.6, 0.5, "hello", size=50, rotation=30.,
            ha="center", va="center",
            bbox=dict(boxstyle="round",
                      ec=(1., 0.5, 0.5),
                      fc=(1., 0.8, 0.8),
                      )
            )
    ax.text(0.5, 0.4, "world", size=50, rotation=-30.,
            ha="right", va="top",
            bbox=dict(boxstyle="square",
                      ec=(1., 0.5, 0.5),
                      fc=(1., 0.8, 0.8),
                      )
            )
    canvas = FigureCanvasKivyAgg(figure=fig)

The object canvas can be added as a widget into the kivy tree widget.
If a change is done on the figure an update can be performed using
:meth:`~kivy.ext.mpl.backend_kivyagg.FigureCanvasKivyAgg.draw`.::

    # update graph
    canvas.draw()

The plot can be exported to png with
:meth:`~kivy.ext.mpl.backend_kivyagg.FigureCanvasKivyAgg.print_png`, as an
argument receives the `filename`.::

    # export to png
    canvas.print_png("my_plot.png")


Backend KivyAgg Events
-----------------------

The events available are the same events available from Backend Kivy.::

    def my_callback(event):
        print('press released from test', event.x, event.y, event.button)

    fig.canvas.mpl_connect('mpl_event', my_callback)

'''

# from __future__ import (absolute_import, division, print_function,
#                         unicode_literals)

# __all__ = ('FigureCanvasKivyAgg')

from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.behaviors import FocusBehavior

import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backend_bases import FigureCanvasBase, Event

from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle, Color

# register_backend('png', 'backend_kivyagg', 'PNG File Format')
#
# toolbar = None
# my_canvas = None

class FigureCanvasKivy ( FocusBehavior, Widget, FigureCanvasBase ):
    '''FigureCanvasKivy class. See module documentation for more information.
    '''

    def __init__(self, figure, **kwargs):
        Window.bind(mouse_pos=self._on_mouse_pos)
        self.bind(size=self._on_size_changed)
        self.bind(pos=self._on_pos_changed)
        self.entered_figure = True
        self.figure = figure
        super(FigureCanvasKivy, self).__init__(figure=self.figure, **kwargs)

    def draw(self):
        '''Draw the figure using the KivyRenderer
        '''
        self.clear_widgets()
        self.canvas.clear()
        self._renderer = RendererKivy(self)
        self.figure.draw(self._renderer)

    def on_touch_down(self, touch):
        '''Kivy Event to trigger the following matplotlib events:
           `motion_notify_event`, `scroll_event`, `button_press_event`,
           `enter_notify_event` and `leave_notify_event`
        '''
        newcoord = self.to_widget(touch.x, touch.y, relative=True)
        x = newcoord[0]
        y = newcoord[1]

        if super(FigureCanvasKivy, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos):
            self.motion_notify_event(x, y, guiEvent=None)

            touch.grab(self)
            if 'button' in touch.profile and touch.button in ("scrollup", "scrolldown",):
                self.scroll_event(x, y, 5, guiEvent=None)
            else:
                self.button_press_event(x, y, self.get_mouse_button(touch),
                                        dblclick=False, guiEvent=None)
            if self.entered_figure:
                self.enter_notify_event(guiEvent=None, xy=None)
        else:
            if not self.entered_figure:
                self.leave_notify_event(guiEvent=None)
        return False

    def on_touch_move(self, touch):
        '''Kivy Event to trigger the following matplotlib events:
           `motion_notify_event`, `enter_notify_event` and `leave_notify_event`
        '''
        newcoord = self.to_widget(touch.x, touch.y, relative=True)
        x = newcoord[0]
        y = newcoord[1]
        inside = self.collide_point(touch.x, touch.y)
        if inside:
            self.motion_notify_event(x, y, guiEvent=None)
        if not inside and not self.entered_figure:
            self.leave_notify_event(guiEvent=None)
            self.entered_figure = True
        elif inside and self.entered_figure:
            self.enter_notify_event(guiEvent=None, xy=(x, y))
            self.entered_figure = False
        return False

    def get_mouse_button(self, touch):
        '''Translate kivy convention for left, right and middle click button
           into matplotlib int values: 1 for left, 2 for middle and 3 for
           right.
        '''
        if 'button' in touch.profile:
            if touch.button == "left":
                return 1
            elif touch.button == "middle":
                return 2
            elif touch.button == "right":
                return 3
        return -1

    def on_touch_up(self, touch):
        '''Kivy Event to trigger the following matplotlib events:
           `scroll_event` and `button_release_event`.
        '''
        newcoord = self.to_widget(touch.x, touch.y, relative=True)
        x = newcoord[0]
        y = newcoord[1]
        if touch.grab_current is self:
            if 'button' in touch.profile and touch.button in ("scrollup", "scrolldown",):
                self.scroll_event(x, y, 5, guiEvent=None)
            else:
                self.button_release_event(x, y, self.get_mouse_button(touch), guiEvent=None)
            touch.ungrab(self)
        else:
            return super(FigureCanvasKivy, self).on_touch_up(touch)
        return False

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        '''Kivy event to trigger matplotlib `key_press_event`.
        '''
        self.key_press_event(keycode[1], guiEvent=None)
        return super(FigureCanvasKivy, self).keyboard_on_key_down(window,
                                                    keycode, text, modifiers)

    def keyboard_on_key_up(self, window, keycode):
        '''Kivy event to trigger matplotlib `key_release_event`.
        '''
        self.key_release_event(keycode[1], guiEvent=None)
        return super(FigureCanvasKivy, self).keyboard_on_key_up(window, keycode)

    def _on_mouse_pos(self, *args):
        '''Kivy Event to trigger the following matplotlib events:
           `motion_notify_event`, `leave_notify_event` and
           `enter_notify_event`.
        '''
        pos = args[1]
        newcoord = self.to_widget(pos[0], pos[1], relative=True)
        x = newcoord[0]
        y = newcoord[1]
        inside = self.collide_point(*pos)
        if inside:
            self.motion_notify_event(x, y, guiEvent=None)
        if not inside and not self.entered_figure:
            self.leave_notify_event(guiEvent=None)
            self.entered_figure = True
        elif inside and self.entered_figure:
            self.enter_notify_event(guiEvent=None, xy=(pos[0], pos[1]))
            self.entered_figure = False

    def enter_notify_event(self, guiEvent=None, xy=None):
        event = Event('figure_enter_event', self, guiEvent)
        self.callbacks.process('figure_enter_event', event)

    def leave_notify_event(self, guiEvent=None):
        event = Event('figure_leave_event', self, guiEvent)
        self.callbacks.process('figure_leave_event', event)

    def _on_pos_changed(self, *args):
        self.draw()

    def _on_size_changed(self, *args):
        '''Changes the size of the matplotlib figure based on the size of the
           widget. The widget will change size according to the parent Layout
           size.
        '''
        w, h = self.size
        dpival = self.figure.dpi
        winch = float(w) / dpival
        hinch = float(h) / dpival
        self.figure.set_size_inches(winch, hinch, forward=False)
        self.resize_event()
        self.draw()

    def callback(self, *largs):
        self.draw()

    def blit(self, bbox=None):
        '''If bbox is None, blit the entire canvas to the widget. Otherwise
           blit only the area defined by the bbox.
        '''
        self.blitbox = bbox

    # filetypes = FigureCanvasBase.filetypes.copy()
    # filetypes['png'] = 'Portable Network Graphics'
    #
    # def print_png(self, filename, *args, **kwargs):
    #     '''Call the widget function to make a png of the widget.
    #     '''
    #     fig = FigureCanvasAgg(self.figure)
    #     FigureCanvasAgg.draw(fig)
    #
    #     l, b, w, h = self.figure.bbox.bounds
    #     texture = Texture.create(size=(w, h))
    #     texture.blit_buffer(bytes(fig.get_renderer().buffer_rgba()),
    #                             colorfmt='rgba', bufferfmt='ubyte')
    #     texture.flip_vertical()
    #     img = Image(texture)
    #     img.save(filename)
    #
    # def get_default_filetype(self):
    #     return 'png'
    #
    # def new_timer(self, *args, **kwargs):
    #     """
    #     Creates a new backend-specific subclass of :class:`backend_bases.Timer`.
    #     This is useful for getting periodic events through the backend's native
    #     event loop. Implemented only for backends with GUIs.
    #     optional arguments:
    #     *interval*
    #       Timer interval in milliseconds
    #     *callbacks*
    #       Sequence of (func, args, kwargs) where func(*args, **kwargs) will
    #       be executed by the timer every *interval*.
    #     """
    #     return TimerKivy(*args, **kwargs)

class FigureCanvasKivyAgg ( FigureCanvasKivy, FigureCanvasAgg ):
    '''
    FigureCanvasKivyAgg class. See module documentation for more information.
    '''

    def __init__(self, figure, **kwargs):
        self.figure = figure
        self.bind(size=self._on_size_changed)
        super(FigureCanvasKivyAgg, self).__init__(figure=self.figure, **kwargs)
        self.img_texture = None
        self.img_rect = None
        self.blit()

    def draw(self):
        '''
        Draw the figure using the agg renderer
        '''
        self.canvas.clear()
        FigureCanvasAgg.draw(self)
        if self.blitbox is None:
            l, b, w, h = self.figure.bbox.bounds
            w, h = int(w), int(h)
            buf_rgba = self.get_renderer().buffer_rgba()
        else:
            bbox = self.blitbox
            l, b, r, t = bbox.extents
            w = int(r) - int(l)
            h = int(t) - int(b)
            t = int(b) + h
            reg = self.copy_from_bbox(bbox)
            buf_rgba = reg.to_string()
        texture = Texture.create(size=(w, h))
        texture.flip_vertical()
        color = self.figure.get_facecolor()
        with self.canvas:
            Color(*color)
            Rectangle(pos=self.pos, size=(w, h))
            Color(1.0, 1.0, 1.0, 1.0)
            self.img_rect = Rectangle(texture=texture, pos=self.pos,
                                      size=(w, h))
        texture.blit_buffer(bytes(buf_rgba), colorfmt='rgba', bufferfmt='ubyte')
        self.img_texture = texture

    # filetypes = FigureCanvasKivy.filetypes.copy()
    # filetypes['png'] = 'Portable Network Graphics'

    def _on_pos_changed(self, *args):
        if self.img_rect is not None:
            self.img_rect.pos = self.pos

    def _print_image(self, filename, *args, **kwargs):
        '''Write out format png. The image is saved with the filename given.
        '''
        pass
        # l, b, w, h = self.figure.bbox.bounds
        # img = None
        # if self.img_texture is None:
        #     texture = Texture.create(size=(w, h))
        #     texture.blit_buffer(bytes(self.get_renderer().buffer_rgba()),
        #                         colorfmt='rgba', bufferfmt='ubyte')
        #     texture.flip_vertical()
        #     img = Image(texture)
        # else:
        #     img = Image(self.img_texture)
        # img.save(filename)
