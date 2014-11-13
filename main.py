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
imprt xml.dom as X

ser = []
active = []
multiQueue = []
log = 0
#G = geodetic.geodetic()   # TODO : we might want to make geodetic a static method?
#M = MultipathDetector.MultipathDetector()
xmlFilePath = 'ui.xml'


class connectOutput:

    # Searches and opens serial connections
    # Called from: thread
    def initSerial(self, i):
        comNum = self.portSearch()        
        # configure and open serial connections
        global ser, xmlFilePath, active
        tree = X.parse(xmlFilePath)
        serialConfig = tree.getElementsByTagName("serial")
        p = serial.Serial()
        p.port = comNum
        p.baudrate = int(serialConfig.find("baudrate").text)
        p.bytesize = int(serialConfig.find("bytesize").text)
        p.stopbits = int(serialConfig.find("stopbits").text)
        p.timeout = int(serialConfig.find("timeout").text)
        active.append(comNum)
        ser.append(p)
        p.open()
        p.isOpen()
        print 'OPEN: '+ ser[i].name
    
    # Handles thread logistics, creates logs, calls multipathQueueHandler
    # Called from: main
    def thread(self):
        global log, multiQueue,M
        signal.signal(signal.SIGINT, self.signalHandler)

        print "How many receivers are you connecting?"
        r = raw_input()
        if not r.isdigit():
            print "Invalid number of receivers, exiting!!!"
            sys.exit(0)
        r = int(r)
        if r == 3:
            self.createQueue()
           
        log = open('.\output\output_'+ str(datetime.date.today())+'.txt','a')
        #print log.name
        
        for i in range(0, r):
            thread = threading.Thread(target=self.initSerial(i))
            thread.daemon = True
            thread.start()
        while True:
            for i in range(0, r):
                thread = threading.Thread(target=self.streamSerial(str(i))).run()
            if (r == 3 and len(multiQueue[0]) == 10 and 
                    len(multiQueue[1]) == 10 and 
                    len(multiQueue[2]) == 10):
                #print multiQueue
                multipathing = MultipathDetector().multipathQueueHandler(multiQueue)
                print "Multipathing: " = str(multipathing)
    
    # Scan for available ports. Return a list of tuples (num, name)
    # Called from: portSearch
    def scan(self):
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
                cartesian = geodetic().geo(lat, lon)
                northing, easting, k , gamma = cartesian
                print "cartesian: " + str(cartesian)
                self.queueAppend(name, (northing,easting))
        line_str = name + ":" + str(line)
        print line_str
        log.writelines(line_str)
        
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
    def queueAppend(self, int(name), coor):
        global multiQueue
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
    def portSearch(self):
        print "Use existing(e) devices or search(s) for devices?"
        input = raw_input()
        if input == 'e':
            available = []
            tree = X.parse(xmlFilePath)
            RSearch = tree.getElementsByTagName("receiver")
            print "Found Devices:"
            for r in range(len(RSearch)):
                print "Serial Number: " + RSearch[r][serialNumber] + ", port: " + RSearch[r][port]
                available.append(RSearch[r][port])
            print "Choose a COM port #. Enter # only, then enter"
            temp = raw_input()
            if temp != 'q' or (temp not in available) or not temp.isdigit():
                print "Invalid Port, exiting!!!"
                sys.exit(0)
            return 'COM' + temp #concatenate COM and the port number to define serial port    
        elif input == 's':
            print "Found Ports:"
            for n, s in self.scan():
                print "%s" % s
            print " "
            print "Choose a COM port #. Enter # only, then enter"
            temp = raw_input()
            if temp != 'q' or not temp.isdigit():
                print "Invalid Port, exiting!!!"
                sys.exit(0)
            return 'COM' + temp #concatenate COM and the port number to define serial port
        else:
            print "Invalid input, exiting!!!"
            sys.exit(0)
        
        
run = connectOutput()
run.thread()



