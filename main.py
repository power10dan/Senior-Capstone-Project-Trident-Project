from pynmea import nmea
import serial, time, sys, datetime, shutil, threading, signal
from collections import deque
#import utm
from threading import Lock
import geodetic
import MultipathDetector
import xml.etree.ElementTree as ET

######Global Variables#####################################################
# you must declare the variables as 'global' in the fxn before using#
ser = []
active = []
mutex = Lock()
multQueue = []
log = 0
G = geodetic.geodetic()   # TODO : we might want to make geodetic a static method?
M = MultipathDetector.MultipathDetector()
xmlFilePath = 'ui.xml'
######FUNCTIONS############################################################ 
class connect_output:
    def init_serial(self, i):
        #opens the serial port based on the COM number you choose
        print "Found Ports:"
        for n, s in self.scan():
            print "%s" % s
        print " "
        #enter your COM port number
        print "Choose a COM port #. Enter # only, then enter"
        temp = raw_input() #waits here for keyboard input
        if temp != 'e' and not temp.isdigit():
            print "Invalid Port, exiting!!!"
            sys.exit(0)
        comNum = 'COM' + temp #concatenate COM and the port number to define serial port
        # configure the serial connections
        global ser,xmlFilePath
        tree = ET.parse(xmlFilePath)
        nmea = tree.find("nmea")
        
        
        p = serial.Serial()
        p.port = comNum
        p.baudrate = int(nmea.find("baudrate").text)
        p.bytesize = int(nmea.find("bytesize").text)
        p.stopbits = int(nmea.find("stopbits").text)
        print p
        global active
        active.append(comNum)
        ser.append(p)

        p.open()
        p.isOpen()
        print 'OPEN: '+ ser[i].name

    def signal_handler(self, signal, frame):
        global ser, log
        if log != 0:
            log.close()
        for	n in range(0, len(ser)):
            ser[n].close()
        sys.exit(0)

    def thread(self):
        global log, multQueue,M
        signal.signal(signal.SIGINT, self.signal_handler)

        print "How many receivers are you connecting?"
        r = raw_input()
        if not r.isdigit():
            print "Invalid number of receivers, exiting!!!"
            sys.exit(0)
        
        r = int(r)
        
        if r == 3:
            self.createQueue()
            
        for i in range(0, r):
            thread = threading.Thread(target=self.init_serial(i))
            thread.daemon = True
            thread.start()
        
        log = open('.\output\output_'+ str(datetime.date.today())+'.txt','a')
        print log.name
        while 1:
            for i in range(0, r):
                thread = threading.Thread(target=self.stream_serial(str(i))).run()
            if r == 3 and len(multQueue[0]) == 10 and len(multQueue[1]) == 10 and len(multQueue[2]) == 10:
                print multQueue
                M.multipathQueueHandler(multQueue)    

    def scan(self):
        #scan for available ports. return a list of tuples (num, name)
        global active
        available = []
        for i in range(256):
            try:
                s = serial.Serial(i)
                if s.name in active:
                    break
                else:
                    available.append((i, s.name))
                    s.close()   # explicit close 'cause of delayed GC in java
            except serial.SerialException:
                pass
        return available

    def stream_serial(self, name):
        #stream data directly from the serial port
        global log, multQueue,G
        line = ser[int(name)].readline()
        if line[3:6] == 'GGA':
            data = nmea.GPGGA()
            data.parse(line)

            if len(line) > 50:
                lat = self.degrees(data.latitude)
                lon = self.degrees(data.longitude)

                print str(name) + " latitude: " + str(lat)
                print str(name) + " longitude: " + str(lon)

                cartesian = G.geo(lat, lon)
                northing, easting, k , gamma = cartesian
                print "cartesian: " + str(cartesian)
                multQueue[int(name)].append((northing,easting))
                
                #print utm.from_latlon(self.degrees(data.latitude), self.degrees(data.longitude))
        line_str = name + ":" + str(line)
        print line_str
        log.writelines(line_str)
        
    def createQueue(self):
        for i in range(3):
            temp =  deque(maxlen = 10)
            multQueue.append(temp)
        

    def degrees(self, coor):
        if len(coor.split('.')[0])%2 == 0:
            degrees = float(coor[:2])
            minutes = float(coor[2:])/60
        else:
            degrees = float(coor[:3])
            minutes = float(coor[3:])/60
        return degrees + minutes


########START#####################################################################################
run = connect_output()
run.thread()



