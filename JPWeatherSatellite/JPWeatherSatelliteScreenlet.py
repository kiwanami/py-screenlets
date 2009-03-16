#!/usr/bin/env python

#  JPWeatherSatelliteScreenlet (c) SAKURAI Masashi 2009 <m.sakurai@kiwanami.net>
#
# INFO:
# - Show the weather satellite images.
# 

from __future__ import with_statement

import screenlets
from screenlets.options import StringOption, IntOption, FloatOption

import webbrowser
import gtk
import gobject
import pango
import cairo
from datetime import datetime,timedelta
from urllib import urlretrieve,urlcleanup
import sys, traceback

class JPWeatherSatelliteScreenlet (screenlets.Screenlet):
	"""A Screenlet that displays the weather satellite images from the JMA Web site (http://www.jma.go.jp/jp/gms/)"""
	
	# --------------------------------------------------------------------------
	# meta-info, options
	# --------------------------------------------------------------------------
	
	__name__		= 'JPWeatherSatelliteScreenlet'
	__version__		= '0.1'
	__author__		= 'SAKURAI Masashi 2009'
	__desc__		= __doc__
	
	# attributes
	__current_image = None
        __current_url = None
	__timeout = None
        __has_updated = False
        __timestr = ""
        __click_pos = [-1,-1]
	
	# editable options
        base_url = 'http://www.jma.go.jp/jp/gms/imgs/0/%(type)s/1/%(time)s-00.png'
        image_type = 'infrared'
        update_interval = 120
	
	# --------------------------------------------------------------------------
	# constructor and internals
	# --------------------------------------------------------------------------
	
	def __init__ (self, **keyword_args):
		screenlets.Screenlet.__init__(self, width=400, height=400, drag_drop=True,uses_theme=False, **keyword_args)
		self.theme_name = "default"
		self.add_default_menuitems()
		self.add_options_group('JPWeatherSatellite', 'JPWeatherSatellite-related settings ...')
		self.add_option(StringOption('JPWeatherSatellite', 'image_type', self.image_type, 'Image Type', 'infrared / visible / watervapor'))
		self.add_option(IntOption('JPWeatherSatellite', 'update_interval', self.update_interval,'update interval time (minutes)', 'update interval time (minutes)',min=1, max=300),realtime=False)
                self.update_image()
                self.set_update_interval(self.update_interval)

	def set_update_interval (self, interval):
		"""Set the update-time in minutes."""
		if self.__timeout:
			gobject.source_remove(self.__timeout)
                print "update interval : %s" % interval
		self.__timeout = gobject.timeout_add(interval*60*1000, self.update)

	def update (self):
		if self.__has_updated == False :
			self.__has_updated = True
                        try:
                                print "timer event : %s" % datetime.now()
                                self.update_image()
                        finally:
                                self.__has_updated = False
		return True

        def on_after_set_atribute(self,name, value):
                print name + ' is going to change from ' + str(value)
		if name == "local_code":
			if value != '' and value != self.local_code:
                                print "Setting local_code for JPWeatherSatelliteScreenlet: %s" % value
                                self.update_image()
                elif name == "update_interval":
			if value <= 0:
                                value = 1
                        self.set_update_interval(value)

        def update_image(self):
                curtime = datetime.now() + timedelta(minutes=-30)
                tmin = '00' if curtime.minute < 30 else '30'
                timedata = (curtime.year,curtime.month,curtime.day,curtime.hour,tmin)
                timestr = '%04d%02d%02d%02d%s' % timedata
                nurl = self.base_url % {'type':self.image_type,'time':timestr}
                if self.__current_url == nurl:
                        return True
                self.__current_url = nurl

		try:
                        tfile = urlretrieve(self.__current_url)
                        if tfile and tfile[1].gettype().find('image') >= 0:
                                print "image [%s] from %s" % (tfile,nurl)
                                img = cairo.ImageSurface.create_from_png(tfile[0])
                                if img:
                                        if self.__current_image:
                                                self.__current_image.finish()
                                                del self.__current_image
                                        self.width = img.get_width()
                                        self.height = img.get_height()
                                        self.__current_image = img
                                        self.__timestr = '%04d/%02d/%02d %02d:%s' % timedata
                                        self.redraw_canvas()
                                        self.set_update_interval(self.update_interval)
                                        return True
                        else:
                                with file(tfile[0]) as f:
                                        print f.read()
                        self.__current_url = None
                        self.set_update_interval(1)
		except Exception, ex:
			print 'Failed to load image "%s": %s (only PNG images supported yet)' % (self.__current_url, ex)
                        traceback.print_exc()
                finally:
                        urlcleanup()
		return False
		
	# --------------------------------------------------------------------------
	# Screenlet handlers
	# --------------------------------------------------------------------------
	
	def on_drag_enter (self, drag_context, x, y, timestamp):
		self.redraw_canvas()
	
	def on_drag_leave (self, drag_context, timestamp):
		self.redraw_canvas()
	
	def on_draw (self, ctx):
		ctx.set_operator(cairo.OPERATOR_OVER)
		ctx.scale(self.scale, self.scale)
                ctx.save()	
		if self.dragging_over:
			ctx.set_operator(cairo.OPERATOR_XOR)
		if self.__current_image:
			ctx.set_source_surface(self.__current_image, 0, 0)
                        ctx.paint()
                        self.draw_title(ctx,self.__timestr)
                else:
                        color_back = (0.0, 0.0, 0.0, 0.65)
                        ctx.set_source_rgba(color_back[0],color_back[1],
                                            color_back[2],color_back[3])
                        self.draw_rounded_rectangle(ctx,0,0,5,self.width,self.height)
                        self.draw_title(ctx,'Could not get image...')
                ctx.restore()

        def draw_title(self,ctx,title):
                color_title = (1.0, 1.0, 1.0, 1)
                font_title = "FreeSans"
                ctx.set_source_rgba(color_title[0],color_title[1],
                                    color_title[2],color_title[3])
                self.draw_text(ctx, title, 5, 20,
                               font_title,25,self.width-20,pango.ALIGN_LEFT)

	def on_draw_shape (self, ctx):
		self.on_draw(ctx)

	def on_mouse_down (self, event):
                if event.button == 1 and event.x == self.__click_pos[0] and event.y == self.__click_pos[1]:
                        webbrowser.open_new_tab('http://www.jma.go.jp/jp/gms/')
                        self.__click_pos[0] = -1
                        self.__click_pos[1] = -1
                        return True
                if event.button == 1:
                        self.__click_pos[0] = event.x
                        self.__click_pos[1] = event.y
		return False

if __name__ == "__main__":
	import screenlets.session
	screenlets.session.create_session(JPWeatherSatelliteScreenlet)
