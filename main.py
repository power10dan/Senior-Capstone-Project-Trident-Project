from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock, mainthread
from Connecter import connectOutput
import xml.etree.ElementTree as ET
import re
import logging
import os
import threading
from functools import partial
from kivy.graphics import Color, Ellipse, Line
from collections import deque
from kivy.config import Config

LOG_FILENAME = 'GUI_log.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

xmlFilePath = 'ui.xml'

class SurveyPage(Widget):
	base = ObjectProperty(None)
	epochInput = ObjectProperty(None)
	measureButton = ObjectProperty(None)
	graph = ObjectProperty(None)
	multiCounterLabel = ObjectProperty(None)
	counterLabel = ObjectProperty(None)
	gps1Status = ObjectProperty(None)
	gps2Status = ObjectProperty(None)
	gps3Status = ObjectProperty(None)
	multiPStatus = ObjectProperty(None)
	gps_qual = ObjectProperty(None)
	num_sats = ObjectProperty(None)
	antenna_altitude = ObjectProperty(None)
	geo_sep = ObjectProperty(None)
	horizontal_dil = ObjectProperty(None)
	age_gps_data = ObjectProperty(None)
	counter = None
	amoritizedNorthing = ObjectProperty(None)
	amoritizedEasting = ObjectProperty(None)
	graphZoom = ObjectProperty(None)
	zoomLabel = ObjectProperty(None)
	
	def __init__(self, **kwargs):
		super(SurveyPage, self).__init__(**kwargs)
		self.measureButton.bind(on_release=self.updateMeasureButton)
		self.graphZoom.bind(value=self.outputZoom)
		
	def outputZoom(self,instance,value):
		self.zoomLabel.text = 'x'+str(float(value)/4)

	def updateMeasureButton(self,instance):
		if instance.text == 'Measure Point' and self.base.app.config.get('locks','lockSurvey') == 'True':
			instance.text = 'Stop'
			self.base.app.config.set('locks', 'measuring', 'True')
			self.base.app.config.set('job', 'currentPointName', self.base.dataCarousel.current_slide.pointName)
			self.base.app.config.write()
			if epochInput != '0':
				self.base.dataCarousel.epochCount = int(epochInput)
		else:
			instance.text = 'Measure Point'
			self.base.app.config.set('locks', 'measuring', 'False')
			self.base.app.config.set('job', 'currentPointName', '')
			self.base.app.config.write()
			self.outputResultsToCSV()

	def outputResultsToCSV(self):
		pointName = self.base.dataCarousel.current_slide.pointName
		pointCode = self.base.dataCarousel.current_slide.pointCode
		latitude = self.base.dataCarousel.current_slide.latitude
		longitude = self.base.dataCarousel.current_slide.longitude
		northing = self.base.dataCarousel.current_slide.northing
		easting = self.base.dataCarousel.current_slide.easting
		altitude = self.base.dataCarousel.current_slide.altitude

		self.counter = self.base.dataCarousel.current_slide.counter
		if self.counter != 0:
			latitude = latitude / self.counter
			longitude = longitude / self.counter
			northing = northing / self.counter
			easting = easting / self.counter
			altitude = altitude / self.counter

			csvFile = open(self.base.jobPath+'/'+str(self.base.app.config.get('job','jobName'))+'.csv', 'a')
			finalOutputString = str(pointName)+','+str(latitude)+','+str(longitude)+','+str(northing)+','+str(easting)+','+str(altitude)+','+str(pointCode)
			csvFile.writelines(finalOutputString)


################################################################################################################
################################################################################################################

class PointPopUp(BoxLayout):
	root = ObjectProperty(None)
	def updatePointPass(self,Name,Code):
		self.root.updatePointName(Name,Code)

################################################################################################################
################################################################################################################

