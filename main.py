from pynmea import nmea
import serial
import sys
import datetime
import threading
import signal
from collections import deque
import geodetic
import MultipathDetector
import xml.etree.ElementTree as ET


ser = []
active = []
multiQueue = []
log = 0
allLog = 0
G = geodetic.geodetic()   # TODO : we might want to make geodetic a static method?
M = MultipathDetector.MultipathDetector()
xmlFilePath = 'ui.xml'
multiQueueFlag = 0

class connectOutput:
    # Searches and opens serial connections
    # Called from: thread
    def initSerial(self, i, input):
        comNum = self.portSearch(i,input)        
        # configure and open serial connections
        global ser, xmlFilePath, active
        tree = ET.parse(xmlFilePath)
        serialConfig = tree.iter('serial')
        serialConfig = list(serialConfig)
        p = serial.Serial()
        p.port = comNum
        p.baudrate = int(serialConfig[0][0].text)
        p.bytesize = int(serialConfig[0][1].text)
        p.stopbits = int(serialConfig[0][2].text)
        p.timeout = int(serialConfig[0][3].text)
        active.append(comNum)
        ser.append(p)
        try:
            p.open()
            p.isOpen()
            print 'OPEN: '+ ser[i].name
        except serial.SerialException:
            print "Error opening port, exiting!!!"
            sys.exit(0)
        
    # Handles thread logistics, creates logs, calls multipathQueueHandler
    # Called from: main
    def thread(self):
        global log, multiQueue, M
        signal.signal(signal.SIGINT, self.signalHandler)
        print "How many receivers are you connecting?"
        r = raw_input()
        if not r.isdigit():
            print "Invalid number of receivers, exiting!!!"
            sys.exit(0)
        r = int(r)
        if r == 3:
            self.createQueue()
            multiQueueFlag = 1
        print "Use existing(e) devices or scan(s) for devices?"
        input = raw_input()    
        log = open('.\output\output_'+ str(datetime.date.today())+'.txt','a')
        #allLog = open('.\output\Allout_'+ str(datetime.date.today())+'.txt','a')
        #print log.name      
        for i in range(0, r):
            thread = threading.Thread(target=self.initSerial(i,input))
            thread.daemon = True
            thread.start()
        while True:
            for i in range(0, r):
                thread = threading.Thread(target=self.streamSerial(str(i))).run()
            if (r == 3 and len(multiQueue[0]) == 10 and 
                    len(multiQueue[1]) == 10 and 
                    len(multiQueue[2]) == 10):
                #print multiQueue
                multipathing = M.multipathQueueHandler(multiQueue)
                mult = "Multipathing: " + str(multipathing)
                #allLog.writelines(str(mult))
                print mult
                
    
    # Scan for available ports. Return a list of tuples (num, name)
    # Called from: portSearch
    def scan(self, ports):
        global active
        available = []
        for i in ports:
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

    # Outputs stuff from serial to console and log file
    # Called from: thread
    def streamSerial(self, name):
        global log
        line = ser[int(name)].readline()
        if line[3:6] == 'GGA':
            data = nmea.GPGGA()
            data.parse(line)
            if len(line) > 50:
                lat = self.degrees(data.latitude)
                lon = self.degrees(data.longitude)
                #print str(name) + " latitude: " + str(lat)
                #print str(name) + " longitude: " + str(lon)
                cartesian = G.geo(lat, lon)
                northing, easting, k , gamma = cartesian
                c = "cartesian: " + str(cartesian)
                print c
                #allLog.writelines(str(c))
                if int(data.gps_qual) == 4:
                    self.queueAppend(name, (northing, easting))
                    #self.queueAppend(name, (northing, easting, data.antenna_altitude))
        line_str = name + ":" + str(line)
        print line_str
        log.writelines(line_str)
        #allLog.writelines(line_str)
        
    # Creates a list of queues inside of global list named multiQueue
    # Only used when connecting 3 receivers, sets max length of queues to 10
    # Called from: thread
    def createQueue(self):
        global multiQueue
        for i in range(3):
            temp =  deque(maxlen = 10)
            multiQueue.append(temp)
    
    # Append cartesian coordinates to queues within multiQueue list
    # When the length of queue being appended equals 10, it pops left values off queue
    # Called from: stream_serial
    def queueAppend(self, name, coor):
        global multiQueue
        name = int(name)
        if len(multiQueue[name]) == 10:
            multiQueue[name].popleft()
        multiQueue[name].append(coor)

    # Converts degrees, minutes and decimal minutes into degrees and decimal degrees
    # Called from: stream_serial
    def degrees(self, coor):
        if len(coor.split('.')[0])%2 == 0:
            degrees = float(coor[:2])
            minutes = float(coor[2:])/60
        else:
            degrees = float(coor[:3])
            minutes = float(coor[3:])/60
        return degrees + minutes
    
    # Signal handler function, closes log, and closes serial connections
    # Called from: thread
    def signalHandler(self, signal, frame):
        global ser, log
        if log != 0:
            log.close()
        for	n in range(0, len(ser)):
            ser[n].close()
        sys.exit(0)
    
    # Searches for devices or ports available and returns COM number
    # Called from: initSerial
    def portSearch(self, threadNum, input):
        global active
        if input == 'e':
            available = []
            tree = ET.parse(xmlFilePath)
            RSearch = tree.iter('receiver')
            for r in RSearch:
                if (list(r)[0].text).upper() == 'T' and (('COM'+list(r)[3].text) not in active):
                    available.append((int(list(r)[3].text)-1))
            available = self.scan(available)
            #if multiQueueFlag == 1 and len(available) == 3:
                    #if threadNum == 1 and 
                    #pass
            if len(available) != 0:
                print "Found Devices:"
                for n, s in available:
                    print "%s" % s
                print "Choose a COM port #. Enter # only, then enter"
                temp = raw_input()
                if temp == 'q' or not temp.isdigit():
                    print "Invalid Port, exiting!!!"
                    sys.exit(0)
                return 'COM' + temp #concatenate COM and the port number to define serial port  
            else:
                print "No active devices found. Switching to scan mode"
                self.portSearch('s')  
        elif input == 's':
            print "Found Ports:"
            for n, s in self.scan(range(256)):
                print "%s" % s
            print " "
            print "Choose a COM port #. Enter # only, then enter"
            temp = raw_input()
            if temp == 'q' or not temp.isdigit():
                print "Invalid Port, exiting!!!"
                sys.exit(0)
            return 'COM' + temp #concatenate COM and the port number to define serial port
        else:
            print "Invalid input, exiting!!!"
            sys.exit(0)
               
run = connectOutput()
run.thread()



