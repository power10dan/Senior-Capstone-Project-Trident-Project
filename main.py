from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
import logging
import xml.etree.ElementTree as ET
import re
import Connecter
from kivy.clock import Clock
import threading
from multiprocessing import Process

LOG_FILENAME = 'GUI_log.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

xmlFilePath = 'ui.xml'
     
#found on http://kivy.org/docs/api-kivy.uix.textinput.html
class FloatInput(TextInput):

    pat = re.compile('[^0-9]')
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)
        
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
        
    def popup(self,button,title): 
        layout = BoxLayout(orientation='vertical')
        popup = Popup(attach_to=self,title=str(title),title_align = 'center',size_hint = (.5,.5))
        for r in self.tree.iter('receiver'):
            if (list(r)[0].text).upper() == 'F':
                btn = Button(text='%s' % str(list(r)[4].text), size_y = 5)
                btn.bind(on_press = lambda x: setattr(button, 'text', str(x.text)))
                btn.bind(on_release = popup.dismiss)
                layout.add_widget(btn)
        popup.content = layout
        popup.open()
        
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
                self.tree.write(xmlFilePath)

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
    app = ObjectProperty(None)
    survey = ObjectProperty(None)
    thread = ObjectProperty(None)
    multipathingAlert = ObjectProperty(None)
    nonMultipathQueue = ObjectProperty(None)
    
    
    def __init__(self, **kwargs):
        super(Poseidon, self).__init__(**kwargs)
        
        self.survey.bind(on_release = self.updateSurvey)
        
    def updateSurvey(self,instance):    
        if instance.text == 'Start Survey':
            self.survey.text = 'End Survey'
            if self.app.config.get('settingsMenu','lockSettings') == 'False':
                self.app.config.set('settingsMenu','lockSettings','True')
                self.app.config.write()
            self.startSurvey()    
        else:
            self.survey.text = 'Start Survey'
            if self.app.config.get('settingsMenu','lockSettings') == 'True':
                self.app.config.set('settingsMenu','lockSettings','False')
                self.app.config.write()
            self.endSurvey()
    
    def Settings_Button_pressed(self):      
        if self.settings_popup is None:
            self.settings_popup = Popup(attach_to=self, title='Trident Settings', size_hint=(0.7,0.8))
            self.settings_popup.content = SettingsMenu(root=self)
            
            self.settings_popup.content.vertical_tolerance.text = self.app.config.get('tolerances','vertical')
            self.settings_popup.content.horizontal_tolerance.text = self.app.config.get('tolerances','horizontal')
            self.settings_popup.content.gps_spacing.text = self.app.config.get('tolerances','gps_spacing')
            self.settings_popup.content.antennaHeight.text = self.app.config.get('tolerances','antennaHeight')
            self.settings_popup.content.phaseCenter.text = self.app.config.get('tolerances','phaseCenter')
            self.settings_popup.content.leftReceiver.text = self.app.config.get('receiver','leftReceiver')
            self.settings_popup.content.centerReceiver.text = self.app.config.get('receiver','centerReceiver')
            self.settings_popup.content.rightReceiver.text = self.app.config.get('receiver','rightReceiver')
        if self.app.config.get('settingsMenu','lockSettings') == 'False':
            self.settings_popup.open()
        
    def startSurvey(self):
        self.thread = threading.Thread(target=Connecter.connectOutput().passiveThreads,args=(3,'e',multipathingAlert,nonMultipathQueue,))
        self.thread.daemon = True
        self.thread.start()
        
    def endSurvey(self):
        self.thread.join()
            
class TridentApp(App):
    def build(self):
        self.poseidonWidget = Poseidon(app=self)
        self.root = self.poseidonWidget

        if self.config.get('settingsMenu','lockSettings') == 'True':
            self.config.set('settingsMenu','lockSettings','False')
            self.config.write()
                
    def build_config(self, config):     
        
        config.adddefaultsection('settingsMenu')
        config.setdefault('settingsMenu','lockSettings','False')
        
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

