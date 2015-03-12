from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, StringProperty
from os.path import dirname, join
from kivy.uix.settings import SettingsWithSidebar
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.properties import ObjectProperty, OptionProperty, BoundedNumericProperty
from kivy.uix.label import Label
from kivy.adapters.simplelistadapter import SimpleListAdapter
from kivy.adapters.listadapter import ListAdapter
from kivy.uix.listview import ListItemButton
from kivy.uix.listview import ListView
from kivy.uix.button import Button
import logging
import xml.etree.ElementTree as ET
import math
import re
import re


LOG_FILENAME = 'GUI_log.log'
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

xmlFilePath = '..//ui.xml'

class DataItem(object):
    def __init__(self, text='', is_selected=False):
        self.text = text
        self.is_selected = is_selected

class DataShowcase(Screen):
    fullscreen = BooleanProperty(False)
    tree = ET.parse(xmlFilePath)

    vertical_tolerance = NumericProperty(float(list(tree.iter('vertical'))[0].text))
    horizontal_tolerance = NumericProperty(float(list(tree.iter('horizontal'))[0].text))
    gps_spacing = NumericProperty(float(list(tree.iter('gps_spacing'))[0].text))

    def add_widget(self, *args):
        if 'content' in self.ids:
            return self.ids.content.add_widget(*args)
        return super(DataShowcase, self).add_widget(*args)

