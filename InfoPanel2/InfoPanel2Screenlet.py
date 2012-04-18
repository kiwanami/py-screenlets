#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This application is released under the GNU General Public License
# v3 (or, at your option, any later version). You can find the full
# text of the license under http://www.gnu.org/licenses/gpl.txt.
# By using, editing and/or distributing this software you agree to
# the terms and conditions of this license.
# Thank you for using free software!

# InfoPanel2 (SysMonitor PLUS)
# Original (c) Michal Horejsek <horejsekmichal@gmail.com>
# 2011 Modified SAKURAI Masashi <m.sakurai at kiwanami.net>

import screenlets
from screenlets.options import StringOption, BoolOption , IntOption, FloatOption, ColorOption, FontOption, ImageOption
from screenlets import DefaultMenuItem
from screenlets import sensors
import pango
import gtk

import gobject
import cairo
import os
import sys
import urllib
import time

class InfoPanel2Screenlet( screenlets.Screenlet ):
  """InfoPanel2: Information about your computer and more."""

  ##########################################################
  ###         DEFAULT META-INFO FOR SCREENLETS           ###
  ##########################################################

  __name__ = 'InfoPanel2Screenlet'
  __version__ = '0.9.4-0'
  __author__ = 'SAKURAI Masashi'
  __desc__ = __doc__

  ##########################################################
  ###                      VARIABLES                     ###
  ##########################################################

  _updateInterval = 5
  _refresh = {}
  _refreshNet = {}
  _isTime = {}
  _debug = True

  _allUpdate = False
  _allUpdateNet = False
  _allUpdateWait = False
  _oldHour = 0
  _oldMinute = 0

  _linePx = 0
  _lineAppendPx = 0

  _themeModule = None
  width = 180
  _width = 180
  height = gtk.gdk.screen_height()
  ctxIcons = None

  clickData = {}
  clickDraw = False
  clickStart = 0
  clickEnd = 0

  ##### appearence #####
  font = 'FreeSans'
  fontHard = 'Monospace'
  fontSize = 9

  colorText =       [ 1.0, 1.0, 1.0, 1.0 ]
  colorBackground = [ 0.2, 0.2, 0.2, 0.5 ]

  showIcon = True
  expand = False
  starty = 5

  backgroundTransparency = True
  backgroundTransparencyLeft = False
  backgroundTransparencyStart = 0
  backgroundTransparencyStep = 0.5
  backgroundRadius = 10

  ##### graphs #####
  colorGraphBackground =  [ 0.2, 0.2, 0.2, 0.2 ]
  colorGraphForeground =  [ 0.5, 0.5, 0.5, 0.2 ]
  colorGraphVeryHigh =    [ 1.0, 0.0, 0.0, 0.4 ]
  colorGraphHigh =        [ 0.5, 0.0, 0.0, 0.4 ]
  colorGraphLow =         [ 0.0, 0.5, 0.0, 0.4 ]
  colorGraphVeryLow =     [ 0.0, 1.0, 0.0, 0.4 ]
  colorGraphHover =       [ 0.3, 0.7, 0.3, 0.4 ]

  graphTypes = [ 'none', 'line', 'line_color', 'boxes', 'boxes_color', ]
  graphTypeCpus = 'boxes_color'
  graphTypeNvidiaTemp = 'boxes_color'
  graphTypeMemory = 'boxes_color'
  graphTypeSwap = 'boxes_color'
  graphTypeDownUp = 'none'
  graphTypeDisks = 'boxes_color'
  graphTypeBattery = 'boxes_color'
  graphTypeWireless = 'boxes_color'

  graphVeryHigh = 90.0
  graphHigh = 75.0
  graphLow = 15.0
  graphVeryLow = 5.0

  graphBoxesWidth = 5
  graphBoxesSpace = 2

  # get net devices
  # @return list
  def getLocalIpDevices():
    devices = ['']
    for line in os.popen('/sbin/ifconfig').readlines():
      if line[0] != ' ':
        devices.append(line[0 : line[1:].find(' ')+1 ])
    print devices
    return devices
  # end getLocalIpDevices()

  ##### time #####
  time = ''
  ##### date #####
  date = ''
  datePhase = '0'
  ##### holiday #####
  holidayNum = 1
  holidayFiles = []
  holidayFile0 = ''
  holidayFile1 = ''
  holidayFile2 = ''
  holidayToday = ['', '', '']
  holidayTomorrow = ['', '', '']
  ##### weather #####
  weatherNum = 1
  weatherMetric = True
  weatherZip0 = 'EZXX0031'
  weatherZip1 = ''
  weatherZip2 = ''
  weatherForecast0 = True
  weatherForecast1 = True
  weatherForecast2 = True
  weatherLocateCity = {}
  weatherLocateState = {}
  weatherTmp = {}
  weatherLow = {}
  weatherHi = {}
  weatherIcon = {}
  ##### course #####
  courseNum = 1
  courseCourse = {}
  courseCodes = []
  courseNumber = {}
  courseCurrency = {}
  courseFrom0 = ''
  courseFrom1 = ''
  courseFrom2 = ''
  courseTo0 = ''
  courseTo1 = ''
  courseTo2 = ''
  ##### stock #####
  stockNum = 1
  stockSymbol0 = ''
  stockSymbol1 = ''
  stockSymbol2 = ''
  stockName = {}
  stockLastTrade = {}
  stockChange = {}
  ##### username #####
  username = ''
  hostname = ''
  ##### distro #####
  distro = ''
  ##### kernel #####
  kernel = ''
  ##### cpuname #####
  cpuname = ''
  ##### cpufrequency #####
  cpufrequency = []
  cpufrequencyOld = []
  ##### cpus #####
  cpusNum = sensors.cpu_get_nb_cpu()
  cpusNew = {}
  cpusOld = {}
  cpusLoad = {}
  ##### load #####
  load = ''
  loadOld = ''
  ##### nvidiaInfo #####
  nvidiaInfo = {}
  nvidiaInfoOld = {}
  nvidiaTemp = 0
  nvidiaTempMax = 80
  nvidiaShowGpu = True
  nvidiaShowRam = True
  nvidiaShowDriver = True
  nvidiaShowReolution = True
  nvidiaShowRefreshRate = True
  nvidiaShowGpuFrequency = True
  nvidiaShowMemFrequency = True
  nvidiaShowTemp = True
  ##### memory #####
  memory = ''
  memoryOld = ''
  ##### swap #####
  swap = ''
  swapOld = ''
  ##### localIp #####
  localIp = ''
  localIpOld = ''
  localIpDevice = ''
  localIpDevices = getLocalIpDevices()
  ##### externalIp #####
  externalIp = ''
  externalLocalIpOld = ''
  externalIpUrl = 'http://www.whatismyip.com/automation/n09230945.asp'
  ##### net #####
  netLoadUpload = 0.0
  netLoadDownload = 0.0
  netLoadMaxUpload = 512
  netLoadMaxDownload = 1024
  ##### upload #####
  upload = '0.0'
  uploadNew = 0
  uploadOld = 0
  ##### download #####
  download = '0.0'
  downloadNew = 0
  downloadOld = 0
  ##### netStatistic #####
  netStatisticUpload = '0.0'
  netStatisticDownload = '0.0'
  netStatisticUploadOld = '0.0'
  netStatisticDownloadOld = '0.0'
  netStatisticUploadTotal = 0.0
  netStatisticDownloadTotal = 0.0
  ##### rss #####
  rssNum = 1
  rssData = {}
  rssUrl0 = ''
  rssUrl1 = ''
  rssUrl2 = ''
  rssItems = 5
  rssBrowser = 'firefox'
  ##### disks #####
  disks = []
  disksOld = []
  disksTypes = [ 'usage', 'free', ]
  disksType = 'usage'
  ##### battery #####
  battery = ''
  batteryLoad = ''
  ##### wireless #####
  wireless = ''
  wirelessLoad = ''
  ##### processes #####
  processesNum = 10
  processesTypes = [ 'basic', 'extra', ]
  processesType = 'extra'
  processes = []
  processesOld = []
  ##### uptime #####
  uptime = ''
  ##### logintime #####
  logintime = ''
  logintimeStart = ''
  ##### temperature #####
  temperature1 = ''
  temperature1Old = ''
  ##### fan speed #####
  fan1 = ''
  fan1Old = ''

  __sensors = {}
  sensorsTime = True
  sensorsDate = True
  sensorsDateMoon = False
  sensorsHoliday = False
  sensorsWeather = True
  sensorsCourse = False
  sensorsStock = False
  sensorsUsername = False
  sensorsDistro = True
  sensorsKernel = True
  sensorsCpuname = True
  sensorsCpufrequency = False
  sensorsCpus = True
  sensorsCpus0 = False
  sensorsLoad = True
  sensorsNvidiaInfo = False
  sensorsMemory = True
  sensorsSwap = True
  sensorsLocalIp = True
  sensorsExternalIp = True
  sensorsUpload = True
  sensorsDownload = True
  sensorsNetStatistic = True
  sensorsRss = False
  sensorsDisks = True
  sensorsBattery = False
  sensorsWireless = False
  sensorsProcesses = True
  sensorsUptime = True
  sensorsLogintime = False
  sensorsTemperature1 = True
  sensorsFan1 = True

  __positions = {}
  positionsTime = 1
  positionsDate = 2
  positionsHoliday = 3
  positionsWeather = 4
  positionsCourse = 5
  positionsStock = 6
  positionsUsername = 7
  positionsDistro = 8
  positionsKernel = 9
  positionsCpuname = 10
  positionsCpufrequency = 11
  positionsCpus = 12
  positionsLoad = 13
  positionsNvidiaInfo = 14
  positionsMemory = 15
  positionsSwap = 16
  positionsLocalIp = 17
  positionsExternalIp = 18
  positionsUpload = 19
  positionsDownload = 20
  positionsNetStatistic = 21
  positionsRss = 22
  positionsDisks = 23
  positionsBattery = 24
  positionsWireless = 25
  positionsProcesses = 26
  positionsUptime = 27
  positionsLogintime = 28
  positionsTemperature1 = 29
  positionsFan1 = 30
  _numPositions = 30

  __spaces = {}
  spacesTime = 0
  spacesDate = 0
  spacesHoliday = 0
  spacesWeather = 0
  spacesCourse = 0
  spacesStock = 0
  spacesUsername = 0
  spacesDistro = 0
  spacesKernel = 0
  spacesCpuname = 0
  spacesCpufrequency = 0
  spacesCpus = 0
  spacesLoad = 0
  spacesNvidiaInfo = 0
  spacesMemory = 0
  spacesSwap = 0
  spacesLocalIp = 0
  spacesExternalIp = 0
  spacesUpload = 0
  spacesDownload = 0
  spacesNetStatistic = 0
  spacesRss = 0
  spacesDisks = 0
  spacesBattery = 0
  spacesWireless = 0
  spacesProcesses = 0
  spacesUptime = 0
  spacesLogintime = 0
  spacesTemperature1 = 0
  spacesFan1 = 0

  heights = {
    'time'          : 0,
    'date'          : 0,
    'holiday'       : 0,
    'weather'       : 0,
    'course'        : 0,
    'stock'         : 0,
    'username'      : 0,
    'distro'        : 0,
    'kernel'        : 0,
    'cpuname'       : 0,
    'cpufrequency'  : 0,
    'cpus'          : 0,
    'load'          : 0,
    'nvidiaInfo'    : 0,
    'memory'        : 0,
    'swap'          : 0,
    'localIp'       : 0,
    'externalIp'    : 0,
    'upload'        : 0,
    'download'      : 0,
    'netStatistic'  : 0,
    'rss'           : 0,
    'disks'         : 0,
    'battery'       : 0,
    'wireless'      : 0,
    'processes'     : 0,
    'uptime'        : 0,
    'logintime'     : 0,
    'temperature1'  : 0,
    'fan1'          : 0,
  }

  __buffers = {}

  # create arrays sensors and positions
  # @return void
  def createArrays( self ):
    self.__sensors = {
      'time'          : self.sensorsTime,
      'date'          : self.sensorsDate,
      'holiday'       : self.sensorsHoliday,
      'weather'       : self.sensorsWeather,
      'course'        : self.sensorsCourse,
      'stock'         : self.sensorsStock,
      'username'      : self.sensorsUsername,
      'distro'        : self.sensorsDistro,
      'kernel'        : self.sensorsKernel,
      'cpuname'       : self.sensorsCpuname,
      'cpufrequency'  : self.sensorsCpufrequency,
      'cpus'          : self.sensorsCpus,
      'load'          : self.sensorsLoad,
      'nvidiaInfo'    : self.sensorsNvidiaInfo,
      'memory'        : self.sensorsMemory,
      'swap'          : self.sensorsSwap,
      'localIp'       : self.sensorsLocalIp,
      'externalIp'    : self.sensorsExternalIp,
      'upload'        : self.sensorsUpload,
      'download'      : self.sensorsDownload,
      'netStatistic'  : self.sensorsNetStatistic,
      'rss'           : self.sensorsRss,
      'disks'         : self.sensorsDisks,
      'battery'       : self.sensorsBattery,
      'wireless'      : self.sensorsWireless,
      'processes'     : self.sensorsProcesses,
      'uptime'        : self.sensorsUptime,
      'logintime'     : self.sensorsLogintime,
      'temperature1'  : self.sensorsTemperature1,
      'fan1'          : self.sensorsFan1,
    }
    self.__positions = {
      'time'          : self.positionsTime,
      'date'          : self.positionsDate,
      'holiday'       : self.positionsHoliday,
      'weather'       : self.positionsWeather,
      'course'        : self.positionsCourse,
      'stock'         : self.positionsStock,
      'username'      : self.positionsUsername,
      'distro'        : self.positionsDistro,
      'kernel'        : self.positionsKernel,
      'cpuname'       : self.positionsCpuname,
      'cpufrequency'  : self.positionsCpufrequency,
      'cpus'          : self.positionsCpus,
      'load'          : self.positionsLoad,
      'nvidiaInfo'    : self.positionsNvidiaInfo,
      'memory'        : self.positionsMemory,
      'swap'          : self.positionsSwap,
      'localIp'       : self.positionsLocalIp,
      'externalIp'    : self.positionsExternalIp,
      'upload'        : self.positionsUpload,
      'download'      : self.positionsDownload,
      'netStatistic'  : self.positionsNetStatistic,
      'rss'           : self.positionsRss,
      'disks'         : self.positionsDisks,
      'battery'       : self.positionsBattery,
      'wireless'      : self.positionsWireless,
      'processes'     : self.positionsProcesses,
      'uptime'        : self.positionsUptime,
      'logintime'     : self.positionsLogintime,
      'temperature1'  : self.positionsTemperature1,
      'fan1'          : self.positionsFan1,
    }
    self.__spaces = {
      'time'          : self.spacesTime,
      'date'          : self.spacesDate,
      'holiday'       : self.spacesHoliday,
      'weather'       : self.spacesWeather,
      'course'        : self.spacesCourse,
      'stock'         : self.spacesStock,
      'username'      : self.spacesUsername,
      'distro'        : self.spacesDistro,
      'kernel'        : self.spacesKernel,
      'cpuname'       : self.spacesCpuname,
      'cpufrequency'  : self.spacesCpufrequency,
      'cpus'          : self.spacesCpus,
      'load'          : self.spacesLoad,
      'nvidiaInfo'    : self.spacesNvidiaInfo,
      'memory'        : self.spacesMemory,
      'swap'          : self.spacesSwap,
      'localIp'       : self.spacesLocalIp,
      'externalIp'    : self.spacesExternalIp,
      'upload'        : self.spacesUpload,
      'download'      : self.spacesDownload,
      'netStatistic'  : self.spacesNetStatistic,
      'rss'           : self.spacesRss,
      'disks'         : self.spacesDisks,
      'battery'       : self.spacesBattery,
      'wireless'      : self.spacesWireless,
      'processes'     : self.spacesProcesses,
      'uptime'        : self.spacesUptime,
      'logintime'     : self.spacesLogintime,
      'temperature1'  : self.spacesTemperature1,
      'fan1'          : self.spacesFan1,
    }
  # end createArray()

  # debug
  # @param  string bool
  # @return void
  def debug( self, msg = '', wait = False ):
    if self._debug:
      if wait:
        print 'Debug:', msg,
        try: input()
        except: pass
      else:
        print 'Debug:', msg
  # end debug

  # clear clickData
  # @param	string
  # @return void
  def clearClickData( self, key ):
    arr = []
    for x,y in self.clickData.iteritems():
      if key in x:
        arr.append( x )
    for key in arr:
      del self.clickData[ key ]
  # end clearClickData


  ##########################################################
  ###                                                    ###
  ###                    INIT FUNCTION                   ###
  ###                                                    ###
  ##########################################################

  # init
  # @param  list
  # @return void
  def __init__( self, **keyword_args ):
    screenlets.Screenlet.__init__( self, width=self.width, height=self.height, **keyword_args )

    # set theme
    theme_name = 'default'
    os.chdir( self.get_screenlet_dir() )
    sys.path.append( "themes" )
    self._themeModule = __import__( self.theme_name )
    # set timer
    self.timer = None
    # on start update all sensors
    self._allUpdate = True
    self._allUpdateNet = True
    self._allUpdateWait = True
    # create array
    self.createArrays()
    # set login time
    self.logintimeStart = time.time()
    # set list of files and course
    self.holidayFiles = os.listdir( self.get_screenlet_dir()+'/holidays' )
    self.getCourse()

    # options
    self.add_options_group( 'Appearance', '' )
    self.add_option( IntOption( 'Appearance', 'starty', self.starty, 'Start on [px]', '', min=0, max=500 ) )
    self.add_option( BoolOption( 'Appearance','expand', self.expand, 'Expand', '' ) )
    self.add_option( BoolOption( 'Appearance', 'showIcon', self.showIcon, 'Show icon', '' ) )
    self.add_option( FontOption( 'Appearance','font', self.font, 'Font', '' ) )
    self.add_option( ColorOption( 'Appearance','colorText', self.colorText, 'Text color', '' ) )
    self.add_option( ColorOption( 'Appearance','colorBackground', self.colorBackground, 'Background color', '' ) )
    self.add_option( BoolOption( 'Appearance', 'backgroundTransparency', self.backgroundTransparency, 'Background transparency', '' ) )
    self.add_option( BoolOption( 'Appearance', 'backgroundTransparencyLeft', self.backgroundTransparencyLeft, 'Background transparency invert', '' ) )
    self.add_option( IntOption( 'Appearance', 'backgroundTransparencyStart', self.backgroundTransparencyStart, 'Start background transparency', '', min=-self.width, max=255 ) )
    self.add_option( FloatOption( 'Appearance', 'backgroundTransparencyStep', self.backgroundTransparencyStep, 'Step background transparency', '', min=0.1, max=10.0 ) )
    self.add_option( IntOption( 'Appearance', 'backgroundRadius', self.backgroundRadius, 'Background radius', '', min=0, max=80 ) )

    self.add_options_group( 'Graphs', '' )
    self.add_option( ColorOption( 'Graphs','colorGraphForeground', self.colorGraphForeground, 'Foreground color', '' ) )
    self.add_option( ColorOption( 'Graphs','colorGraphBackground', self.colorGraphBackground, 'Background color', '' ) )
    self.add_option( ColorOption( 'Graphs','colorGraphVeryHigh', self.colorGraphVeryHigh, 'Very high color', '' ) )
    self.add_option( ColorOption( 'Graphs','colorGraphHigh', self.colorGraphHigh, 'High color', '' ) )
    self.add_option( ColorOption( 'Graphs','colorGraphLow', self.colorGraphLow, 'Low color', '' ) )
    self.add_option( ColorOption( 'Graphs','colorGraphVeryLow', self.colorGraphVeryLow, 'Very low color', '' ) )
    self.add_option( ColorOption( 'Graphs','colorGraphHover', self.colorGraphHover, 'Hover color', '' ) )
    self.add_option( IntOption( 'Graphs','graphVeryHigh', self.graphVeryHigh, 'Very high border', '', min=0, max=100 ) )
    self.add_option( IntOption( 'Graphs','graphHigh', self.graphHigh, 'High border', '', min=0, max=100 ) )
    self.add_option( IntOption( 'Graphs','graphLow', self.graphLow, 'Low border', '', min=0, max=100 ) )
    self.add_option( IntOption( 'Graphs','graphVeryLow', self.graphVeryLow, 'Very low border', '', min=0, max=100 ) )
    self.add_option( StringOption( 'Graphs', 'graphTypeCpus', self.graphTypeCpus, 'Cpus type', '', choices=self.graphTypes ) )
    self.add_option( StringOption( 'Graphs', 'graphTypeNvidiaTemp', self.graphTypeNvidiaTemp, 'nVidia temp type', '', choices=self.graphTypes ) )
    self.add_option( StringOption( 'Graphs', 'graphTypeMemory', self.graphTypeMemory, 'Memory type', '', choices=self.graphTypes ) )
    self.add_option( StringOption( 'Graphs', 'graphTypeSwap', self.graphTypeSwap, 'Swap type', '', choices=self.graphTypes ) )
    self.add_option( StringOption( 'Graphs', 'graphTypeDownUp', self.graphTypeDownUp, 'Down/Up type', '', choices=self.graphTypes ) )
    self.add_option( StringOption( 'Graphs', 'graphTypeDisks', self.graphTypeDisks, 'Disks type', '', choices=self.graphTypes ) )
    self.add_option( StringOption( 'Graphs', 'graphTypeBattery', self.graphTypeBattery, 'Battery type', '', choices=self.graphTypes ) )
    self.add_option( StringOption( 'Graphs', 'graphTypeWireless', self.graphTypeWireless, 'Wireless type', '', choices=self.graphTypes ) )
    self.add_option( IntOption( 'Graphs', 'graphBoxesWidth', self.graphBoxesWidth, 'Width boxs (only boxes type)', '', min=1, max=50 ) )
    self.add_option( IntOption( 'Graphs', 'graphBoxesSpace', self.graphBoxesSpace, 'Width spaces (only boxes type)', '', min=1, max=10 ) )

    # create & sort list of sensors
    list = [ [key,value] for key,value in self.__positions.iteritems() ]
    list.sort( self.mySort )

    counter = 1;
    self.add_options_group( 'Sensors '+str(counter), '' )
    for x,foo in enumerate( list, 1 ):
      sensor = foo[0]
      foo = foo[1]
      self.add_option( BoolOption( 'Sensors '+str(counter), 'sensors'+sensor[0].upper()+sensor[1:], self.__sensors[sensor], 'Show '+sensor, '' ) )
      if x%20 == 0:
        counter = counter+1
        self.add_options_group( 'Sensors '+str(counter), '' )
    self.add_option( BoolOption( 'Sensors '+str(counter), 'sensorsCpus0', self.sensorsCpus0, 'Show cpus0', '' ) )
    self.add_option( BoolOption( 'Sensors '+str(counter), 'sensorsDateMoon', self.sensorsDateMoon, 'Show moon', '' ) )

    counter = 1;
    self.add_options_group( 'Positions '+str(counter), '' )
    for x,foo in enumerate( list, 1 ):
      sensor = foo[0]
      position = foo[1]
      self.add_option( IntOption( 'Positions '+str(counter), 'positions'+sensor[0].upper()+sensor[1:], position, 'Positions '+sensor, '', min=1, max=self._numPositions ) )
      if x%20 == 0:
        counter = counter+1
        self.add_options_group( 'Positions '+str(counter), '' )

    counter = 1;
    self.add_options_group( 'Spaces '+str(counter), '' )
    for x,foo in enumerate( list, 1 ):
      sensor = foo[0]
      foo = foo[1]
      self.add_option( IntOption( 'Spaces '+str(counter), 'spaces'+sensor[0].upper()+sensor[1:], self.__spaces[sensor], 'Spaces '+sensor, '', min=0, max=50 ) )
      if x%20 == 0:
        counter = counter+1
        self.add_options_group( 'Spaces '+str(counter), '' )

    self.add_options_group( 'Holiday', '' )
    self.add_option( IntOption( 'Holiday','holidayNum', self.holidayNum, 'Num holidays', '', min=1, max=3 ) )
    self.add_option( StringOption( 'Holiday', 'holidayFile0', self.holidayFile0, 'Holiday file 1', '', choices=self.holidayFiles ) )
    self.add_option( StringOption( 'Holiday', 'holidayFile1', self.holidayFile1, 'Holiday file 2', '', choices=self.holidayFiles ) )
    self.add_option( StringOption( 'Holiday', 'holidayFile2', self.holidayFile2, 'Holiday file 3', '', choices=self.holidayFiles ) )

    self.add_options_group( 'Weather', '' )
    self.add_option( BoolOption( 'Weather', 'weatherMetric', self.weatherMetric, 'Use metric', '' ) )
    self.add_option( IntOption( 'Weather','weatherNum', self.weatherNum, 'Num weathers', '', min=1, max=3 ) )
    self.add_option( StringOption( 'Weather', 'weatherZip0', self.weatherZip0, 'ZIP code 1', ''), realtime=False )
    self.add_option( BoolOption( 'Weather', 'weatherForecast0', self.weatherForecast0, 'Show forecast 1', '' ) )
    self.add_option( StringOption( 'Weather', 'weatherZip1', self.weatherZip1, 'ZIP code 2', ''), realtime=False )
    self.add_option( BoolOption( 'Weather', 'weatherForecast1', self.weatherForecast1, 'Show forecast 2', '' ) )
    self.add_option( StringOption( 'Weather', 'weatherZip2', self.weatherZip2, 'ZIP code 3', ''), realtime=False )
    self.add_option( BoolOption( 'Weather', 'weatherForecast2', self.weatherForecast2, 'Show forecast 3', '' ) )

    self.add_options_group( 'Course', '' )
    self.add_option( IntOption( 'Course','courseNum', self.courseNum, 'Num courses', '', min=1, max=3 ) )
    self.add_option( StringOption( 'Course', 'courseFrom0', self.courseFrom0, 'Course 1 from', '', choices=self.courseCodes ) )
    self.add_option( StringOption( 'Course', 'courseTo0', self.courseTo0, 'Course 1 to', '', choices=self.courseCodes ) )
    self.add_option( StringOption( 'Course', 'courseFrom1', self.courseFrom1, 'Course 2 from', '', choices=self.courseCodes ) )
    self.add_option( StringOption( 'Course', 'courseTo1', self.courseTo1, 'Course 2 to', '', choices=self.courseCodes ) )
    self.add_option( StringOption( 'Course', 'courseFrom2', self.courseFrom2, 'Course 3 from', '', choices=self.courseCodes ) )
    self.add_option( StringOption( 'Course', 'courseTo2', self.courseTo2, 'Course 3 to', '', choices=self.courseCodes ) )

    self.add_options_group( 'Stock', '' )
    self.add_option( IntOption( 'Stock','stockNum', self.stockNum, 'Num stocks', '', min=1, max=3 ) )
    self.add_option( StringOption( 'Stock', 'stockSymbol0', self.stockSymbol0, 'Stock symbol 1', '' ), realtime=False )
    self.add_option( StringOption( 'Stock', 'stockSymbol1', self.stockSymbol1, 'Stock symbol 2', '' ), realtime=False )
    self.add_option( StringOption( 'Stock', 'stockSymbol2', self.stockSymbol2, 'Stock symbol 3', '' ), realtime=False )

    self.add_options_group( 'nVidia', 'This sensor can cause the freezing screenlet. If this is your problem, try to turn off unnecessary options.' )
    self.add_option( BoolOption( 'nVidia', 'nvidiaShowGpu', self.nvidiaShowGpu, 'Show GPU', '' ) )
    self.add_option( BoolOption( 'nVidia', 'nvidiaShowRam', self.nvidiaShowRam, 'Show RAM', '' ) )
    self.add_option( BoolOption( 'nVidia', 'nvidiaShowDriver', self.nvidiaShowDriver, 'Show driver', '' ) )
    self.add_option( BoolOption( 'nVidia', 'nvidiaShowReolution', self.nvidiaShowReolution, 'Show resolution', '' ) )
    self.add_option( BoolOption( 'nVidia', 'nvidiaShowRefreshRate', self.nvidiaShowRefreshRate, 'Show refresh rate', '' ) )
    self.add_option( BoolOption( 'nVidia', 'nvidiaShowGpuFrequency', self.nvidiaShowGpuFrequency, 'Show GPU frequency', '' ) )
    self.add_option( BoolOption( 'nVidia', 'nvidiaShowMemFrequency', self.nvidiaShowMemFrequency, 'Show MEM frequency', '' ) )
    self.add_option( BoolOption( 'nVidia', 'nvidiaShowTemp', self.nvidiaShowTemp, 'Show GPU temp', '' ) )
    self.add_option( IntOption( 'nVidia','nvidiaTempMax', self.nvidiaTempMax, 'Temp max ', '', min=40, max=100 ) )

    self.add_options_group( 'Net', '' )
    self.add_option( StringOption( 'Net', 'externalIpUrl', self.externalIpUrl, 'External IP from URL', '' ), realtime=False )
    self.add_option( StringOption( 'Net', 'localIpDevice', self.localIpDevice, 'Local IP device', '', choices=self.localIpDevices ) )
    self.add_option( FloatOption( 'Net', 'netStatisticUploadTotal', self.netStatisticUploadTotal, 'Total upload', '', min=0.0, max=1024.0*1024.0*1024.0*1024.0 ), realtime=False )
    self.add_option( FloatOption( 'Net', 'netStatisticDownloadTotal', self.netStatisticDownloadTotal, 'Total download', '', min=0.0, max=1024.0*1024.0*1024.0*1024.0 ), realtime=False )
    self.add_option( IntOption( 'Net', 'netLoadMaxUpload', self.netLoadMaxUpload, '100% upload (for graph) [Kbps]', '', min=1, max=1024*1024 ) )
    self.add_option( IntOption( 'Net', 'netLoadMaxDownload', self.netLoadMaxDownload, '100% download (for graph) [Kbps]', '', min=1, max=1024*1024 ) )

    self.add_options_group( 'RSS', '' )
    self.add_option( IntOption( 'RSS','rssNum', self.rssNum, 'Num RSS', '', min=1, max=3 ) )
    self.add_option( StringOption( 'RSS', 'rssUrl0', self.rssUrl0, 'Rss url 1', '' ), realtime=False )
    self.add_option( StringOption( 'RSS', 'rssUrl1', self.rssUrl1, 'Rss url 2', '' ), realtime=False )
    self.add_option( StringOption( 'RSS', 'rssUrl2', self.rssUrl2, 'Rss url 3', '' ), realtime=False )
    self.add_option( IntOption( 'RSS','rssItems', self.rssItems, 'Max items', '', min=1, max=20 ) )
    self.add_option( StringOption( 'RSS', 'rssBrowser', self.rssBrowser, 'Default browser', '' ), realtime=False )

    self.add_options_group( 'Disks', '' )
    self.add_option( StringOption( 'Disks', 'disksType', self.disksType, 'Disk type', '', choices=self.disksTypes ) )

    self.add_options_group( 'Processes', '' )
    self.add_option( StringOption( 'Processes', 'processesType', self.processesType, 'Processes type', '', choices=self.processesTypes ) )
    self.add_option( IntOption( 'Processes', 'processesNum', self.processesNum, 'Processes num (only extra)', 'Just for extra processes.', min=1, max=20 ) )


  # end __init__()

  # on change variable in class
  # @param  string string
  # @return void
  def __setattr__ ( self, name, value ):
    if name != 'width':
      screenlets.Screenlet.__setattr__( self, name, value )

    # refresh all infopanel, if options sensors or positions was changed
    if ( 'sensors' in name or 'positions' in name or 'spaces' in name ) and '__' not in name:
      self.createArrays()
      self._allUpdate = True

    if 'font' == name:
      try:
        self.fontSize = int( self.font[ self.font.rfind( ' ' )+1 : ] )
        self.font = self.font[ : self.font.rfind( ' ' ) ]
      except ValueError:
        pass

    if 'scale' == name:
      self._allUpdate = True

    # all update
    foo = [
      'starty', 'expand', 'showIcon', 'font', 'colorText', 'colorBackground', 'height',
      'backgroundTransparency', 'backgroundTransparencyLeft', 'backgroundRadius',
      'backgroundTransparencyStart', 'backgroundTransparencyStep',
      'holidayNum', 'holidayFile0', 'holidayFile1', 'holidayFile2',
      'weatherForecast0', 'weatherForecast1', 'weatherForecast2',
      'courseFrom0', 'courseFrom1', 'courseFrom2', 'courseTo0', 'courseTo1', 'courseTo2',
      'rssBrowser', 'processesType', 'processesNum', 'nvidiaTempMax',
    ]
    for bar in foo:
      if bar == name:
        self._allUpdate = True
    foo = [ 'graph', 'Graph', 'nvidiaShow', ]
    for bar in foo:
      if bar in name:
        self._allUpdate = True

    # all update & refresh
    foo = [ 'weatherNum', 'weatherZip0', 'weatherZip1', 'weatherZip2', 'weatherMetric', ]
    for bar in foo:
      if bar == name:
        self._allUpdate = True
        self._refreshNet['weather'] = True
    if 'courseNum' == name:
      self._allUpdate = True
      self._refreshNet['course'] = True
    foo = [ 'stockNum', 'stockSymbol0', 'stockSymbol1', 'stockSymbol2', ]
    for bar in foo:
      if bar == name:
        self._allUpdate = True
        self._refreshNet['stock'] = True
    foo = [ 'rssNum', 'rssUrl0', 'rssUrl1', 'rssUrl2', 'rssItems', ]
    for bar in foo:
      if bar == name:
        self._allUpdate = True
        self._refreshNet['rss'] = True

    # refresh
    if 'externalIpUrl' == name:
      self._refreshNet['externalIp'] = True
  # end __setattr__()


  ##########################################################
  ###                                                    ###
  ###                    ON_ FUNCTIONS                   ###
  ###                                                    ###
  ##########################################################

  # Called when the Screenlet's options have been applied and the screenlet finished its initialization.
  # @return void
  def on_init( self ):
    """Called when the Screenlet's options have been applied and the
    screenlet finished its initialization. If you want to have your
    Screenlet do things on startup you should use this handler."""
    # set right click menu
    self.add_menuitem( "refreshAll", "Refresh ALL" )
    self.add_menuitem( "refreshIP", "Refresh IP" )
    self.add_menuitem( "refreshWeather", "Refresh Weather" )
    self.add_menuitem( "refreshCourse", "Refresh Course" )
    self.add_menuitem( "refreshStock", "Refresh Stock" )
    self.add_menuitem( "refreshRss", "Refresh RSS" )
    self.add_menuitem( "clearNet", "Clear net statistic" )
    self.add_menuitem( "zipCode", "ZIP code" )
    self.add_default_menuitems()
    # init buffers
    self.initBuffers()
  # end on_init()

  # Called when a menuitem is selected.
  # @param  string
  # @return void
  def on_menuitem_select( self, id ):
    """Called when a menuitem is selected."""
    redraw = False
    # set action for right click menu
    if id == "refreshAll":
      self._refresh['IP'] = True
      self._refresh['weather'] = True
      self._refresh['course'] = True
      self._refresh['stock'] = True
      self._refresh['rss'] = True
      self._refresh['netStatistic'] = True
      redraw = True
    if id == "refreshIP":
      self._refresh['IP'] = True
      redraw = True
    elif id == "refreshWeather":
      self._refresh['weather'] = True
      redraw = True
    elif id == "refreshCourse":
      self._refresh['course'] = True
      redraw = True
    elif id == "refreshStock":
      self._refresh['stock'] = True
      redraw = True
    elif id == "refreshRss":
      self._refresh['rss'] = True
      redraw = True
    elif id == "clearNet":
      self.netStatisticUploadTotal = 0.0
      self.netStatisticDownloadTotal = 0.0
    elif id == "zipCode":
      self.weatherZipDialog()

    # redraw
    if redraw:
      self._allUpdateNet = True
      self._allUpdateWait = True
      self.redraw_canvas()
  # end on_menuitem_select()

  # Called when the theme is reloaded (after loading, before redraw).
  # @return void
  def on_load_theme( self ):
    """Called when the theme is reloaded (after loading, before redraw)."""
    if not self._themeModule or self.theme_name != self._themeModule.__name__:
      self._themeModule = __import__( self.theme_name )
      self.redraw_canvas()
      self._allUpdate = True
  # end on_load_theme()

  # on map
  # @return void
  def on_map( self ):
    if not self.timer:
      self.timer = gobject.timeout_add( self._updateInterval*1000, self.update )
    self.update()
  # end on_map()

  # on unmap
  # @return void
  def on_unmap( self ):
    if self.timer:
      gobject.source_remove( self.timer )
      self.timer = None
  # end on_unmap()


  ##########################################################
  ###                                                    ###
  ###                 ON_MOUSE_ FUNCTIONS                ###
  ###                                                    ###
  ##########################################################

  # Called when a buttonpress-event occured in Screenlet's window.
  # @return void
  def on_mouse_down( self, event ):
    """Called when a buttonpress-event occured in Screenlet's window.
    Returning True causes the event to be not further propagated."""
    x = event.x / self.scale
    y = event.y / self.scale

    for a,b in self.clickData.iteritems():
      if b['start'] < y < b['end']:
        b['function']( b['args'] )
        self.debug( 'Clicked '+a )
  # end on_mouse_down()

  # Called when the mouse leaves the Screenlet's window.
  # @return void
  def on_mouse_leave (self, event ):
    """Called when the mouse leaves the Screenlet's window."""
    self.clickDraw = False
  # end on_mouse_leave()

  # Called when the mouse moves in the Screenlet's window.
  # @return void
  def on_mouse_move( self, event ):
    """Called when the mouse moves in the Screenlet's window."""
    x = event.x / self.scale
    y = event.y / self.scale

    for a,b in self.clickData.iteritems():
      if b['start'] < y < b['end']:
        self.clickDraw = True
        self.clickStart = int( b['start'] )
        self.clickEnd = int( b['end'] )
        self.redraw_canvas()
      else:
        self.clickDraw = False
  # end on_mouse_move()

  # open browser
  # @param  list
  # @return void
  def openBrowser( self, args ):
    os.system( self.rssBrowser + ' ' + args[0] + '&' )
  # end openBrowser()

  # open directory
  # @param  list
  # @return void
  def openDirectory( self, args ):
    os.system('xdg-open '  + chr(34) + args[0] + chr(34) + '&' )
  # end openDirectory()


  ##########################################################
  ###                                                    ###
  ###                  UPDATES FUNCTIONS                 ###
  ###                                                    ###
  ##########################################################

  # update (redraw) infopanel
  # @return bool
  def update( self ):
    hour = int( sensors.cal_get_hour() )
    minute = int( sensors.cal_get_minute() )
    second = int( sensors.cal_get_second() )

    self._isTime = {}
    if minute != self._oldMinute and second == 0:
      self._isTime['everyMinute'] = True
    if hour != self._oldHour and minute == second == 0:
      self._isTime['everyHour'] = True
    if hour < self._oldHour and minute == second == 0:
      self._isTime['everyDay'] = True
    if self.localIp != self.externalLocalIpOld:
      self._isTime['changeLocalIp'] = True

    self.redraw_canvas()
    return True
  # end update()

  # is time to refresh?
  # @param  string
  # @return bool
  def isTime( self, type ):
    if type[-3:] == 'sec' and int( sensors.cal_get_second() ) % int( type[:-3] ) == 0:
      return True
    if type in self._isTime.keys():
      return True
    if type == 'never':
      return False
    return False
  # end varUpdate()

  # if refresh sensor
  # @param  string string
  # @return bool
  def ifRefresh( self, sensor, type ):
    if not self.__sensors[sensor]:
      return False

    elif sensor in self._refresh.keys():
      del self._refresh[sensor]
      return True

    elif self._allUpdate or self._allUpdateNet or sensor in self._refreshNet.keys() or self.isTime( type ):
      return True

    else:
      return False
  # end isRefresh()

  # if refresh net part of sensor
  # @param  string
  # @return bool
  def ifRefreshNet( self, sensor, type ):
    if sensor in self._refreshNet.keys():
      del self._refreshNet[sensor]
      return True

    elif self._allUpdateNet or self.isTime( type ):
      return True

    else:
      return False
  # end isRefreshNet()


  ##########################################################
  ###                                                    ###
  ###           DRAW POSITIONS [PX] FUNCTION             ###
  ###                                                    ###
  ##########################################################

  # get line [px]
  # @return int
  def getLine( self ):
    return self._linePx
  # end getLine()

  # set line [px]
  # @param  int bool
  # @return void
  def setLine( self, px, appPx = True ):
    self._linePx = self._linePx + px
    if appPx:
      self._lineAppendPx = self._lineAppendPx + px
  # end setLine()

  # clear line
  # @return void
  def clearLine( self ):
    self._linePx = 0
    self._lineAppendPx = 0
  # end clearLine()



  # set line [px] by size text
  # @param  int
  # @return void
  def setLineByText( self, fontSize = 0, value = '' ):
    charsPerLine = 47 - int( ( self.fontSize+fontSize ) * 2 )
    lines = len( value ) / charsPerLine + 1
    if lines > 1: foo = 1.2
    else: foo = 1.0
    for i in range( lines ):
      self.setLine( int( self.getHeightText( fontSize ) * foo ) )
  # end setLineByText()

  # set line [px] by size graph
  # @param  string int
  # @return void
  def setLineByGraph( self, fontSize = 0, type = '' ):
    if type == 'none':
      self.setLine( self.getHeightText( fontSize ) )
    else:
      self.setLine( self.getHeightGraph( fontSize ) + 4 )
  # end setLineByGraph()



  # get text height
  # @return int
  def getHeightText( self, fontSize = 0 ):
    return int( ( self.fontSize + fontSize ) * 1.6 )
  # end getLine()

  # get graph height
  # @return int
  def getHeightGraph( self, fontSize = 0 ):
    return int( ( self.fontSize + fontSize ) * 1.8 )
  # end getLine()

  # get icon height
  # @return int
  def getHeightIcon( self, fontSize = 0 ):
    return int( ( self.fontSize + fontSize ) * 2.4 )
  # end getLine()



  # get height [px] of sensor
  # @param  string
  # @return int
  def getHeightSensor( self, sensor ):
    return self.heights[sensor]
  # end getLineHeight()

  # save height [px] of sensor
  # @param  string
  # @return int
  def saveHeightSensor( self, sensor ):
    self.setLine( 4 )
    self.heights[sensor] = self._lineAppendPx
    self._lineAppendPx = 0
  # end saveLine()


  ##########################################################
  ###                                                    ###
  ###                         BUFFERS                    ###
  ###                                                    ###
  ##########################################################

  # init buffers
  # @return void
  def initBuffers(self):
    self.__buffers['hover'] = gtk.gdk.Pixmap(self.window.window, self.width, gtk.gdk.screen_height(), -1)
    self.__buffers['background'] = gtk.gdk.Pixmap(self.window.window, self.width, gtk.gdk.screen_height(), -1)
    self.__buffers['icons'] = gtk.gdk.Pixmap(self.window.window, self.width, gtk.gdk.screen_height(), -1)
    for sensor in self.__sensors.keys():
      self.__buffers[sensor] = gtk.gdk.Pixmap(self.window.window, self.width, gtk.gdk.screen_height(), -1)
  # end init_buffers()


  ##########################################################
  ###                                                    ###
  ###                  ON_DRAW FUNCTION                  ###
  ###                                                    ###
  ##########################################################

  # on draw
  # @param  cairo
  # @return void
  def on_draw( self, ctx ):
    #if not self.theme_module: return
    if self.scale > 5:
      self.scale = 5

    ctx.scale( self.scale, self.scale )

    # create & sort list of sensors
    array = [ [key,value] for key,value in self.__positions.iteritems() ]
    array.sort( self.mySort )

    # set start line
    self.clearLine()
    self.setLine( self.starty )
    self.saveHeightSensor( 'none' )

    # show information about downloading data
    if self._allUpdateWait:

      # draw message
      self._themeModule.drawWait( self, ctx )
      # next time do not show this message
      self._allUpdateWait = False

    # if mouse hover clicable item
    elif self.clickDraw:
      # show background from buffer
      ctx.set_source_pixmap( self.__buffers['background'], 0, 0 )
      ctx.paint()

      # create ctxHover
      ctxHover = self.__buffers['hover'].cairo_create()
      self.clear_cairo_context( ctxHover )
      ctxHover.set_operator( cairo.OPERATOR_OVER )
      self._themeModule.drawHover( self, ctxHover )

      # paint to the ctx
      ctx.set_source_pixmap( self.__buffers['hover'], 0, 0 )
      ctx.paint()

      # show sensors from buffers
      for sensor in self.__sensors.keys():
        if self.__sensors[sensor]:
          ctx.set_source_pixmap( self.__buffers[sensor], 0, 0 )
          ctx.paint()
      # show icon from buffer
      ctx.set_source_pixmap( self.__buffers['icons'], 0, 0 )
      ctx.paint()

    # infopanel
    else:

      # redraw backgroud & icons only when redrawing all
      if self._allUpdate:
        self.debug( 'allUpdate' )

        # background
        ctxBackground = self.__buffers['background'].cairo_create()
        self.clear_cairo_context( ctxBackground )
        ctxBackground.set_operator( cairo.OPERATOR_OVER )
        self._themeModule.drawBackground( self, ctxBackground )

        # icons
        self.ctxIcons = self.__buffers['icons'].cairo_create()
        self.clear_cairo_context( self.ctxIcons )
        self.ctxIcons.set_operator( cairo.OPERATOR_OVER )

      # show background from buffer
      ctx.set_source_pixmap( self.__buffers['background'], 0, 0 )
      ctx.paint()

      # draw sensors
      for sensor,position in array:
        if self.__sensors[sensor]:
          # if refresh and set to show, create new buffer
          if self.getVariable( sensor ):
            # create ctx layer
            ctxLayer = self.__buffers[sensor].cairo_create()
            self.clear_cairo_context( ctxLayer )
            ctxLayer.set_operator( cairo.OPERATOR_OVER )
            # draw sensor
            self._themeModule.draw( self, ctxLayer, sensor )
            # space
            self.setLine( self.__spaces[sensor] )
            # save height [px] of sensor
            self.saveHeightSensor( sensor )
          # else add height [px] of sensor
          else: self.setLine( self.getHeightSensor( sensor ), False )

        # if set to show, draw buffer
        if self.__sensors[sensor]:
          ctx.set_source_pixmap( self.__buffers[sensor], 0, 0 )
          ctx.paint()

      # show icon from buffer
      ctx.set_source_pixmap( self.__buffers['icons'], 0, 0 )
      ctx.paint()

      # unset all update
      self._allUpdate = False
      self._allUpdateNet = False
      # set old time
      self._oldHour = int( sensors.cal_get_hour() )
      self._oldMinute = int( sensors.cal_get_minute() )

      # expand
      if self.expand:
        newHeight = gtk.gdk.screen_height()
      else:
        newHeight = self.getLine()
      if self.height != newHeight:
        self.height = newHeight
  # end on_draw()

  # mysort for two dimensions list
  # @param  int int
  # @return int
  def mySort( self, x, y ):
    if x[1] < y[1]: return -1
    elif x[1] > y[1]: return 1
    else: return 0
  # end mySort()


  ##########################################################
  ###                                                    ###
  ###                   GET FUNCTIONS                    ###
  ###                                                    ###
  ##########################################################

  # get variable and return if sensor has be redraw
  # @param  string
  # @return bool
  def getVariable( self, sensor ):

    ##############################
    #####        TIME        #####
    ##############################
    if sensor == 'time':
      self.time = sensors.cal_get_local_time()
      return True
    # end time

    ##############################
    #####        DATE        #####
    ##############################
    elif sensor == 'date' and self.ifRefresh( sensor, 'everyDay' ):
      self.date = sensors.cal_get_day_name() + ' ' + sensors.cal_get_local_date()

      year  = int( sensors.cal_get_year()[-2:] )
      month = int( sensors.cal_get_month() )
      day   = int( sensors.cal_get_day() )
      ageOfMoon = year%19
      if ageOfMoon > 9: afeOfMoon = ageOfMoon - 19
      ageOfMoon = ( ageOfMoon * 11 ) % 30
      if 3 > month > 0: month = month + 2
      ageOfMoon = ageOfMoon + day + month - 8.3
      self.datePhase = str( int( ageOfMoon % 30 ) )

      return True
    # end date

    ##############################
    #####      HOLIDAY       #####
    ##############################
    elif sensor == 'holiday' and self.ifRefresh( sensor, 'everyDay' ):
      # create list of files with holidays
      holidayFile = [ self.holidayFile0, self.holidayFile1, self.holidayFile2 ]

      for key in range( self.holidayNum ):
        # if file is empty => jump
        if holidayFile[key] == '': continue
        # open file, read, create list and close file
        f = open(self.get_screenlet_dir() + '/holidays/' + holidayFile[key], 'r')
        file = f.read().split( '\n' )
        f.close()
        # line: "02-02: Name"
        # if is silvestr
        if sensors.cal_get_day() == '31' and sensors.cal_get_month() == '12':
          self.holidayToday[key] = file[len(file)-1][6:]
          self.holidayTomorrow[key] = file[0][6:]
        else:
          for index,line in enumerate( file ):
            if line[0:2] == sensors.cal_get_day() and line[3:5] == sensors.cal_get_month():
              self.holidayToday[key] = line[6:]
              self.holidayTomorrow[key] = file[index+1][6:]
      return True
    # end holiday

    ##############################
    #####       WEATHER      #####
    ##############################
    elif sensor == 'weather' and self.ifRefresh( sensor, 'everyHour' ):
      if self.ifRefreshNet( sensor, 'everyHour' ):

        # set unit
        if self.weatherMetric: weatherUnit = 'm'
        else: weatherUnit = 's'
        # create list of zips code
        weatherZips = [ self.weatherZip0, self.weatherZip1, self.weatherZip2 ]

        for key in range( self.weatherNum ):
          try:
            # download data
            self.debug( 'Download weather' )
            data = urllib.urlopen( 'http://xoap.weather.com/weather/local/'+weatherZips[key]+
                                   '?cc=*&dayf=10&prod=xoap&par=1003666583&key=4128909340a9b2fc&unit='+weatherUnit+
                                   '&link=xoap' ).read()

            locate = data[data.find('<dnam>')+6:data.find('</dnam>')]
            # set locate
            self.weatherLocateCity[key] = locate[0:locate.find(',')]
            self.weatherLocateState[key] = locate[locate.find(',')+2:]
            # set celsia and icon
            self.weatherTmp[key] = data[data.find('<tmp>')+5:data.find('</tmp>')]
            self.weatherLow[key] = []
            self.weatherHi[key] = []
            self.weatherIcon[key] = []
            # get data
            for x in range(5):
              day = data[data.find('<day d="'+str(x)+'"'):]
              day = day[:day.find('</day>')]
              self.weatherLow[key].append( day[day.find('<low>')+5 : day.find('</low>')] )
              self.weatherHi[key].append( day[day.find('<hi>')+4 : day.find('</hi>')] )
              self.weatherIcon[key].append( day[day.find('<icon>')+6 : day.find('</icon>')] )

          # if isn't net connection, set default values
          except IOError:
            self.weatherLocateState[key] = ''
            self.weatherTmp[key] = 'N/A'
            if len(self.weatherLow) == 0:
              self.weatherLocateCity[key] = ''
              self.weatherLow[key] = []
              self.weatherHi[key] = []
              self.weatherIcon[key] = []
              for x in range(5):
                self.weatherLow[key].append( '?' )
                self.weatherHi[key].append( '?' )
                self.weatherIcon[key].append( '' )
      return True
    # end weather

    ##############################
    #####       COURSE       #####
    ##############################
    elif sensor == 'course' and self.ifRefresh( sensor, 'everyHour' ):
      if self.ifRefreshNet( sensor, 'everyHour' ):
        self.getCourse()

      # create list courseFrom and courseTo
      courseFrom = [ self.courseFrom0, self.courseFrom1, self.courseFrom2 ]
      courseTo = [ self.courseTo0, self.courseTo1, self.courseTo2 ]

      for key in range( self.courseNum ):
        result = 0
        if courseFrom[key] != '' and courseTo[key] != '' and len( self.courseCodes ) != 0:
          result = float( self.courseCurrency[courseFrom[key]]) / float(self.courseCurrency[courseTo[key]] )
          result = round( result, 3 )
        self.courseCourse[key] = str(result)

      return True
    # end course

    ##############################
    #####        STOCK       #####
    ##############################
    elif sensor == 'stock' and self.ifRefresh( sensor, 'everyHour' ):
      stockSymbols = [ self.stockSymbol0, self.stockSymbol1, self.stockSymbol2 ]

      if self.ifRefreshNet( sensor, 'everyHour' ):

        for key in range( self.stockNum ):
          try:
            if stockSymbols[key] != '':
              self.debug( 'Download stock' )
              data = urllib.urlopen( 'http://download.finance.yahoo.com/d/quotes.csv?s='+stockSymbols[key]+'&f=nl1c1' ).read().split( ',' )
            else:
              data = [ '"No symbol"', '', '' ]
            self.stockName[stockSymbols[key]] = data[0].split( '"' )[1]
            self.stockLastTrade[stockSymbols[key]] = data[1]
            self.stockChange[stockSymbols[key]] = data[2]

          # if isn't net connection, set default value
          except IOError:
            self.stockChange[stockSymbols[key]] = 'N/A'
            if stockSymbols[key] not in self.stockName:
              self.stockName[stockSymbols[key]] = ''
              self.stockLastTrade[stockSymbols[key]] = ''

      for key in range( self.stockNum ):
        if stockSymbols[key] not in self.stockName.keys():
          self.stockChange[stockSymbols[key]] = 'N/A'
          self.stockName[stockSymbols[key]] = ''
          self.stockLastTrade[stockSymbols[key]] = ''

      return True
    # end stock

    ##############################
    #####      USERNAME      #####
    ##############################
    elif sensor == 'username' and self.ifRefresh( sensor, 'never' ):
      self.username = sensors.sys_get_username()
      self.hostname = sensors.sys_get_hostname()
      return True
    # end username

    ##############################
    #####       DISTRO       #####
    ##############################
    elif sensor == 'distro' and self.ifRefresh( sensor, 'never' ):
      self.distro = sensors.sys_get_distrib_name()
      return True
    # end distro

    ##############################
    #####       KERNEL       #####
    ##############################
    elif sensor == 'kernel' and self.ifRefresh( sensor, 'never' ):
      self.kernel = sensors.sys_get_kernel_version()
      return True
    # end kernel

    ##############################
    #####       CPUNAME      #####
    ##############################
    elif sensor == 'cpuname' and self.ifRefresh( sensor, 'never' ):
      self.cpuname = sensors.cpu_get_cpu_name().replace( '  ', '' )
      return True
    # end cpuname

    ##############################
    #####    CPUFREQUENCY    #####
    ##############################
    elif sensor == 'cpufrequency' and self.ifRefresh( sensor, '3sec' ):
      foo = sensors.sys_get_full_info().split( 'processor\t' )
      foo.pop( 0 )

      self.cpufrequency = []
      for cpu in foo:
        mhz = cpu[ cpu.find( 'cpu MHz')+11 : ]
        mhz = mhz[ : mhz.find( '\n' ) ]
        mhz = str( round( float( mhz ), 2 ) )
        self.cpufrequency.append( mhz )

      if self.cpufrequency == self.cpufrequencyOld and not self._allUpdate:
        return False
      self.cpufrequencyOld = self.cpufrequency
      return True
    # end cpuname

    ##############################
    #####        CPUS        #####
    ##############################
    elif sensor == 'cpus':

      if self.sensorsCpus0: start = 0
      else: start = 1

      for key in range( start, self.cpusNum+1 ):

        # set default old load
        if key not in self.cpusOld.keys():
          self.cpusOld[key] = 0

        # get new load
        self.cpusNew[key] = sensors.cpu_get_load( key )
        self.cpusLoad[key] = str( round( ( self.cpusNew[key]-self.cpusOld[key]) / self._updateInterval, 1 ) )
        self.cpusOld[key] = self.cpusNew[key]

        if float(self.cpusLoad[key]) > 100.0: self.cpusLoad[key] = '99.9'
        if float(self.cpusLoad[key]) < 0.0: self.cpusLoad[key] = '0.0'

      return True
    # end cpus

    ##############################
    #####        LOAD        #####
    ##############################
    elif sensor == 'load':
      self.load = sensors.sys_get_average_load()
      if self.load == self.loadOld and not self._allUpdate:
        return False
      self.loadOld = self.load
      return True
    # end load

    ##############################
    #####     NVIDIAINFO     #####
    ##############################
    elif sensor == 'nvidiaInfo' and self.ifRefresh( sensor, '3sec' ):
      if self.ifRefresh( sensor, 'never' ):
        if self.nvidiaShowGpu:
          self.nvidiaInfo['gpu'] = os.popen( 'nvidia-settings -q Gpus | cut -d \'(\' -f 2 -s' ).read().replace( '\n', '' ).replace( ')', '' )
        if self.nvidiaShowRam:
          self.nvidiaInfo['ram'] = str( int( os.popen( 'nvidia-settings -q VideoRam -t' ).read().replace( '\n', '' ) )/1024 )
        if self.nvidiaShowDriver:
          self.nvidiaInfo['driver'] = os.popen( 'nvidia-settings -q NvidiaDriverVersion -t' ).read().replace( '\n', '' )
        if self.nvidiaShowReolution:
          self.nvidiaInfo['resolution'] = os.popen( 'nvidia-settings -q FrontendResolution -t' ).read().replace( '\n', '' ).split( ',' )
        if self.nvidiaShowRefreshRate:
          self.nvidiaInfo['refreshRate'] = os.popen( 'nvidia-settings -q RefreshRate -t' ).read().replace( '\n', '' )

      if self.nvidiaShowGpuFrequency:
        self.nvidiaInfo['gpuFrequency'] = os.popen( 'nvidia-settings -q GPUCurrentClockFreqs -t | cut -d \',\' -f1' ).read().replace( '\n', '' )
      if self.nvidiaShowMemFrequency:
        self.nvidiaInfo['memFrequency'] = os.popen( 'nvidia-settings -q GPUCurrentClockFreqs -t | cut -d \',\' -f2' ).read().replace( '\n', '' )
      if self.nvidiaShowTemp:
        self.nvidiaInfo['temp'] = os.popen( 'nvidia-settings -q GPUCoreTemp -t' ).read().replace( '\n', '' )

      if self.nvidiaInfo == self.nvidiaInfoOld and not self._allUpdate:
        return False
      self.nvidiaInfoOld = dict( self.nvidiaInfo )

      if self.nvidiaShowTemp:
        self.nvidiaTemp = int( int( self.nvidiaInfo['temp'] ) / ( self.nvidiaTempMax / 100.0 ) )

      return True
    # end nvidiainfo

    ##############################
    #####       MEMORY       #####
    ##############################
    elif sensor == 'memory' and self.ifRefresh( sensor, '3sec' ):
      self.memory = str( sensors.mem_get_usage() )
      if self.memory == self.memoryOld and not self._allUpdate:
        return False
      self.memoryOld = self.memory
      return True
    # end memory

    ##############################
    #####        SWAP        #####
    ##############################
    elif sensor == 'swap' and self.ifRefresh( sensor, '3sec' ):
      self.swap = str( sensors.mem_get_usedswap() )
      if self.swap == self.swapOld and not self._allUpdate:
        return False
      self.swapOld = self.swap
      return True
    # end swap

    ##############################
    #####      LOCAL IP      #####
    ##############################
    elif sensor == 'localIp' and self.ifRefresh( sensor, '3sec' ):

      device = ''
      localIps = {}

      for line in os.popen( '/sbin/ifconfig' ).readlines():
        if line[0] != ' ':
          device = line[0 : line[1:].find(' ')+1 ]
          continue
        #    inet 10.0.35.11/8 brd 10.255.255.255 scope global eth0
        if line.find( 'inet ' ) >= 0:
          localIps[device] = line[ line.find( 'addr:' )+5 : line.find( 'Bcast' )-1 ]

      if self.localIpDevice != '':
        if self.localIpDevice in localIps.keys():
          self.localIp = localIps[self.localIpDevice]
        else:
          self.localIp = 'Undefined'

      elif len( localIps.keys() ) == 1:
        self.localIp = localIps.values()[0]
        self.localIpDevice = localIps.keys()[0]

      else:
        for key in localIps.keys():
          if localIps[key] != '127.0.0.1':
            self.localIp = localIps[key]
            self.localIpDevice = key

      if self.localIp == self.localIpOld and not self._allUpdate:
        return False
      self.localIpOld = self.localIp

      return True
    # end localIp

    ##############################
    #####     EXTERNAL IP    #####
    ##############################
    elif sensor == 'externalIp' and self.ifRefresh( sensor, 'changeLocalIp' ):
      if self.ifRefreshNet( sensor, 'changeLocalIp' ):
        self.debug( 'Download external IP' )
        try: self.externalIp = urllib.urlopen( self.externalIpUrl ).read()
        except IOError: self.externalIp ='Undefined'
        self.externalLocalIpOld = self.localIp
      return True
    # end externalIp

    ##############################
    #####       UPLOAD       #####
    ##############################
    elif sensor == 'upload':
      self.uploadNew = sensors.net_get_updown()[0]
      if self.uploadOld == 0.0:
        self.uploadOld = self.uploadNew
      foo = round( ( self.uploadNew-self.uploadOld) / self._updateInterval, 1 )
      if foo < 0.0: foo = 0.0
      self.upload = str( foo )
      self.uploadOld = self.uploadNew
      self.netLoadUpload = float( self.upload ) / ( self.netLoadMaxUpload / 100.0 )
      return True
    # end upload

    ##############################
    #####      DOWNLOAD      #####
    ##############################
    elif sensor == 'download':
      self.downloadNew = sensors.net_get_updown()[1]
      if self.downloadOld == 0.0:
        self.downloadOld = self.downloadNew
      foo = round( ( self.downloadNew-self.downloadOld ) / self._updateInterval, 1 )
      if foo < 0.0: foo = 0.0
      self.download = str( foo )
      self.downloadOld = self.downloadNew
      self.netLoadDownload = float( self.download ) / ( self.netLoadMaxDownload / 100.0 )
      return True
    # end download

    ##############################
    #####    NET STATISTIC   #####
    ##############################
    elif sensor == 'netStatistic':
      #if self.uploadNew == self.uploadOld and self.downloadNew == self.downloadOld and not self._allUpdate:
      #  return False

      if not self.sensorsUpload: self.getVariable( 'upload' )
      if not self.sensorsDownload: self.getVariable( 'download' )

      self.netStatisticUploadTotal = float( self.netStatisticUploadTotal ) + float( self.upload )
      self.netStatisticDownloadTotal = float( self.netStatisticDownloadTotal ) + float( self.download )

      foo = [ ' KB', ' MB', ' GB', ' TB' ]

      for x,bar in enumerate( foo ):
        if self.netStatisticUploadTotal / 1024.0**(x+1) < 1.0:
          self.netStatisticUpload = str( round( self.netStatisticUploadTotal / 1024.0**x, 1 ) ) + bar
          break

      for x,bar in enumerate( foo ):
        if self.netStatisticDownloadTotal / 1024.0**(x+1) < 1.0:
          self.netStatisticDownload = str( round( self.netStatisticDownloadTotal / 1024.0**x, 1 ) ) + bar
          break

      if self.netStatisticUpload == self.netStatisticUploadOld and self.netStatisticDownload and self.netStatisticDownload and not self._allUpdate:
        return False
      self.netStatisticUploadOld = self.netStatisticUpload
      self.netStatisticDownloadOld = self.netStatisticDownload

      return True
    # end netStatistic

    ##############################
    #####         RSS        #####
    ##############################
    elif sensor == 'rss' and self.ifRefresh( sensor, 'everyHour' ):

      rssUrls = [ self.rssUrl0, self.rssUrl1, self.rssUrl2 ]

      if self.ifRefreshNet( sensor, 'everyHour' ):

        for key in range( self.rssNum ):
          try:

            if rssUrls[key] == '':
              raise IOError

            self.debug( 'Download RSS' )
            data = urllib.urlopen( rssUrls[key] ).read()

            title = data[ data.find( '<title>' )+7 : data.find( '</title>' ) ]
            link = data[ data.find( '<link>' )+6 : data.find( '</link>' ) ]
            items = data.split( '<item>' )
            del items[0]

            foo = []
            for item in items:
              bar = {}
              bar['title'] = item[ item.find( '<title>' )+7 : item.find( '</title>' ) ]
              bar['link'] = item[ item.find( '<link>' )+6 : item.find( '</link>' ) ]
              #bar['description'] = item[item.find('<description>')+13:item.find('</description>')]
              #bar['pubdate'] = item[item.find('<pubDate>')+9:item.find('</pubDate>')]
              foo.append(bar)

            self.rssData[key] = {
              'title' : title,
              'link' : link,
              'items' : foo,
            }

          except IOError:
            self.rssData[key] = {
              'title' : 'Undefined',
              'link' : 'Undefined',
              'items' : [ { 'title' : '', 'link' : '', }, ]
            }

      return True
    # end rss

    ##############################
    #####        DISKS       #####
    ##############################
    elif sensor == 'disks' and self.ifRefresh( sensor, '3sec' ):
      list = sensors.disk_get_disk_list()

      self.disks = []
      for disk in list:
        disk = sensors.disk_get_usage(disk)
        if self.disksType == 'usage':
          self.disks.append( {
            'name' : disk[0],
            'capacity' : disk[1],
            'usage' : disk[2],
            'free' : disk[3],
            'usage%' : disk[4].replace( '%', '' ),
            'free%' : str( 100-float( disk[4].replace( '%', '' ) ) ),
            'mount' : disk[5],
          } )
        elif self.disksType == 'free':
          self.disks.append( {
            'name' : disk[0],
            'capacity' : disk[1],
            'usage' : disk[3], # in usage is free
            'free' : disk[2], # in free is usage
            'usage%' : str( 100-float( disk[4].replace( '%', '' ) ) ), # in usage is free
            'free%' : disk[4].replace( '%', '' ), # in free is usage
            'mount' : disk[5],
          } )

      if self.disks == self.disksOld and not self._allUpdate:
        return False
      self.disksOld = self.disks

      return True
    # end disks

    ##############################
    #####       BATTERY      #####
    ##############################
    elif sensor == 'battery' and self.ifRefresh( sensor, '3sec' ):
      list = sensors.bat_get_battery_list()
      if list:
        self.battery = list[0]
        data = sensors.bat_get_data( self.battery )
        try: self.batteryLoad = str( ( data[1]*100 ) / data[2] )
        except: self.batteryLoad = '0.0'
      return True
    # end battery

    ##############################
    #####      WIRELESS      #####
    ##############################
    elif sensor == 'wireless':
      foo = sensors.wir_get_interfaces()
      if foo:
        self.wireless = foo[0]
        self.wirelessLoad = str( sensors.wir_get_stats( foo[0] )['percentage'] )
      return True
    # end wireless

    ##############################
    #####     PROCESSES      #####
    ##############################
    elif sensor == 'processes':
      self.processes = []
      if self.processesType == 'basic':
        for line in sensors.process_get_top().replace(' ',' ').split('\n'):
          self.processes.append( line )
      else:
        process = os.popen('ps -eo pcpu,pmem,comm --sort -pcpu').readlines()
        for key in range( self.processesNum ):
          foo = process[key].replace( '\n', '' )
          self.processes.append( {
            'cpu' : foo[0:5],
            'mem' : foo[5:10],
            'command' : foo[10:],
          } )

      if self.processes == self.processesOld and not self._allUpdate:
        return False
      self.processesOld = self.processes

      return True
    # end processes

    ##############################
    #####       UPTIME       #####
    ##############################
    elif sensor == 'uptime' and self.ifRefresh( sensor, 'everyMinute' ):
      foo = sensors.sys_get_uptime()
      hour = int( foo[ : foo.find( ':' ) ] )
      minute = int( foo[ foo.find( ':' )+1 : ] )

      day = int( hour/24 )
      hour = int( hour%24 )

      if day == 0: self.uptime = str( hour ) + ':' + self.twoDigits( minute )
      else:
        foo = 'day'
        if day > 1: foo = foo + 's'
        self.uptime = str( day ) + ' ' + foo + ' ' + str( hour ) + ':' + self.twoDigits( minute )

      return True
    # end uptime

    ##############################
    #####     LOGINTIME      #####
    ##############################
    elif sensor == 'logintime' and self.ifRefresh( sensor, 'everyMinute' ):
      foo = int( time.time() - self.logintimeStart )

      day = int( foo/3600/24 )
      hour = int( (foo/3600)%24 )
      minute = int( (foo/60)%60 )

      if day == 0: self.logintime = str( hour ) + ':' + self.twoDigits( minute )
      else:
        foo = 'day'
        if day > 1: foo = foo + 's'
        self.logintime = str( day ) + ' ' + foo + ' ' + str( hour ) + ':' + self.twoDigits( minute )

      return True
    # end logintime

    ##############################
    #####     TEMPERATURE    #####
    ##############################

    elif sensor == 'temperature1':
      f = open('/sys/devices/platform/thinkpad_hwmon/temp1_input', "r")
      tmp = f.readlines()
      f.close()
      self.temperature1 = "%d℃" % (int(tmp[0])/1000)
      if self.temperature1 == self.temperature1Old and not self._allUpdate:
        return False
      self.temperature1Old = self.temperature1
      return True

    ##############################
    #####     FAN            #####
    ##############################

    elif sensor == 'fan1':
      f = open('/sys/devices/platform/thinkpad_hwmon/fan1_input', "r")
      tmp = f.readlines()
      f.close()
      self.fan1 = tmp[0][0:-1]+' RPM'

      if self.fan1 == self.fan1Old and not self._allUpdate:
        return False
      self.fan1Old = self.fan1
      return True

    return False
  # end getVariable()


  # get course data
  # @return void
  def getCourse( self ):
    try:
      # download data
      self.debug( 'Download course' )
      data = urllib.urlopen( 'http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.txt' ).read()
      data = data[data.find( 'kurz\n' )+5:data.rfind( '\n' )].split( '\n' )
      # create list from data

      self.courseCodes = []
      for line in data:
        line = line.split( '|' )
        self.courseCodes.append(line[3])
        self.courseNumber[line[3]] = line[2]
        self.courseCurrency[line[3]] = line[4].replace( ',', '.' )
      # add czech republic
      self.courseCodes.append( 'CZE' )
      self.courseCodes = self.courseCodes
      self.courseNumber['CZE'] = '1'
      self.courseCurrency['CZE'] = '1'
      # sort list with codes
      self.courseCodes.sort()

    # if isn't net connection, set default value
    except IOError:
      self.courseCodes = []
      self.courseNumber = {}
      self.courseCurrency = {}
  # end getCourse()

  # change zip codes
  # @return void
  def weatherZipDialog( self ):
    # create dialog
    dialog = gtk.Dialog( "ZIP codes", self.window )
    dialog.resize( 300, 100 )
    dialog.add_buttons( gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL )
    # entry
    entrybox0 = gtk.Entry()
    entrybox0.set_text( str( self.weatherZip0 ) )
    entrybox1 = gtk.Entry()
    entrybox1.set_text( str( self.weatherZip1 ) )
    entrybox2 = gtk.Entry()
    entrybox2.set_text( str( self.weatherZip2 ) )
    # add to dialog
    dialog.vbox.add( entrybox0 )
    dialog.vbox.add( entrybox1 )
    dialog.vbox.add( entrybox2 )
    # show
    entrybox0.show()
    entrybox1.show()
    entrybox2.show()
    # run dialog
    response = dialog.run()
    if response == gtk.RESPONSE_OK:
      self.weatherZip0 = entrybox0.get_text()
      self.weatherZip1 = entrybox1.get_text()
      self.weatherZip2 = entrybox2.get_text()
    dialog.hide()
    self._refresh['weather'] = True
  # end weatherZipDialog()


  ##########################################################
  ###                                                    ###
  ###                HELP DRAW FUNCTIONS                 ###
  ###                                                    ###
  ##########################################################

  # translate integer to string with two digits
  # @param  int
  # @retrun string
  def twoDigits( self, num ):
    num = str( num )
    if len(num) < 2: return '0'+num
    else: return num
  # end twoDigit()

  # set color
  # @param  cairo list
  # @return void
  def setColor( self, ctx, color ):
    ctx.set_source_rgba( color[0], color[1], color[2], color[3] )
  # end setColor()

  # draw text
  # @param  cairo ctx, string value, int x, int y, int width, string font, int fontSite, pango align
  # @return void
  def drawText( self, ctx, value, x=0, y=None, width=None, font=None, fontSize=None, align=pango.ALIGN_CENTER ):
    if y == None: y = self.getLine()
    if width == None: width = self.width
    if font == None: font = self.font
    if fontSize == None: fontSize = self.fontSize
    ctx.save()
    ctx.translate( x, y )
    if self.p_layout == None:
      self.p_layout = ctx.create_layout()
    else:
      ctx.update_layout(self.p_layout)
    p_fdesc = pango.FontDescription()
    p_fdesc.set_family_static( font )
    p_fdesc.set_size( fontSize * pango.SCALE )
    self.p_layout.set_font_description( p_fdesc )
    self.p_layout.set_width( width * pango.SCALE )
    self.p_layout.set_alignment( align )
    self.p_layout.set_markup( str( value ) )
    ctx.show_layout( self.p_layout )
    self.p_layout.set_alignment( pango.ALIGN_CENTER )
    ctx.restore()
  # end draw_text()

  # on draw shape
  # @param  cairo
  # @return void
  def on_draw_shape(self, ctx):
    if self.theme:
      pass
    ctx.set_source_rgba(0, 0, 0, 1)
    self.draw_rectangle(ctx, 0, 0, self.width, self.height)
  # end on_draw_shape()

# end class InfoPanel2Screenlet





if __name__ == '__main__':
  import screenlets.session
  screenlets.session.create_session(InfoPanel2Screenlet)