class SettingsMenu(GridLayout):
    tree = ET.parse(xmlFilePath)
    root = ObjectProperty(None)
    vertical_tolerance = ObjectProperty(None)
    horizontal_tolerance = ObjectProperty(None)
    gps_spacing = ObjectProperty(None)
    antennaHeight = ObjectProperty(None)
    phaseCenter = ObjectProperty(None)
    leftReceiver = ObjectProperty(None)
    centerReceiver = ObjectProperty(None)
    rightReceiver = ObjectProperty(None)
    verticalLabel = ObjectProperty(None)
    horizontalLabel = ObjectProperty(None)
    gpsSpacingLabel = ObjectProperty(None)
    antennaLabel = ObjectProperty(None)
    phaseLabel = ObjectProperty(None)
	
    def __init__(self, **kwargs):
		super(SettingsMenu, self).__init__(**kwargs)
		self.vertical_tolerance.bind(text = self.updateVerticalTolerance)
		self.horizontal_tolerance.bind(text = self.updateHorizontalTolerance)
		self.gps_spacing.bind(text = self.updateGPSSpacing)
		self.antennaHeight.bind(text = self.updateAntennaHeight)
		self.phaseCenter.bind(text = self.updatePhaseCenter)
		self.leftReceiver.bind(text = self.updateLeftReceiver)
		self.rightReceiver.bind(text = self.updateRightReceiver)
		self.centerReceiver.bind(text = self.updateCenterReceiver)

    def updateLeftReceiver(self, instance, value):
		for r in self.tree.iter('receiver'):
			if (list(r)[4].text) == self.root.app.config.get('receiver','leftReceiver'):
				list(r)[0].text = 'F'
				list(r)[1].text = 'F'
		for r in self.tree.iter('receiver'):
			if (list(r)[4].text) == value:
				list(r)[0].text = 'T'
				list(r)[1].text = 'T'
		self.root.app.config.set('receiver','leftReceiver',str(value))
		self.root.app.config.write()
		self.tree.write(xmlFilePath)


    def updateCenterReceiver(self, instance, value):
		for r in self.tree.iter('receiver'):
			if (list(r)[4].text) == self.root.app.config.get('receiver','centerReceiver'):
				list(r)[0].text = 'F'
				list(r)[3].text = 'F'
		for r in self.tree.iter('receiver'):
			if (list(r)[4].text) == value:
				list(r)[0].text = 'T'
				list(r)[3].text = 'T'
		self.root.app.config.set('receiver','centerReceiver',str(value))
		self.root.app.config.write()
		self.tree.write(xmlFilePath)

    def updateRightReceiver(self, instance, value):
		for r in self.tree.iter('receiver'):
			if (list(r)[4].text) == self.root.app.config.get('receiver','rightReceiver'):
				list(r)[0].text = 'F'
				list(r)[2].text = 'F'
		for r in self.tree.iter('receiver'):
			if (list(r)[4].text) == value:
				list(r)[0].text = 'T'
				list(r)[2].text = 'T'
		self.root.app.config.set('receiver','rightReceiver',str(value))
		self.root.app.config.write()
		self.tree.write(xmlFilePath)


    def clearReceiver(self, receiver):
		blank = ''
		for r in self.tree.iter('receiver'):
			if (list(r)[4].text) == self.root.app.config.get('receiver', receiver):
				list(r)[0].text = 'F'
				list(r)[1].text = 'F'
				list(r)[2].text = 'F'
				list(r)[3].text = 'F'
		self.root.app.config.set('receiver', receiver, blank)
		self.root.app.config.write()

    def updateVerticalTolerance(self, instance, value):
		if float(value) >= 0.0 and float(value) < 0.16:
			self.verticalLabel.text = ''
			self.root.app.config.set('tolerances', 'vertical', str(float(re.sub('[^\.0-9]', '', value))))
			self.root.app.config.write()
		else:
			self.verticalLabel.text = '!'

    def updateHorizontalTolerance(self, instance, value):
		if float(value) >= 0.0 and float(value) < 0.11:
			self.horizontalLabel.text = ''
			self.root.app.config.set('tolerances','horizontal', str(value))
			self.root.app.config.write()
		else:
			self.horizontalLabel.text = '!'

    def updateGPSSpacing(self, instance, value):
		if float(value) > 0.44 and float(value) < 0.56:
			self.gpsSpacingLabel.text = ''
			self.root.app.config.set('tolerances','gps_spacing', str(value))
			self.root.app.config.write()
		else:
			self.gpsSpacingLabel.text = '!'

    def updateAntennaHeight(self, instance, value):
		self.root.app.config.set('tolerances','antennaHeight',str(value))
		self.root.app.config.write()

    def updatePhaseCenter(self, instance, value):
		self.root.app.config.set('tolerances','phaseCenter',str(value))
		self.root.app.config.write()

    def receiverPopup(self,button,title):
		layout = BoxLayout(orientation='vertical')
		pop = Popup(attach_to=self,title=str(title),title_align = 'center',size_hint = (.5,.5))
		for r in self.tree.iter('receiver'):
			if (list(r)[0].text).upper() == 'F':
				btn = Button(text='%s' % str(list(r)[4].text), size_y = 5)
				btn.bind(on_press = lambda x: setattr(button, 'text', str(x.text)))
				btn.bind(on_release = pop.dismiss)
				layout.add_widget(btn)
		pop.content = layout
		pop.open()

    def submit(self,horizontal,vertical,gps_spacing,antennaHeight,phaseCenter):
        updateTolerance = False
        try:
            if self.verifyToleranceValues(float(horizontal),float(vertical),float(gps_spacing)):
                if vertical != list(self.tree.iter('vertical'))[0].text:
                    updateTolerance = True
                    list(self.tree.iter('vertical'))[0].text = vertical
                if horizontal != list(self.tree.iter('horizontal'))[0].text:
                    updateTolerance = True
                    list(self.tree.iter('horizontal'))[0].text = horizontal
                if gps_spacing != list(self.tree.iter('gps_spacing'))[0].text:
                    updateTolerance = True
                    list(self.tree.iter('gps_spacing'))[0].text = gps_spacing
                if antennaHeight != list(self.tree.iter('antennaHeight'))[0].text:
                    updateTolerance = True
                    list(self.tree.iter('antennaHeight'))[0].text = antennaHeight
                if phaseCenter != list(self.tree.iter('phaseCenter'))[0].text:
                    updateTolerance = True
                    list(self.tree.iter('phaseCenter'))[0].text = phaseCenter
                if updateTolerance:
                    self.root.settings_popup.dismiss()
                    self.tree.write(xmlFilePath)
                    popup_notif = Popup(attach_to=self,title='Settings', size_hint=(.3,.2))
                    content= Label(text ='Successfully submitted!')
                    content.bind(on_touch_up = popup_notif.dismiss)
                    popup_notif.content = content
                    popup_notif.open()
            popup_notesubmit = Popup(attach_to=self, title='Settings', size_hint=(.3,.2))
            content = Label(text='Submitted tolerances')
            content.bind(on_touch_up=popup_notesubmit.dismiss)
            popup_notesubmit.content = content
            popup_notesubmit.open()
        except ValueError:
            box = BoxLayout()
            box.add_widget(Label(text='There are fields in the settings menu that are empty.'))
            popup = Popup(title='Warning', content=box, size_hint = (None, None), size=(400,400))
            popup.open()
	# Checks tolerance inputs to ensure they are within the allowed range
	# Returns 'False' if values are unacceptable, 'True' otherwise, and creates a warning in GUI_log.log
    def verifyToleranceValues(self, horizontalToleranceInput, altitudeToleranceInput, gps_distance):
		# NOTE: units are in meters
		if horizontalToleranceInput < 0 or horizontalToleranceInput > 0.10:
			logging.warn('horizontal tolerance outside of allowed range - input value between 0.0m and 0.10m')
			return False
		elif altitudeToleranceInput < 0 or altitudeToleranceInput > 0.15:
			logging.warn('altitude tolerance outside of allowed range - input value between 0.0m and 0.15m')
			return False
		elif gps_distance != 0.50:
			logging.warn('gps_distance outside of allowed range - only currently accepted value is 0.50m')
			return False
		else:
			return True

