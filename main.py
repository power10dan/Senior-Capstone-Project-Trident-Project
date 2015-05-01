from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock, mainthread
import logging
import xml.etree.ElementTree as ET
import re
import Connecter
import threading
import os

LOG_FILENAME = 'GUI_log.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

xmlFilePath = 'ui.xml'

class SurveyPage(Widget):
	base = ObjectProperty(None)
	counterLabel = ObjectProperty(None)
	epochInput = ObjectProperty(None)
	measureButton = ObjectProperty(None)
	
	def __init__(self, **kwargs):
		super(SurveyPage, self).__init__(**kwargs)
		self.measureButton.bind(on_release = self.updateMeasureButton)

	def updateMeasureButton(self,instance):
		if instance.text == 'Measure Point' and self.base.app.config.get('locks','lockSurvey') == 'True':
			instance.text = 'Stop'
			self.base.app.config.set('locks','measuring','True')
			self.base.app.config.write()
		else:
			instance.text = 'Measure Point'
			self.base.app.config.set('locks','measuring','False')
			self.base.app.config.write()

	
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
		self.root.app.config.write
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
			if (list(r)[4].text) == self.root.app.config.get('receiver',receiver):
				list(r)[0].text = 'F'
				list(r)[1].text = 'F'
				list(r)[2].text = 'F'
				list(r)[3].text = 'F'
		self.root.app.config.set('receiver',receiver,str(blank))
		self.root.app.config.write

    def updateVerticalTolerance(self, instance, value):
		if float(value) >= 0.0 and float(value) < 0.16:
			self.verticalLabel.text = ''
			self.root.app.config.set('tolerances','vertical',str(float(re.sub('[^\.0-9]','',value))))
			self.root.app.config.write()
		else:
			self.verticalLabel.text = '!'

    def updateHorizontalTolerance(self, instance, value):
		if float(value) >= 0.0 and float(value) < 0.11:
			self.horizontalLabel.text = ''
			self.root.app.config.set('tolerances','horizontal',str(value))
			self.root.app.config.write()
		else:
			self.horizontalLabel.text = '!'

    def updateGPSSpacing(self, instance, value):
		if float(value) > 0.44 and float(value) < 0.56:
			self.gpsSpacingLabel.text = ''
			self.root.app.config.set('tolerances','gps_spacing',str(value))
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
			
class Poseidon(Widget):
	settings_popup = None
	job_popup = None
	point_popup = None
	thread_stop = None
	app = ObjectProperty(None)
	survey = ObjectProperty(None)
	thread = ObjectProperty(None)
	nonMultipathQueue = ObjectProperty(None)
	jobNameLabel = ObjectProperty(None)
	pointNameLabel = ObjectProperty(None)
	jobNameButton = ObjectProperty(None)
	newPointButton = ObjectProperty(None)
	dataCarousel = ObjectProperty(None)
	newPage = ObjectProperty(None)
	gpsOutput = ObjectProperty(None)
	homePage = ObjectProperty(None)
	
	def __init__(self, **kwargs):
		super(Poseidon, self).__init__(**kwargs)
	
		self.survey.bind(on_release = self.updateSurveyButton)
		self.jobNameButton.bind(on_release = self.updateJob)
		self.newPointButton.bind(on_release = self.updatePoint)
		
		self.gpsOutput = Label()
		self.homePage = GridLayout(cols = 4)
		self.homePage.add_widget(self.gpsOutput)
		self.dataCarousel.add_widget(self.homePage)
		self.homePage.create_property('name')
		self.homePage.name = "Home"
		self.dataCarousel.load_slide(self.homePage)
	
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
			layout = BoxLayout(orientation='vertical')
			self.point_popup = Popup(attach_to=self, title='Point Name',title_align = 'center',size_hint=(.3,.4),padding=10)
			point = TextInput(multiline= False)
			code = TextInput(multiline= False)
			point.bind(on_text_validate = lambda t: self.updatePointName(t.text))
			layout.add_widget(Label(text="point name:"))
			layout.add_widget(point)
			layout.add_widget(Label(text="point code:"))
			layout.add_widget(code)
			self.point_popup.content = layout
			self.point_popup.open()
	
	def	updatePointName(self, text):
		self.point_popup.dismiss()
		newPage = SurveyPage(base=self)
		self.dataCarousel.add_widget(newPage)
		newPage.create_property('name')
		newPage.name = text
		self.dataCarousel.load_slide(newPage)
	
	def Settings_Button_pressed(self):
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
		self.thread_stop = threading.Event()
		self.thread = threading.Thread(target=self.passiveThreads,args=(3,'e'))
		self.thread.daemon = True
		self.thread.start()
	
	def endSurvey(self):
		if self.app.config.get('locks','measuring'):
			self.app.config.set('locks','measuring','False')
			self.app.config.write()
		self.thread_stop.set()
		self.thread.join()
	
	def passiveThreads(self, r, input):
		Connecter.connectOutput().createQueue()
		Connecter.multiQueueFlag = True
		Connecter.logging.info('user search input: %s'%(input))
		Connecter.log = open('.\output\output_'+ str(Connecter.datetime.date.today())+'.txt','a') 

		for i in range(0, int(r)):
			thread = threading.Thread(target=Connecter.connectOutput().initSerial(i,input))
			thread.daemon = True
			thread.start()
			Connecter.logging.info('Created Thread: %s'%(i))
			Connecter.timeout.append(0)
		while True:
			if self.thread_stop.is_set():
				Connecter.connectOutput().signalHandler(0,0)
				return
			for i in range(0, r):
				thread = threading.Thread(target=Connecter.connectOutput().streamSerial(str(i))).run()
			if (r == 3 and len(Connecter.multiQueue[0]) == 10 and 
					len(Connecter.multiQueue[1]) == 10 and 
					len(Connecter.multiQueue[2]) == 10):
				#print multiQueue
				multipathing = Connecter.M.multipathQueueHandler(multiQueue)
				mult = "Multipathing: " + str(multipathing)
				print mult
				self.updateOutput(mult)
				#if not multipathing and Connecter.goodNmea != None:
				#	self.updateOutput(Connecter.goodNmea)
				# if the units are out of order (mislabeled), then exit this loop
				if M.mislabeledFlag != 0:
					self.thread_stop.set()
	@mainthread
	def updateOutput(self,nmea):
		self.gpsOutput.text = str(nmea)
		
	
class TridentApp(App):
	def build(self):
		self.poseidonWidget = Poseidon(app=self)
		self.root = self.poseidonWidget

		self.root.jobNameLabel.text = self.config.get('job','jobName')

		if self.config.get('locks','lockSettings') == 'True':
			self.config.set('locks','lockSettings','False')
			self.config.write()

		if self.config.get('locks','lockPoint') == 'False':
			self.config.set('locks','lockPoint','True')
			self.config.write()

		if self.config.get('locks','lockSurvey') == 'True':
			self.config.set('locks','lockSurvey','False')
			self.config.write()

	def build_config(self, config):

		config.adddefaultsection('job')
		config.setdefault('job','jobName','')

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

