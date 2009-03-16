#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This application is released under the GNU General Public License 
# v3 (or, at your option, any later version). You can find the full 
# text of the license under http://www.gnu.org/licenses/gpl.txt. 
# By using, editing and/or distributing this software you agree to 
# the terms and conditions of this license. 
# Thank you for using free software!

#  ClearCalendarScreenlet (c) Whise aka Helder Fraga
#  JPClearCalendarScreenlet (c) SAKURAI Masashi <m.sakurai@kiwanami.net>


import screenlets
from screenlets.options import StringOption, BoolOption, ColorOption
import cairo
import pango
import gtk
import gobject
import datetime
import locale
from screenlets import Plugins
iCal = Plugins.importAPI('iCal')
import sys

"""
//_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
//_/
//_/  CopyRight(C) K.Tsunoda(AddinBox) 2001 All Rights Reserved.
//_/  ( http://www.h3.dion.ne.jp/~sakatsu/index.htm )
//_/
//_/    この祝日判定コードは『Excel:kt関数アドイン』で使用しているものです。
//_/    この関数では、２００７年施行の改正祝日法(昭和の日)までを
//_/  　サポートしています(９月の国民の休日を含む)。
//_/
//_/  (*1)このコードを引用するに当たっては、必ずこのコメントも
//_/      一緒に引用する事とします。
//_/  (*2)他サイト上で本マクロを直接引用する事は、ご遠慮願います。
//_/      【 http://www.h3.dion.ne.jp/~sakatsu/holiday_logic.htm 】
//_/      へのリンクによる紹介で対応して下さい。
//_/  (*3)[ktHolidayName]という関数名そのものは、各自の環境に
//_/      おける命名規則に沿って変更しても構いません。
//_/  
//_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/

 追記 2007/May/26     SETOGUCHI Mitsuhiro  http://matatabi.homeip.net/

 このスクリプトは JavaScript 用判定コード
  http://www.h3.dion.ne.jp/~sakatsu/holiday_logic.htm#JS
 を元に、Python 向けに移植したものです。

 holiday_name() は、年、月、日の3つの整数の引数を取ります。
 不適切な値を与えると、 ValueError が発生します。
 与えた日付が日本において何らかの祝日であれば、その名前が Unicode で返ります。
 祝日でない場合は None が返ります。

サンプル

import jholiday
jholiday.holiday_name(2007, 4, 28)
None
jholiday.holiday_name(2007, 4, 29)
u'\u662d\u548c\u306e\u65e5'
print jholiday.holiday_name(2007, 4, 29).encode('euc-jp')
昭和の日
"""

MONDAY, TUESDAY, WEDNESDAY = 0, 1, 2

def _vernal_equinox(y):
    """整数で年を与えると、その年の春分の日が3月の何日であるかを返す"""
    if y <= 1947:
        d = 0
    elif y <= 1979:
        d = int(20.8357  +  0.242194 * (y - 1980)  -  int((y - 1980) / 4))
    elif y <= 2099:
        d = int(20.8431  +  0.242194 * (y - 1980)  -  int((y - 1980) / 4))
    elif y <= 2150:
        d = int(21.8510  +  0.242194 * (y - 1980)  -  int((y - 1980) / 4))
    else:
        d = 0

    return d

def _autumn_equinox(y):
    """整数で年を与えると、その年の秋分の日が9月の何日であるかを返す"""
    if y <= 1947:
        d = 0
    elif y <= 1979:
        d = int(23.2588  +  0.242194 * (y - 1980)  -  int((y - 1980) / 4))
    elif y <= 2099:
        d = int(23.2488  +  0.242194 * (y - 1980)  -  int((y - 1980) / 4))
    elif y <= 2150:
        d = int(24.2488  +  0.242194 * (y - 1980)  -  int((y - 1980) / 4))
    else:
        d = 0

    return d