################################################################################################################
################################################################################################################

class Poseidon(Widget):
	settings_popup = None
	jobName = None
	job_popup = None
	point_popup = None
	thread = None
	pointRaw = None
	pointCollected = None
	currentPoint = None
	optionalData = None
	thread_stop = threading.Event()
	app = ObjectProperty(None)
	survey = ObjectProperty(None)
	nonMultipathQueue = ObjectProperty(None)
	jobNameLabel = ObjectProperty(None)
	pointNameLabel = ObjectProperty(None)
	jobNameButton = ObjectProperty(None)
	newPointButton = ObjectProperty(None)
	dataCarousel = ObjectProperty(None)
	newPage = ObjectProperty(None)
	root = ObjectProperty(None)
	base = ObjectProperty(None)
	multiQ = None
	workingSlide =  -1


	def __init__(self, **kwargs):
		super(Poseidon, self).__init__(**kwargs)

		self.survey.bind(on_release = self.updateSurveyButton)
		self.jobNameButton.bind(on_release = self.updateJob)
		self.newPointButton.bind(on_release = self.updatePoint)

	def updateSurveyButton(self,instance):
		if instance.text == 'Start Survey':
			self.survey.text = 'End Survey'
			if self.app.config.get('locks','lockSettings') == 'False':
				self.app.config.set('locks','lockSettings','True')
				self.app.config.set('locks','lockSurvey','True')
				self.app.config.set('locks','lockPoint','False')
				self.app.config.write()
			self.startSurvey()
		else:
			self.survey.text = 'Start Survey'
			if self.app.config.get('locks','lockSettings') == 'True':
				self.app.config.set('locks','lockSettings','False')
				self.app.config.set('locks','lockSurvey','False')
				self.app.config.set('locks','lockPoint','True')
				self.app.config.write()
			self.endSurvey()

	def updateJob(self,instance):
		#print self.dataCarousel.children[0].children
		if self.job_popup is None:
			self.job_popup = Popup(attach_to=self, title='Survey Name',title_align = 'center',size_hint=(0.5,None),padding=10)
			job = TextInput(multiline= False)
			job.bind(on_text_validate = lambda t: self.updateJobName(t.text))
			self.job_popup.content = job
		if self.app.config.get('locks','lockSurvey') == 'False':
			self.job_popup.open()

	def	updateJobName(self, text):
		self.job_popup.dismiss()
		self.jobNameLabel.text = text
		self.app.config.set('job','jobName',str(text))
		self.app.config.write()

	def updatePoint(self, instance):
		if self.app.config.get('locks','lockPoint') == 'False':
			self.point_popup = Popup(attach_to=self, title='Point Name',title_align = 'center',size_hint=(.3,.4),padding=10)
			self.point_popup.content = PointPopUp(root=self)
			self.point_popup.open()

	def	updatePointName(self, text, code):
		self.point_popup.dismiss()
		newPage = SurveyPage(base=self)
		newPage.create_property('pointName')
		newPage.pointName = text
		self.app.config.set('job','currentPointName',str(text))
		self.app.config.write()
		newPage.create_property('pointCode')
		newPage.pointCode = code
		newPage.create_property('latitude')
		newPage.create_property('longitude')
		newPage.create_property('northing')
		newPage.create_property('easting')
		newPage.create_property('altitude')
		newPage.create_property('counter')
		newPage.create_property('multiCounter')
		newPage.counter = 0.0
		newPage.epochCount = 0
		newPage.epochCounter = 0
		newPage.multiCounter = 0.0
		newPage.easting = 0.0
		newPage.northing = 0.0
		newPage.altitude = 0.0
		newPage.latitude = 0.0
		newPage.longitude = 0.0
		newPage.gps1Status.bind(on_touch_up=self.openOptional)
		newPage.gps2Status.bind(on_touch_up=self.openOptional)
		newPage.gps3Status.bind(on_touch_up=self.openOptional)
		self.dataCarousel.add_widget(newPage)
		self.dataCarousel.load_slide(newPage)

		self.workingSlide = self.workingSlide + 1
		
		
	def Settings_Button_pressed(self):
		#self.dataCarousel.children[self.workingSlide].children[0].gps_qual.text = 'hi'
		if self.settings_popup is None:
			self.settings_popup = Popup(attach_to=self, title='Trident Settings', title_align = 'center', size_hint=(0.7,0.8))
			self.settings_popup.content = SettingsMenu(root=self)
			self.settings_popup.content.vertical_tolerance.text = self.app.config.get('tolerances','vertical')
			self.settings_popup.content.horizontal_tolerance.text = self.app.config.get('tolerances','horizontal')
			self.settings_popup.content.gps_spacing.text = self.app.config.get('tolerances','gps_spacing')
			self.settings_popup.content.antennaHeight.text = self.app.config.get('tolerances','antennaHeight')
			self.settings_popup.content.phaseCenter.text = self.app.config.get('tolerances','phaseCenter')
			self.settings_popup.content.leftReceiver.text = self.app.config.get('receiver','leftReceiver')
			self.settings_popup.content.centerReceiver.text = self.app.config.get('receiver','centerReceiver')
			self.settings_popup.content.rightReceiver.text = self.app.config.get('receiver','rightReceiver')
		if self.app.config.get('locks','lockSettings') == 'False':
			self.settings_popup.open()

	def startSurvey(self):
		self.jobPath = "./output/"+str(self.app.config.get('job','jobName'))
		if not os.path.exists(self.jobPath):
			os.makedirs(self.jobPath)
		self.thread = threading.Thread(target=self.secondThread)
		self.thread.start()


	def secondThread(self):
		self.thread_stop.clear()
		Clock.schedule_once(connectOutput(self.updateOutput,self.thread_stop).passiveThreads(3,'e'))

	def endSurvey(self):
		if self.app.config.get('locks','measuring'):
			self.app.config.set('locks','measuring','False')
			self.app.config.write()
		self.thread_stop.set()

	def gpsStatus(self,receiver,qual):
		if int(qual) <= 3:
			receiver.source = "yellow.png"
		elif int(qual) == 4:
			receiver.source = "green.png"
		else:
			receiver.source = "red.png"

	@mainthread
	def updateOutput(self,name,nmea, q=None):
		try: 
			if self.app.config.get('locks','lockSurvey') == 'True':
				if not os.path.isfile(self.jobPath+'/'+self.app.config.get('job','currentPointName')+'_raw.txt'):
					self.pointRaw = open(self.jobPath+'/'+self.app.config.get('job','currentPointName')+'_raw.txt','a')			
			if name == 0:
				self.gpsStatus(self.dataCarousel.current_slide.gps1Status,nmea['gps_qual'])
				if name == self.optionalData:
					self.optionalDisplay(nmea)
				#print nmea
				self.pointRaw.writelines(str(1)+str(nmea)+str('\n'))
			elif name == 1:
				self.gpsStatus(self.dataCarousel.current_slide.gps2Status,nmea['gps_qual'])
				if name == self.optionalData:
					self.optionalDisplay(nmea)
				self.pointRaw.writelines(str(2)+str(nmea)+str('\n'))
			elif name == 2:
				self.gpsStatus(self.dataCarousel.current_slide.gps3Status,nmea['gps_qual'])
				if name == self.optionalData:
					self.optionalDisplay(nmea)
				self.pointRaw.writelines(str(3)+str(nmea)+str('\n'))
			elif name == 3:
				
				if len(self.multiQ) == 10:
					self.multiQ.popleft()
				if nmea == False or nmea == (False, False):
					self.dataCarousel.current_slide.multiPStatus.text = "Ready to Measure!"
					self.amoratizeData(q[1][9])
					#print q[1][9]
					self.dataCarousel.current_slide.counter = self.dataCarousel.current_slide.counter + 1
					self.dataCarousel.current_slide.counterLabel.text = str(self.dataCarousel.current_slide.counter)
					self.multiQ = False
					if self.app.config.get('locks','measuring') == 'True':
						if not os.path.isfile(self.jobPath+'/'+self.app.config.get('job','currentPointName')+'.txt'):
							self.pointCollected = open(self.jobPath+'/'+self.app.config.get('job','currentPointName')+'.txt','a')
						else:
							self.pointCollected.writelines(str(q[1][9])+str('\n'))
							if self.dataCarousel.current_slide.epochCount == 0:
								pass
							elif self.dataCarousel.current_slide.epochCounter < self.dataCarousel.current_slide.epochCount and self.dataCarousel.current_slide.epochCount != 0:
								self.dataCarousel.current_slide.epochCounter = self.dataCarousel.current_slide.epochCounter + 1
							else:
								SurveyPage.updateMeasureButton(self.dataCarousel.current_slide.measureButton)
				else:
					self.dataCarousel.current_slide.multiPStatus.text = "Multipathing!"
					self.dataCarousel.current_slide.multiCounter = self.dataCarousel.current_slide.multiCounter + 1
					self.dataCarousel.current_slide.multiCounterLabel.text = str(self.dataCarousel.current_slide.multiCounter)
					self.multiQ = True
				if float(self.dataCarousel.current_slide.counter) > 10 :
					self.plotPoints(q[1][9])
		except:
			pass

	@mainthread
	def plotPoints(self, newCoor):
		centerX = self.dataCarousel.current_slide.easting/self.dataCarousel.current_slide.counter
		centerY = self.dataCarousel.current_slide.northing/self.dataCarousel.current_slide.counter
		tolerance = float(self.app.config.get('tolerances', 'horizontal'))
		w = self.dataCarousel.current_slide.graph.width/2
		h = self.dataCarousel.current_slide.graph.height/2
		zoom = float(self.dataCarousel.current_slide.graphZoom.value)

		self.dataCarousel.current_slide.graph.canvas.before.add(Line(circle=(w,h,(2*w*zoom)),width=1.3)) #circle=(centerX,centerY,size),thickness)
		
		
		diffYDec = (newCoor['northing'] % int(newCoor['northing'])) - (centerY % int(centerY))
		diffXDec = (newCoor['easting'] % int(newCoor['easting'])) - (centerX % int(centerX))

		diffYInt = int(newCoor['northing'])-int(centerY)
		diffXInt = int(newCoor['easting'])-int(centerX)

		diffY = diffYInt + diffYDec
		diffX = diffXInt + diffXDec
		
		offsetX = ((-1.0 * diffX) / (4.0*tolerance))*zoom
		offsetY = ((-1.0 * diffY) / (4.0*tolerance))*zoom

		if self.multiQ[i]:
			self.dataCarousel.current_slide.graph.canvas.add(Color(1,0,0))
		else:
			self.dataCarousel.current_slide.graph.canvas.add(Color(0,0,1))
		
		self.dataCarousel.current_slide.graph.canvas.add(Ellipse(pos=(((w)- offsetX - 5), ((h) - offsetY - 5)), size=(10,10)))

	@mainthread
	def amoratizeData(self, dataEpochDict):	
		self.dataCarousel.current_slide.latitude += float(dataEpochDict['latd'])
		self.dataCarousel.current_slide.longitude += float(dataEpochDict['lond'])
		self.dataCarousel.current_slide.northing += float(dataEpochDict['northing'])
		self.dataCarousel.current_slide.easting += float(dataEpochDict['easting'])
		self.dataCarousel.current_slide.altitude += float(dataEpochDict['antenna_altitude'])
		self.dataCarousel.current_slide.amoritizedNorthing.text = str(self.dataCarousel.current_slide.northing/self.dataCarousel.current_slide.counter)
		self.dataCarousel.current_slide.amoritizedEasting.text = str(self.dataCarousel.current_slide.easting/self.dataCarousel.current_slide.counter)
		
		
	def openOptional(self,instance,pos):
		if instance.collide_point(pos.x,pos.y):
			self.optionalData = int(instance.name)
			
	def optionalDisplay(self,nmea):
		self.dataCarousel.current_slide.geo_sep.text = str(nmea['geo_sep'])
		self.dataCarousel.current_slide.num_sats.text = str(nmea['num_sats'])
		self.dataCarousel.current_slide.gps_qual.text = str(nmea['gps_qual'])
		self.dataCarousel.current_slide.horizontal_dil.text = str(nmea['horizontal_dil'])
		self.dataCarousel.current_slide.age_gps_data.text = str(nmea['age_gps_data'])
		self.dataCarousel.current_slide.antenna_altitude.text = str(nmea['antenna_altitude'])