class TridentLayoutApp(App):
    index = NumericProperty(-1)
    screen_names = ListProperty([])
    hierarchy = ListProperty([])

    def build(self):
        self.buildtitle = "Poseidon Build"
        self.screens = {}
        self.available_screens = ['TextInputs','DataCarousel']
        self.screen_names = self.available_screens
        cur_dir = dirname(__file__)
        self.available_screens = [join(cur_dir, '{}.kv'.format(fn)) for fn in self.available_screens]
        self.go_next_screen()

    def go_previous_screen(self):
        self.index = (self.index - 1) % len(self.available_screens)
        screen = self.load_screen(self.index)
        sm = self.root.ids.sm
        sm.switch_to(screen, direction='right')
    def go_next_screen(self):
        self.index = (self.index + 1) % len(self.available_screens)
        screen = self.load_screen(self.index)
        sm = self.root.ids.sm
        sm.switch_to(screen, direction='left')

    def lat_long_to_Oregon_Grid(self, lat, lon, zone):
        # this is a direct translation of the MATLAB code Geodetic2SPS
        # check input
        if ((lat > 360 and lat < 0) or (long > 360 and long < 0)):
            print 'Your input for lat or long has to be in degrees'
            return
        #init variables
        Lat0 = 0
        LatS = 0
        LatN = 0
        Eo = 0
        #load GRS80 constants.
        a = 6378137.0 # meters
        f = float(1/298.257222101)
        e = math.sqrt(2*f-math.pow(f,2))
        #define zones in NAD83
        OREGON_N_ZONE = 3601
        OREGON_S_ZONE = 3602
        lambdacm = 120.5
        Nb = 0
        # check which zone
        if zone == OREGON_N_ZONE:
            Lat0 = float(43.0+40.0/60.0)
            LatS = float(44.0+20.0/60.0)
            LatN = 46.0
            Eo = 2500000.0

        if zone == OREGON_S_ZONE:
            Lat0 = float(41.0+40.0/60.0)
            LatS = float(42.0+20.0/60.0)
            LatN = 44.0
            Eo = 1500000.0 #meters

        if zone != OREGON_S_ZONE and zone != OREGON_N_ZONE:
            print 'Your zone input is wrong'
            return

        sin_lat_d = float(math.sin(float(lat*math.pi/180)))
        cos_lat_d = float(math.cos(float(lat*math.pi/180)))
        LatS_d = float(math.sin(float(LatS)*math.pi/180))
        LatN_d = float(math.sin(float(LatN*math.pi/180)))
        Lat0_d = float(math.sin(float(Lat0)*math.pi/180))


        W = float(math.sqrt(1-math.pow(e,2)*(math.pow(sin_lat_d, 2))))
        M = float(cos_lat_d / W)
        T = float(math.sqrt(float(((1-sin_lat_d)/ (1+sin_lat_d)) * math.pow(((1+e*sin_lat_d) / (1-e*sin_lat_d)), e))))

        w1 = float(math.sqrt(float(1-math.pow(e,2)*(math.pow(LatS_d,2)))))
        w2 = float(math.sqrt(float(1-math.pow(e,2)*(math.pow(LatN_d, 2)))))

        m1 = float(math.cos(LatS*math.pi/180) / w1)
        m2 = float(math.cos(LatN*math.pi/180) / w2)

        t0 = float(math.sqrt(float(((1-Lat0_d) /(1+Lat0_d))*math.pow(((1+e*Lat0_d)/(1-e*Lat0_d)),e))))
        t1 = float(math.sqrt(float(((1-LatS_d) /(1+LatS_d))*math.pow(((1+e*LatS_d)/(1-e*LatS_d)),e))))
        t2 = float(math.sqrt(float(((1-LatN_d) /(1+LatN_d))*math.pow(((1+e*LatN_d)/(1-e*LatN_d)),e))))

        n = float((math.log(m1)- math.log(m2)) / (math.log(t1)- math.log(t2)))

        F =float(m1 / (n*math.pow(t1,n)))
        Rb = float(a*F*math.pow(t0,n))
        gamma = float((lambdacm-lon) *n)

        R = a*F*math.pow(T,n)
        k =(R*n) / (a*M)

        easting = R*math.sin(gamma*math.pi/180) + Eo
        northing = Rb - R*math.cos(gamma*math.pi/180)+Nb
        result = "%f   %f  %f  %f\n" % (northing, easting, k, gamma)
        return result

    def quality_reader(self):
        #this part is solely for demoing.
        #basically read from a known output file
        #and check of the coordinates are of output value of 4
        count = 0
        with open('../output/cart_2014-11-17-1.txt') as f:
            lines = f.readlines()
        for x in range(len(lines)):
            if (lines[x][0].isdigit()):
                print lines[x][0]
                print 'bad data'
            else:
                count = count + 1
        result = 'There are %d quality points' % count
        return result
    def popup_open(self):
        list_simple_adapter = SimpleListAdapter(data=["Router 1", "Router 2", "Router 3"], cls=Label)
        list_view = ListView(adapter=list_simple_adapter)
        popup = Popup(title="Router Selections", content=list_view, size_hint=(None, None), size=(250, 250))
        popup.open()

    def dms_degree_conversion(self, DMS):
        #split DMS string into array and
        #perform conversion
        result = re.split('\s+', DMS)
        degree = int(result[0])
        dec_min = float(result[1]) / 60.0
        dec_sec = float(result[2]) / 3600.00
        decimal_degrees = float(degree+dec_min+dec_sec)

        result = '%d %f' % (degree, decimal_degrees)
        return result
    def go_screen(self, idx):
        self.index = idx
        self.root.ids.sm.switch_to(self.load_screen(idx), direction='left')

    def go_hierarchy_previous(self):
        ahr = self.hierarchy
        if len(ahr) == 1:
            return
        if ahr:
            ahr.pop()
        if ahr:
            idx = ahr.pop()
            self.go_screen(idx)

    def load_screen(self, index):
        if index in self.screens:
            return self.screens[index]
        screen = Builder.load_file(self.available_screens[index].lower())
        self.screens[index] = screen
        return screen

    def display_settings(self, settings):
        p = self.settings_popup
        if p is None:
            self.settings_popup = p = Popup(content=settings, title='Settings', size_hint=(0.8, 0.8))
        if p.content is not settings:
            p.content = settings
        p.open()

    def set_settings_cls(self, panel_type):
        self.settings_cls = panel_type

    def set_display_type(self, display_type):
        self.destroy_settings()
        self.display_type = display_type

    def dropdown(self,loc):
        receiverList = []
        tree = ET.parse(xmlFilePath)
        RSearch = tree.iter('receiver')
        for r in RSearch:
            if (list(r)[0].text).upper() == 'T':
                receiverList.append(Button(text="%s"%(str(list(r)[4].text))))
                Button.bind(on_release=self.choiceReceiver(loc))
        list_adapter = ListAdapter(data=receiverList,
                                    allow_empty_selection=False,
                                    selection_mode='single',
                                    cls=ListItemButton)
        list_view = ListView(adapter=list_adapter)
        popup = Popup(title="Receivers", content=list_view, size_hint=(None, None), size=(250, 250))
        popup.open()

    def choiceReceiver(self,loc):
        print "chose %s for %s receiver"%(ListAdapter.selection,loc)

    def submit(self,horizontal,vertical,gps_spacing):
        tree = ET.parse(xmlFilePath)
        horizontal = float(horizontal)
        vertical = float(vertical)
        gps_spacing = float(gps_spacing)

        horizontal = float(re.sub('[^\.0-9]','',horizontal))
        vertical = float(re.sub('[^\.0-9]','',vertical))
        gps_spacing = float(re.sub('[^\.0-9]','',gps_spacing))

        if self.verifyToleranceValues(horizontal,vertical,gps_spacing):
            if vertical != DataShowcase.vertical_tolerance:
                list(tree.iter('vertical'))[0].text = str(vertical)
            if horizontal != DataShowcase.horizontal_tolerance:
                list(tree.iter('horizontal'))[0].text = str(horizontal)
            if gps_spacing != DataShowcase.gps_spacing:
                list(tree.iter('gps_spacing'))[0].text = str(gps_spacing)
            if horizontal != DataShowcase.horizontal_tolerance or \
               vertical != DataShowcase.vertical_tolerance or \
               gps_spacing != DataShowcase.gps_spacing:
                tree.write(xmlFilePath)

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


TridentLayoutApp().run()