def holiday_name(year, month, day):
    date = datetime.date(year, month, day)
    name = None

    if date < datetime.date(1948, 7, 20):
        return name

    # 1月
    if month == 1:
        if day == 1:
            name = u'元日'
        else:
            if year >= 2000:
                if int((day - 1) / 7) == 1 and date.weekday() == MONDAY:
                    name = u'成人の日'
            else:
                if day == 15:
                    name = u'成人の日'
    # 2月
    elif month == 2:
        if day == 11 and year >= 1967:
            name = u'建国記念の日'
        elif (year, month, day) == (1989, 2, 24):
            name = u'昭和天皇の大喪の礼'
    # 3月
    elif month == 3:
        if day == _vernal_equinox(year):
            name = u'春分の日'
    # 4月
    elif month == 4:
        if day == 29:
            if year >= 2007:
                name = u'昭和の日'
            elif year >= 1989:
                name = u'みどりの日'
            else:
                name = u'天皇誕生日'
        elif (year, month, day) == (1959, 4, 10):
            name = u'皇太子明仁親王の結婚の儀'
    # 5月
    elif month == 5:
        if day == 3:
            name = u'憲法記念日'
        elif day == 4:
            if year >= 2007:
                name = u'みどりの日'
            elif year >= 1986 and date.weekday() != MONDAY:
                name = u'国民の休日'
        elif day == 5:
            name = u'こどもの日'
        elif day == 6:
            if year >= 2007 and date.weekday() in (TUESDAY, WEDNESDAY):
                name = u'振替休日'
    # 6月
    elif month == 6:
        if (year, month, day) == (1993, 6, 9):
            name = u'皇太子徳仁親王の結婚の儀'
    # 7月
    elif month == 7:
        if year >= 2003:
            if int((day - 1) / 7) == 2 and date.weekday() == MONDAY:
                name = u'海の日'
        elif year >= 1996 and day == 20:
            name = u'海の日'
    # 9月
    elif month == 9:
        autumn_equinox = _autumn_equinox(year)
        if day == autumn_equinox:
            name = u'秋分の日'
        else:
            if year >= 2003:
                if int((day - 1) / 7) == 2 and date.weekday() == MONDAY:
                    name = u'敬老の日'
                elif date.weekday() == TUESDAY and day == autumn_equinox - 1:
                    name = u'国民の休日'
            elif year >= 1966 and day == 15:
                name = u'敬老の日'
    # 10月
    elif month == 10:
        if year >= 2000:
            if int((day - 1) / 7) == 1 and date.weekday() == MONDAY:
                name = u'体育の日'
        elif year >= 1966 and day == 10:
            name = u'体育の日'
    # 11月
    elif month == 11:
        if day == 3:
            name = u'文化の日'
        elif day == 23:
            name = u'勤労感謝の日'
        elif (year, month, day) == (1990, 11, 12):
            name = u'即位礼正殿の儀'
    # 12月
    elif month == 12:
        if day == 23 and year >= 1989:
            name = u'天皇誕生日'

    # 振替休日
    if not name and date.weekday() == MONDAY:
        prev = date + datetime.timedelta(days = -1)
        if holiday_name(prev.year, prev.month, prev.day):
            name = u'振替休日'

    return name


"""
//_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
//_/ CopyRight(C) K.Tsunoda(AddinBox) 2001 All Rights Reserved.
//_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
"""