################################################################################################################
################################################################################################################

class TridentApp(App):
	def on_stop(self):
		self.root.thread_stop.set()


	def build(self):
		Config.set('graphics', 'width', '1100')
		Config.set('graphics', 'height', '800')

		self.poseidonWidget = Poseidon(app=self)
		self.root = self.poseidonWidget
		
		
		self.root.jobNameLabel.text = self.config.get('job','jobName')

		if self.config.get('locks','lockSettings') == 'True':
			self.config.set('locks','lockSettings','False')
			self.config.write()

		if self.config.get('locks','lockPoint') == 'False':
			self.config.set('locks','lockPoint','True')
			self.config.write()

		if self.config.get('locks','measuring') == 'True':
			self.config.set('locks','measuring','False')
			self.config.write()

		if self.config.get('locks','lockSurvey') == 'True':
			self.config.set('locks','lockSurvey','False')
			self.config.write()

		if self.config.get('job','currentPointName') != '':
			self.config.set('job','currentPointName','')
			self.config.write()

	def build_config(self, config):

		config.adddefaultsection('job')
		config.setdefault('job','jobName','')
		config.setdefault('job','currentPointName','')


		config.adddefaultsection('locks')
		config.setdefault('locks','lockSettings','False')
		config.setdefault('locks','lockPoint','True')
		config.setdefault('locks','lockSurvey','False')
		config.setdefault('locks','measuring','False')


		config.adddefaultsection('receiver')
		config.setdefault('receiver','leftReceiver','')
		config.setdefault('receiver','centerReceiver','')
		config.setdefault('receiver','rightReceiver','')

		config.adddefaultsection('tolerances')
		config.setdefault('tolerances','gps_spacing','0.5')
		config.setdefault('tolerances','vertical', '0.1')
		config.setdefault('tolerances','horizontal','0.05')
		config.setdefault('tolerances','antennaHeight','2.02')
		config.setdefault('tolerances','phaseCenter','0.05')

		config.adddefaultsection('coordinateSystem')
		config.setdefault('coordinateSystem','zone','3601')

		config.adddefaultsection('serialSettings')
		config.setdefault('serialSettings','baudrate','115200')
		config.setdefault('serialSettings','bytesize','8')
		config.setdefault('serialSettings','stopbits','1')
		config.setdefault('serialSettings','timeout','1')

if __name__ == "__main__":
    TridentApp().run()

