
import pango
import os
import re


# draw wait
# @param  cairo
# @return void
def drawWait( self, ctx ):
  self.setColor( ctx, self.colorText )
  self.drawText( ctx, 'Downloading data.', 0, self.getLine(), self.width, self.font, self.fontSize )
  self.setLineByText()
  self.drawText( ctx, 'Please, wait..', 0, self.getLine(), self.width, self.font, self.fontSize )
  self.setLineByText()
# end drawWait()


# draw background
# @param  cairo
# @return void
def drawBackground( self, ctxBackground ):
  if self.backgroundTransparency:
    for x in range( self.width ):
      color = list( self.colorBackground )
      if self.backgroundTransparencyLeft:
        color[3] = ( self.width*self.backgroundTransparencyStep - x*self.backgroundTransparencyStep + self.backgroundTransparencyStart ) / 255.0
      else:
        color[3] = ( x*self.backgroundTransparencyStep + self.backgroundTransparencyStart ) / 255.0
      self.setColor( ctxBackground, color )
      self.draw_rectangle( ctxBackground, x, 0, 1, self.height )
  else:
    self.setColor( ctxBackground, self.colorBackground )
    self.draw_rounded_rectangle( ctxBackground, 0, 0, self.backgroundRadius, self.width, self.height )
# end drawBackground()


# draw on mouse hover
# @param  cairo
# @raturn void
def drawHover( self, ctxHover ):
  self.setColor( ctxHover, self.colorGraphHover )
  self.draw_rectangle( ctxHover, 0, self.clickStart, self.width, self.clickEnd-self.clickStart )
# end drawHover()

# draw graph
# @param  cairo string float bool
# @return void
def drawGraph( self, ctx, type, percent, drawBackground=True, oppositeColor=False ):
  if type == 'none':
    return

  ctx.save()
  if self.showIcon:
    ctx.translate( self.getHeightIcon()+9, self.getLine() )
    width = self.width-self.getHeightIcon()-5
  else:
    ctx.translate( 0, self.getLine() )
    width = self.width

  if percent == '':
    percent = 0
  else:
    percent = float( percent )
  if percent > 99.9: percent = 99.9
  widthGraph = int( ( percent * width ) / 100 )

  if oppositeColor: percent = 100-percent

  if drawBackground:
    self.setColor( ctx, self.colorGraphBackground )
    self.draw_rectangle( ctx, 0, 0, width, self.getHeightGraph() )

  if 'color' in type:
    if percent > self.graphVeryHigh: self.setColor( ctx, self.colorGraphVeryHigh )
    elif percent > self.graphHigh: self.setColor( ctx, self.colorGraphHigh )
    elif percent > self.graphLow: self.setColor( ctx, self.colorGraphForeground )
    elif percent > self.graphVeryLow: self.setColor( ctx, self.colorGraphLow )
    else: self.setColor( ctx, self.colorGraphVeryLow )
  else:
    self.setColor( ctx, self.colorGraphForeground )

  if 'line' in type:
    self.draw_rectangle( ctx, 0, 0, widthGraph, self.getHeightGraph() )

  elif 'boxes' in type:
    i = 0
    while ( i * ( self.graphBoxesWidth + self.graphBoxesSpace ) ) < widthGraph and percent != 0:
      self.draw_rectangle( ctx, i*(self.graphBoxesWidth+self.graphBoxesSpace), 0, self.graphBoxesWidth, self.getHeightGraph() )
      i = i + 1

  ctx.restore()
# end drawGraph()


# draw icon
# @param  string
# @return void
def drawIcon( self, icon, move=-3 ):
  if not self.showIcon:
    return
  if self._allUpdate:
    icon = self.get_screenlet_dir()+'/themes/'+self.theme_name+'/'+icon
    if os.path.isfile( icon+'.png' ):
      self.ctxIcons.save()
      self.ctxIcons.translate( 4, self.getLine()+move )
      self.draw_scaled_image( self.ctxIcons, 0, 0, icon+'.png', self.getHeightIcon(), self.getHeightIcon() )
      self.ctxIcons.restore()
    elif os.path.isfile( icon+'.svg' ):
      self.ctxIcons.save()
      self.ctxIcons.translate( 4, self.getLine()+move )
      self.draw_scaled_image( self.ctxIcons, 0, 0, icon+'.svg', self.getHeightIcon(), self.getHeightIcon() )
      self.ctxIcons.restore()
# end drawIcon()