class JPClearCalendarScreenlet(screenlets.Screenlet):
	"""A simple Japanese iCalendar Screenlet with month preview, you can scroll through other months too and view monthly events."""
	
	# default meta-info for Screenlets
	__name__ = 'JPClearCalendarScreenlet'
	__version__ = '0.4-1.0'
	__author__ = 'SAKURAI Masashi based on ClearCalendar by Helder Fraga aka Whise'
	__desc__ = 'A simple Japanese iCalendar Screenlet with month preview, you can scroll through other months too and view monthly events.'

	# internals
	__timeout = None
	__first_day = 0
	__day_names = []


	__buttons_pixmap = None
	__buttons_alpha = 0
	__buttons_timeout = None
	__button_pressed = 0
	__month_shift = 0

	# settings
	update_interval = 60*60
	first_weekday = ''
	enable_buttons = True
	reader = iCal.ICalReader()
	event1 = ''

	font_color = (1,1,1, 0.8)
	sat_font_color = (0.5,0.5,1, 0.8)
	sun_font_color = (1,0.5,0.5, 0.8)
        font_colors = []
	today_color = (1,0,0, 0.8)
	event_color = (0,1,0, 0.8)
	today_event_color = (0,0,1, 0.8)
	background_color = (0,0,0, 0.8)
	showevents = True
	today=datetime.datetime.now().strftime("%F")
	mypath = sys.argv[0][:sys.argv[0].find('JPClearCalendarScreenlet.py')].strip()
	icalpath = mypath + 'calendar.ics'
	p_layout = None
	# constructor
	def __init__(self, **keyword_args):
		screenlets.Screenlet.__init__(self, width=int(102*2), height=int(105*2),uses_theme=True, **keyword_args) 
		# get localized day names
		locale.setlocale(locale.LC_ALL, '');
		# Use Japanese week
		self.__day_names = ['日','月','火','水','木','金','土']
		self.first_weekday = self.__day_names[self.__first_day]
		# call super (and not show window yet)
		# set theme
		self.add_menuitem("icspath", "Ics file path")	
		self.add_menuitem("events", "View events")
		self.add_menuitem("mini", "Toggle view events")
		self.add_menuitem("update", "Update events")	
		self.theme_name = "default"
		# add settings
		self.add_options_group('iCalendar', 'Calendar specific options')
		self.add_option(StringOption('iCalendar', 'first_weekday', self.first_weekday,
			'First Weekday', 'The day to be shown in the leftmost column',
			choices = self.__day_names))
		self.add_option(BoolOption('iCalendar', 'enable_buttons', self.enable_buttons, 
			'Enable month shifting', 'Enable buttons selecting another months'))
		self.add_option(StringOption('iCalendar', 'icalpath', self.icalpath, 'iCalendar ics file path', 'The full path where the .ics file is located , local or url) ...'), realtime=False)
		self.add_option(BoolOption('iCalendar', 'showevents',bool(self.showevents), 'Show iCalendar events','Show iCalendar events'),realtime=False)
		self.add_option(ColorOption('iCalendar','font_color', 
			self.font_color, 'Text color', 'font_color'))
		self.add_option(ColorOption('iCalendar','background_color', 
			self.background_color, 'Back color(only with default theme)', 'only works with default theme'))
		self.add_option(ColorOption('iCalendar','today_color', 
			self.today_color, 'Today color', 'today_color'))
		self.add_option(ColorOption('iCalendar','event_color', 
			self.event_color, 'Event day color', 'event_color'))
		self.add_option(ColorOption('iCalendar','today_event_color', 
			self.today_event_color, 'Today event color', 'today_event_color'))
		# init the timeout functions
		self.update_interval = self.update_interval
		self.enable_buttons = self.enable_buttons
		self.reader.readURL(self.icalpath)
		self.showevents = self.showevents
                for i in range(7):
                        self.font_colors.append(self.font_color)
                self.font_colors[6] = self.sat_font_color
                self.font_colors[0] = self.sun_font_color
	# attribute-"setter", handles setting of attributes
	def __setattr__(self, name, value):
		# call Screenlet.__setattr__ in baseclass (ESSENTIAL!!!!)
		screenlets.Screenlet.__setattr__(self, name, value)
		# check for this Screenlet's attributes, we are interested in:
		if name == ('icalpath'):
			self.reader = iCal.ICalReader()
			self.reader.readURL(self.icalpath)
			if self.window:
				self.redraw_canvas()
		if name == "update_interval":
			if value > 0:
				self.__dict__['update_interval'] = value
				if self.__timeout:
					gobject.source_remove(self.__timeout)
				self.__timeout = gobject.timeout_add(value 
						* 1000, self.update)
			else:
				# TODO: raise exception!!!
				pass
		elif name == 'first_weekday':
			self.__first_day\
				= self.__day_names.index(self.first_weekday)
			self.update()
		elif name == 'enable_buttons':
			self.__dict__['enable_buttons'] = value
			if value == True and not self.__buttons_timeout:
				self.__buttons_timeout = gobject.timeout_add(100, 
						self.update_buttons)
			elif value == False and self.__buttons_timeout:
				gobject.source_remove(self.__buttons_timeout)
				self.__buttons_timeout = None
				self.__buttons_alpha = 0
				self.update()
	def on_init (self):
		print "Screenlet has been initialized."
		# add default menuitems
		self.add_default_menuitems()	
	
	def get_date_info(self):
		today = datetime.datetime.now()
		day = today.day
		month = today.month
		year = today.year
		# apply month shift
		if self.__month_shift:
			month += self.__month_shift
			if month > 12:
				year += int((month - 1) / 12)
				month -= (year - today.year) * 12
			elif month <= 0:
				year -= int((12 - month) / 12)
				month += (today.year - year) * 12
		# get first day of the updated month
		month_num = datetime.datetime.now().strftime("%m")
		first_day = datetime.date(year, month, 1)
		# get the month name
		month_name = first_day.strftime("%B")
		month_num = first_day.strftime("%m")
		# get the day count
		when = datetime.date(int(year), int(month), int(1))
		# get the first day of the month (mon, tues, etc..)
		first_day = when.strftime("%A")
		# find number of days in the month
		if month in (1, 3, 5, 7, 8, 10, 12):
			days_in_month = 31
		elif month <> 2:
			days_in_month = 30
		elif year%4 == 0:
			days_in_month = 29
		else:
			days_in_month = 28
		#find the first day of the month
		start_day = int(when.strftime("%u"))  
		if start_day == 7:				# and do calculations on it...
			start_day = 0   
		start_day = start_day + 1
	
		# return as array
		return [day, year, month_name, days_in_month, start_day,month_num]

	def on_map(self):
		if not self.__timeout:
			self.__timeout = gobject.timeout_add(self.__dict__['update_interval']
						* 1000, self.update)
		if self.__dict__['enable_buttons'] == True and not self.__buttons_timeout:
			self.__buttons_timeout = gobject.timeout_add(100, 
					self.update_buttons)
 
	def on_unmap(self):
		if self.__timeout:
			gobject.source_remove(self.__timeout)
			self.__timeout = None
		if self.__buttons_timeout:
			gobject.source_remove(self.__buttons_timeout)
			self.__buttons_timeout = None

	# timeout-functions
	def update(self):
		self.icalpath = self.icalpath
		self.redraw_canvas()
		return True

	def update_buttons(self):
		x, y = self.window.get_pointer()
		x /= (2*self.scale)
		y /= (2*self.scale)
		al_last = self.__buttons_alpha
		if x >= 0 and x < 100 and y >= 0 and y <= 15:	# top line
			self.__buttons_alpha = min(self.__buttons_alpha + 0.2, 1.0)
		else:
			self.__buttons_alpha = max(self.__buttons_alpha - 0.2, 0.0)
		if self.__buttons_alpha != al_last:
			self.redraw_canvas()
		return True

	def on_load_theme(self):
		self.init_buttons()

	def on_scale(self):

		if self.window:
			self.init_buttons()

	# redraw button buffer. FIXME: the pixmap is used to enable alpha-rendering of the SVGs.
	def init_buttons(self):
		if self.__buttons_pixmap:
			del self.__buttons_pixmap
		self.__buttons_pixmap = gtk.gdk.Pixmap(self.window.window, int(self.width 
			* (2*self.scale)), int(self.height * (2*self.scale)), -1)
		ctx = self.__buttons_pixmap.cairo_create()
		self.clear_cairo_context(ctx)
		ctx.scale(2 *self.scale, 2* self.scale)
		ctx.set_operator(cairo.OPERATOR_OVER)
		self.theme.render(ctx,'buttons-dim')
		ctx.translate(0, 50)	# bottom half
		self.theme.render(ctx,'buttons-press')
		del ctx

	def on_mouse_down(self, event):
		if self.enable_buttons and event.button == 1:
			if event.type == gtk.gdk.BUTTON_PRESS:
				return self.detect_button(event.x, event.y)
			else:
				return True
		return False

	def on_mouse_up(self, event):
		# do the active button's action
		if self.__button_pressed:
			if self.__button_pressed == 1:
				self.__month_shift -= 1
			elif self.__button_pressed == 2:
				self.__month_shift = 0
			elif self.__button_pressed == 3:
				self.__month_shift += 1
			self.__button_pressed = 0
			self.redraw_canvas()
		return False

	def detect_button(self, x, y):
		x /= (2*self.scale)
		y /= (2*self.scale)

		button_det = 0
		if y >= 5.5 and y <= 12.5:
			if x >= 8.5 and x <= 15.5:
				button_det = 1
			elif x >= 18.5 and x <= 25.5:
				button_det = 2
			elif x >= 28.5 and x <= 35.5:
				button_det = 3
		self.__button_pressed = button_det
		if button_det:
			self.redraw_canvas()
			return True	# we must return boolean for Screenlet.button_press
		else:
			return False

	def menuitem_callback(self, widget, id):
		screenlets.Screenlet.menuitem_callback(self, widget, id)

		if id == "events":
			screenlets.show_message(self,self.event1)
			self.redraw_canvas()
		if id=="icspath":
			self.show_edit_dialog()
			


		if id == "mini":
			self.showevents = not self.showevents
			self.redraw_canvas()
	
		if id=="update":
			
			self.update()
	
	def on_draw(self, ctx):
		# get data
		date = self.get_date_info() # [day, year, month_name, days_in_month, start_day, month_num]
                year_num = int(date[1])
                month_num = int(date[5])
		# set size
		ctx.scale(2*self.scale, 2*self.scale)
		# draw bg (if theme available)
		ctx.set_operator(cairo.OPERATOR_OVER)
		if self.theme:
			ctx.set_source_rgba(*self.background_color)
			if self.theme_name == 'default':self.draw_rounded_rectangle(ctx,0,1,8,100,82)
			try:self.theme.render(ctx,'date-bg')
			except:pass
			#self.theme['date-border.svg'].render_cairo(ctx)
		# draw buttons and optionally the pressed one
		if self.p_layout == None :
	
			self.p_layout = ctx.create_layout()
		else:
		
			ctx.update_layout(self.p_layout)
		if self.__buttons_pixmap:
			ctx.save()
			ctx.rectangle(0, 0, 100, 15)
			ctx.clip()
			ctx.identity_matrix()
			ctx.set_source_pixmap(self.__buttons_pixmap, 0, 0)
			ctx.paint_with_alpha(self.__buttons_alpha)
			ctx.restore()
			if self.__button_pressed:
				ctx.save()
				ctx.rectangle(26.5 + self.__button_pressed * 10, 0, 10, 15)
				ctx.clip()
				ctx.identity_matrix()
				# use bottom half of the pixmap
				ctx.set_source_pixmap(self.__buttons_pixmap, 0, -50 * 2* self.scale)
				ctx.paint()
				ctx.restore()
				
		# draw the calendar foreground
		if self.theme:
			ctx.save()
			ctx.translate(5,5)
			self.p_layout = ctx.create_layout()
			p_fdesc = pango.FontDescription()
			p_fdesc.set_family_static("Tahoma")
			p_fdesc.set_size(5 * pango.SCALE)
			self.p_layout.set_font_description(p_fdesc)      ### draw the month
			self.p_layout.set_width((self.width - 10) * pango.SCALE)
			self.p_layout.set_markup('<b>' + date[2] + '</b>')
			ctx.set_source_rgba(*self.font_color)
			
			
			#ctx.show_layout(self.p_layout)
		
			ctx.translate(-100,0)
			self.p_layout.set_width((self.width - 10) * pango.SCALE)
			self.p_layout.set_alignment(pango.ALIGN_RIGHT)
			self.p_layout.set_markup("" + str(date[1])+'年 '+ date[2]+'  ') ### draw the year
			ctx.set_source_rgba(*self.font_color)
			ctx.show_layout(self.p_layout)

			ctx.restore()
			ctx.save()

			ctx.translate(0, 15)
			#self.theme['header-bg.svg'].render_cairo(ctx)  #draw the header background
			ctx.translate(6, 0)
			p_fdesc.set_size(4 * pango.SCALE)
			self.p_layout.set_font_description(p_fdesc) 
			#Draw header
			self.p_layout.set_alignment(pango.ALIGN_CENTER);
			self.p_layout.set_width(10*pango.SCALE);
			self.event1 = ''
			for i in range(7):
                                cofw = (i + self.__first_day) % 7
				dayname = self.__day_names[cofw]
				self.p_layout.set_markup("<b><span font_desc='Monospace'>" + dayname[:3] + '</span></b>') # use first letter
                                if len(self.font_colors) > 0:
                                        ctx.set_source_rgba(*(self.font_colors[cofw]))
				ctx.show_layout(self.p_layout)
				ctx.translate(13, 0)	# 6 + 6*13 + 6 = 100
			p_fdesc.set_size(6 * pango.SCALE)
			p_fdesc.set_family_static("FreeSans")

			self.p_layout.set_font_description(p_fdesc) 
			# Draw the day labels
			ctx.restore()
			row = 1

			day = (int(date[4]) + 7 - self.__first_day)%7
			if day == 0 :
				day = 7
			for x in range(date[3]):
				ctx.save()

				if row == 6:
					row = 1
				ctx.translate(6 + (day - 1)*13, 25 + 12*(row - 1))
				#print str(6 + (day - 1)*13)
				#print str( 25 + 12*(row - 1))
				if self.__month_shift == 0 and int(x)+1 == int(date[0]):
					ctx.set_source_rgba(*self.today_color)
					self.draw_rounded_rectangle(ctx,0,0,2,10,9)
				if self.showevents == True:
					for event in self.reader.events:
						
						myevent = str(event.startDate)
						myevent  = myevent[:myevent.find(' ')].strip()
	
						a = str(x +1)
						if len(a) == 1:
							a = '0' + a
					
						if myevent == str(date[1]) + '-' + str(date[5])+ '-' + str(a) :
							ctx.set_source_rgba(*self.event_color)
							self.draw_rounded_rectangle(ctx,0,0,2,10,9)
							if int(date[1]) >= int(self.today[:4]) or int(date[1]) >= int(self.today[:4]) and int(date[5]) >= int(self.today[5:7]) :
								
								self.event1 = self.event1 + '\n'+ str(date[1]) + '-' + str(date[5])+ '-' + str(a)+ ' - ' +str(event)
						if myevent == datetime.datetime.now().strftime("%F") and self.__month_shift == 0 and int(x)+1 == int(date[0]) :
							ctx.set_source_rgba(*self.today_event_color)
							self.draw_rounded_rectangle(ctx,0,0,2,10,9)

							self.event1 = self.event1 + '\n Today - '+ str(event)
				self.p_layout.set_markup( str(x+1) )
	
                                holiday = holiday_name(year_num, month_num, x+1)
                                if len(self.font_colors) > 0 and holiday == None:
                                        ctx.set_source_rgba(*(self.font_colors[(day-1+self.__first_day)%7]))
                                        ctx.show_layout(self.p_layout)
                                if holiday != None:
                                        ctx.set_source_rgba(*self.sun_font_color)
                                        ctx.show_layout(self.p_layout)
                                        ctx.translate(0, 7)
                                        self.p_layout.set_markup('<span size="1800">'+holiday+'</span>')
                                        ctx.show_layout(self.p_layout)
				if day == 7:
					day = 0
					row = row + 1
				day = day + 1
				ctx.restore()

	def show_edit_dialog(self):
		# create dialog
		dialog = gtk.Dialog("iCalendar ics path", self.window)
		dialog.resize(300, 100)
		dialog.add_buttons(gtk.STOCK_OK, gtk.RESPONSE_OK, 
			gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
		entrybox = gtk.Entry()
		entrybox.set_text(str(self.icalpath))
		dialog.vbox.add(entrybox)
		entrybox.show()	
		# run dialog
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			self.icalpath = entrybox.get_text()
			self.updated_recently = 1
		dialog.hide()
		self.update()

	def on_draw_shape(self,ctx):
		ctx.rectangle(0,0,self.width,self.height)
		ctx.fill()
		self.on_draw(ctx)

	def key_press(self, widget, event):
		key = gtk.gdk.keyval_name (event.keyval)
                if key == "Left":
                    self.__month_shift -= 1
                    self.redraw_canvas()
                if key == "Right":
                    self.__month_shift += 1
                    self.redraw_canvas()
                if key == "Up":
                    self.__month_shift -= 12
                    self.redraw_canvas()
                if key == "Down":
                    self.__month_shift += 12
                    self.redraw_canvas()
		return False

	def key_release(self, widget, event):
		return False
	

# If the program is run directly or passed as an argument to the python
# interpreter then create a Screenlet instance and show it
if __name__ == "__main__":
	import screenlets.session
	screenlets.session.create_session(JPClearCalendarScreenlet)