# draw icon by ctx
# @param  string
# @return void
def drawIconCtx( self, ctx, icon, move=-3 ):
  icon = self.get_screenlet_dir()+'/themes/'+self.theme_name+'/'+icon+'.png'
  if os.path.isfile( icon ):
    ctx.save()
    ctx.translate( 4, self.getLine()+move )
    self.draw_scaled_image( ctx, 0, 0, icon, self.getHeightIcon(), self.getHeightIcon() )
    ctx.restore()
# end drawIconCtx()


# draw
# @param  cairo string
# @return void
def draw( self, ctxLayer, sensor ):

  self.setColor( ctxLayer, self.colorText )

  ##############################
  #####        TIME        #####
  ##############################
  if sensor == 'time':
    drawIcon( self, 'time', 0 )
    self.drawText( ctxLayer, self.time, fontSize=self.fontSize+5 )
    self.setLineByText( 5 )
  # end time

  ##############################
  #####        DATE        #####
  ##############################
  elif sensor == 'date':
    drawIcon( self, 'date', -4 )
    self.drawText( ctxLayer, self.date )

    if self.sensorsDateMoon:
      icon = self.get_screenlet_dir()+'/themes/'+self.theme_name+'/moons/'+self.datePhase+'.png'
      self.draw_scaled_image( ctxLayer, self.width-self.getHeightText( 5 )-4, self.getLine()-4, icon, self.getHeightText( 5 ), self.getHeightText( 5 ) )

    self.setLineByText()
  # end date

  ##############################
  #####      HOLIDAY       #####
  ##############################
  elif sensor == 'holiday':
    for key in range( self.holidayNum ):

      text = 'Today: '+self.holidayToday[key]
      self.drawText( ctxLayer, text )
      self.setLineByText( value=text )

      text = 'Tomorrow: '+self.holidayTomorrow[key]
      self.drawText( ctxLayer, text )
      self.setLineByText( value=text )
  # end holiday

  ##############################
  #####      WEATHER       #####
  ##############################
  elif sensor == 'weather':
    for key in range( self.weatherNum ):
      if ( ( key == 0 and self.weatherZip0 == '' ) or
           ( key == 1 and self.weatherZip1 == '' ) or
           ( key == 2 and self.weatherZip2 == '' ) ):
        continue

      if len( self.weatherLocateState[key] ) > len( self.weatherLocateCity[key] ):
        foo = self.weatherLocateCity[key]
        bar = self.weatherLocateState[key]
      else:
        foo = self.weatherLocateState[key]
        bar = self.weatherLocateCity[key]

      icon = self.get_screenlet_dir()+'/themes/'+self.theme_name+'/weather/'+self.weatherIcon[key][0]+'.png'
      if os.path.isfile( icon ):
        self.draw_scaled_image( ctxLayer, 0, self.getLine(), icon, self.getHeightText( self.fontSize ), self.getHeightText( self.fontSize ) )
      self.drawText( ctxLayer, self.weatherTmp[key]+'\xc2\xb0', self.getHeightText( self.fontSize ), fontSize=self.fontSize*2, align=pango.ALIGN_LEFT )

      self.drawText( ctxLayer, foo+' '+self.weatherLow[key][0]+'/'+self.weatherHi[key][0]+'\xc2\xb0', align=pango.ALIGN_RIGHT )
      self.setLineByText()

      self.drawText( ctxLayer, bar, align=pango.ALIGN_RIGHT )
      self.setLineByText()

      if ( ( key == 0 and self.weatherForecast0) or
           ( key == 1 and self.weatherForecast1) or
           ( key == 2 and self.weatherForecast2) ):
        for x in range( 4 ):
          icon = self.get_screenlet_dir()+'/themes/'+self.theme_name+'/weather/'+self.weatherIcon[key][x+1]+'.png'
          if os.path.isfile( icon ):
            self.draw_scaled_image( ctxLayer, x*self.getHeightText()+x*30+2, self.getLine(), icon, self.getHeightText(), self.getHeightText() )

          self.drawText( ctxLayer, self.weatherLow[key][x+1]+'/'+self.weatherHi[key][x+1]+'\xc2\xb0', self.getHeightText() + x * ( self.getHeightText()+30 ), fontSize=self.fontSize-1, align=pango.ALIGN_LEFT )
        self.setLineByText()
  # end weather

  ##############################
  #####       COURSE       #####
  ##############################
  elif sensor == 'course':
    for key in range( self.courseNum ):

      if key == 0: ( foo, bar ) = ( self.courseFrom0, self.courseTo0 )
      if key == 1: ( foo, bar ) = ( self.courseFrom1, self.courseTo1 )
      if key == 2: ( foo, bar ) = ( self.courseFrom2, self.courseTo2 )

      if foo != '' and bar != '':
        if len( self.courseNumber ) == 0:
          text = 'No course'
        else:
          text = self.courseNumber[foo] + ' ' + foo + ' = ' + self.courseCourse[key] + ' ' + bar
        self.drawText( ctxLayer, text )
        self.setLineByText()
  # end weather

  ##############################
  #####        STOCK       #####
  ##############################
  elif sensor == 'stock':
    for key in range( self.stockNum ):
      if key == 0: symbol = self.stockSymbol0
      elif key == 1: symbol = self.stockSymbol1
      elif key == 2: symbol = self.stockSymbol2

      text = self.stockName[symbol]+': '+self.stockLastTrade[symbol]+', '+self.stockChange[symbol]
      self.drawText( ctxLayer, text )
      self.setLineByText( value=text )
  # end stock

  ##############################
  #####      USERNAME      #####
  ##############################
  elif sensor == 'username':
    text = self.username+'@'+self.hostname
    self.drawText( ctxLayer, text )
    self.setLineByText( value=text )
  # end username

  ##############################
  #####       DISTRO       #####
  ##############################
  elif sensor == 'distro':
    self.drawText( ctxLayer, self.distro )
    self.setLineByText()
  # end distro

  ##############################
  #####       KERNEL       #####
  ##############################
  elif sensor == 'kernel':
    self.drawText( ctxLayer, 'Kernel: '+self.kernel )
    self.setLineByText()
  # end kernel

  ##############################
  #####       CPUNAME      #####
  ##############################
  elif sensor == 'cpuname':
    text = self.cpuname
    self.drawText( ctxLayer, text )
    self.setLineByText( value=text )
  # end cpuname

  ##############################
  #####    CPUFREQUENCY    #####
  ##############################
  elif sensor == 'cpufrequency':
    for key,frequency in enumerate(self.cpufrequency):
      self.drawText( ctxLayer, 'CPU'+str(key+1)+' frequency: '+frequency+' MHz' )
      self.setLineByText()
  # end cpufrequency

  ##############################
  #####        CPUS        #####
  ##############################
  elif sensor == 'cpus':
    if self.sensorsCpus0: start = 0
    else: start = 1

    for key in range( start, self.cpusNum+1 ):
      icon = 'cpus'
      if not re.search( '[a|A][m|M][d|D]', self.cpuname ) == None: icon += 'Amd'
      drawIcon( self, icon )
      drawGraph( self, ctxLayer, self.graphTypeCpus, self.cpusLoad[key] )
      self.drawText( ctxLayer, self.cpusLoad[key]+'% CPU'+str(key), 0, self.getLine()+2, self.width-10, align=pango.ALIGN_RIGHT )
      self.setLineByGraph( type=self.graphTypeCpus )
  # end cpus

  ##############################
  #####        LOAD        #####
  ##############################
  elif sensor == 'load':
    self.drawText( ctxLayer, 'Load: '+self.load )
    self.setLineByText()
  # end load

  ##############################
  #####     NVIDIAINFO     #####
  ##############################
  elif sensor == 'nvidiaInfo':
    if self.nvidiaShowGpu:
      self.drawText( ctxLayer, 'GPU: '+self.nvidiaInfo['gpu'] )
      self.setLineByText()

    if self.nvidiaShowRam:
      self.drawText( ctxLayer, 'RAM: '+self.nvidiaInfo['ram']+' MB' )
      self.setLineByText()

    if self.nvidiaShowDriver:
      self.drawText( ctxLayer, 'GPU driver: '+self.nvidiaInfo['driver'] )
      self.setLineByText()

    if self.nvidiaShowReolution:
      self.drawText( ctxLayer, 'Resolution: '+self.nvidiaInfo['resolution'][0]+'x'+self.nvidiaInfo['resolution'][1] )
      self.setLineByText()

    if self.nvidiaShowRefreshRate:
      self.drawText( ctxLayer, 'Refresh rate: '+self.nvidiaInfo['refreshRate'] )
      self.setLineByText()

    if self.nvidiaShowGpuFrequency:
      self.drawText( ctxLayer, 'GPU frequency: '+self.nvidiaInfo['gpuFrequency']+' MHz' )
      self.setLineByText()

    if self.nvidiaShowMemFrequency:
      self.drawText( ctxLayer, 'MEM frequency: '+self.nvidiaInfo['memFrequency']+' MHz' )
      self.setLineByText()

    if self.nvidiaShowTemp:
      drawIcon( self, 'nvidia' )
      drawGraph( self, ctxLayer, self.graphTypeNvidiaTemp, self.nvidiaTemp )
      self.drawText( ctxLayer, 'nVidia temp: '+self.nvidiaInfo['temp']+' \xc2\xb0C', y=self.getLine()+2 )
      self.setLineByGraph( type=self.graphTypeNvidiaTemp )
  # end nvidiaTemp

  ##############################
  #####       MEMORY       #####
  ##############################
  elif sensor == 'memory':
    drawIcon( self, 'memory' )
    drawGraph( self, ctxLayer, self.graphTypeMemory, self.memory )

    self.drawText( ctxLayer, 'RAM: '+self.memory+'%', y=self.getLine()+2 )
    self.setLineByGraph( type=self.graphTypeMemory )
  # end memory

  ##############################
  #####        SWAP        #####
  ##############################
  elif sensor == 'swap':
    drawIcon( self, 'swap' )
    drawGraph( self, ctxLayer, self.graphTypeSwap, self.swap )

    self.drawText( ctxLayer, 'Swap: '+self.swap+'%', y=self.getLine()+2 )
    self.setLineByGraph( type=self.graphTypeSwap )
  # end swap

  ##############################
  #####      LOCAL IP      #####
  ##############################
  elif sensor == 'localIp':
    text = 'Local IP: '+self.localIp+' ('+self.localIpDevice+')'
    self.drawText( ctxLayer, text )
    self.setLineByText()
  # end localIp

  ##############################
  #####     EXTERNAL IP    #####
  ##############################
  elif sensor == 'externalIp':
    self.drawText( ctxLayer, 'Ext IP: '+self.externalIp )
    self.setLineByText()
  # end externalIp

  ##############################
  #####       UPLOAD       #####
  ##############################
  elif sensor == 'upload':
    drawIcon( self, 'upload' )
    drawGraph( self, ctxLayer, self.graphTypeDownUp, self.netLoadUpload, oppositeColor=True )

    self.drawText( ctxLayer, 'Upload: '+self.upload+' KB/s', y=self.getLine()+1 )
    self.setLineByGraph( type=self.graphTypeDownUp )
  # end upload

  ##############################
  #####      DOWNLOAD      #####
  ##############################
  elif sensor == 'download':
    drawIcon( self, 'download' )
    drawGraph( self, ctxLayer, self.graphTypeDownUp, self.netLoadDownload, oppositeColor=True )

    self.drawText( ctxLayer, 'Download: '+self.download+' KB/s', y=self.getLine()+1 )
    self.setLineByGraph( type=self.graphTypeDownUp )
  # end download

  ##############################
  #####   NET STATISTIC    #####
  ##############################
  elif sensor == 'netStatistic':
    self.drawText( ctxLayer, 'Network statistic' )
    self.setLineByText()

    drawIcon( self, 'netStatistic' )

    self.drawText( ctxLayer, 'Upload: '+self.netStatisticUpload )
    self.setLineByText()
    self.drawText( ctxLayer, 'Download: '+self.netStatisticDownload )
    self.setLineByText()
  # end download

  ##############################
  #####         RSS        #####
  ##############################
  elif sensor == 'rss':

    self.clearClickData( 'RSS' )

    for key in range( self.rssNum ):
      if ( ( key == 0 and self.rssUrl0 == '') or
           ( key == 1 and self.rssUrl1 == '') or
           ( key == 2 and self.rssUrl2 == '') ):
        continue

      self.setColor( ctxLayer, self.colorGraphBackground )
      self.draw_rectangle( ctxLayer, 0, self.getLine(), self.width, self.getHeightText() )

      self.setColor( ctxLayer, self.colorText )
      self.drawText( ctxLayer, self.rssData[key]['title'] )
      self.setLineByText()

      for x,item in enumerate( self.rssData[key]['items'] ):
        if x >= self.rssItems: break

        foo = {
          'function' : self.openBrowser,
          'args' : ( item['link'], ),
          'title' : item['title'],
          'start' : self.getLine(),
        }

        text = item['title']
        self.drawText( ctxLayer, text )
        self.setLineByText( value=text )

        foo['end'] = self.getLine()
        self.clickData[ 'RSS '+str(x) ] = foo

  # end rss

  ##############################
  #####        DISKS       #####
  ##############################
  elif sensor == 'disks':

    self.clearClickData( 'DISK' )

    for disk in self.disks:

      foo = {
        'function' : self.openDirectory,
        'args' : ( disk['mount'], ),
        'name' : disk['name'],
        'start' : self.getLine(),
      }
      if self.disksType == 'free': bar = True
      else: bar = False

      self.setColor( ctxLayer, self.colorGraphBackground )
      self.draw_rectangle( ctxLayer, 0, self.getLine(), self.width, self.getHeightGraph()*2+4 )
      self.setColor( ctxLayer, self.colorText )

      self.drawText( ctxLayer, disk['name'], 3, self.getLine()+2, align=pango.ALIGN_LEFT )
      self.drawText( ctxLayer, disk['mount'], 70, self.getLine()+2, align=pango.ALIGN_LEFT )
      self.setLineByGraph()

      drawIconCtx( self, ctxLayer, 'disks' )
      drawGraph( self, ctxLayer, self.graphTypeDisks, disk['usage%'], drawBackground=False, oppositeColor=bar )

      self.drawText( ctxLayer, disk['usage']+' of '+disk['capacity']+' / '+disk['usage%']+'%', y=self.getLine()+2 )
      self.setLineByGraph()

      foo['end'] = self.getLine()
      self.clickData[ 'DISK '+disk['name'] ] = foo

  # end disks

  ##############################
  #####       BATTERY      #####
  ##############################
  elif sensor == 'battery':
    if self.battery != '':
      drawIcon( self, 'battery' )
      drawGraph( self, ctxLayer, self.graphTypeBattery, self.batteryLoad, oppositeColor=True )
      self.drawText( ctxLayer, self.battery+': '+self.batteryLoad+'%' )
      self.setLineByGraph()

    else:
      self.drawText( ctxLayer, 'No battery' )
      self.setLineByText()
  # end battery

  ##############################
  #####      WIRELESS      #####
  ##############################
  elif sensor == 'wireless':
    if self.battery != '':
      drawIcon( self, 'wireless' )
      drawGraph( self, ctxLayer, self.graphTypeWireless, self.wirelessLoad, oppositeColor=True )
      self.drawText( ctxLayer, self.wireless+': '+self.wirelessLoad+'%' )
      self.setLineByGraph()

    else:
      self.drawText( ctxLayer, 'No wireless' )
      self.setLineByText()
  # end wireless

  ##############################
  #####     PROCESSES      #####
  ##############################
  elif sensor == 'processes':
    if self.processesType == 'basic':
      for line in self.processes:
        self.drawText( ctxLayer, line, font=self.fontHard, fontSize=self.fontSize-2 )
        self.setLineByText( -2 )

    else:
      for key in range( self.processesNum ):
        self.drawText( ctxLayer, self.processes[key]['cpu'], 10, font=self.fontHard, fontSize=self.fontSize-2, align=pango.ALIGN_LEFT )
        self.drawText( ctxLayer, self.processes[key]['mem'], 40, font=self.fontHard, fontSize=self.fontSize-2, align=pango.ALIGN_LEFT )
        self.drawText( ctxLayer, self.processes[key]['command'], 80, font=self.fontHard, fontSize=self.fontSize-2, align=pango.ALIGN_LEFT )
        self.setLineByText( -2 )
  # end wireless

  ##############################
  #####       UPTIME       #####
  ##############################
  elif sensor == 'uptime':
    self.drawText( ctxLayer, 'Uptime: '+self.uptime )
    self.setLineByText()
  # end uptime

  ##############################
  #####     LOGINTIME      #####
  ##############################
  elif sensor == 'logintime':
    self.drawText( ctxLayer, 'Logintime: '+self.logintime )
    self.setLineByText()
  # end logintime

  ##############################
  #####     TEMPERATURE    #####
  ##############################
  elif sensor == 'temperature1':
    drawIcon( self, 'temperature' )
    self.drawText( ctxLayer, 'Temp: '+self.temperature1 )
    self.setLineByText()

  ##############################
  #####     FAN            #####
  ##############################
  elif sensor == 'fan1':
    drawIcon( self, 'fan' )
    self.drawText( ctxLayer, 'Fan: '+self.fan1 )
    self.setLineByText()

# end draw()
