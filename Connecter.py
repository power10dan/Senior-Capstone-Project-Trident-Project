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
import logging


LOG_FILENAME = '.\logs\log_'+ datetime.datetime.now().strftime('%Y-%m-%d') +'.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s %(levelname)s: %(message)s')
log = None

class connectOutput:
	notify = None
	thread_stop = None
	rawQueue = []
	xdata = {}
	timeout = [] #used for checking if signal to receiver lost
	ser = []
	active = []
	multiQueue = []
	multiQueueFlag = False # used to check if multipath queues are allocated and used to auto select receivers
	G = geodetic.geodetic()   # TODO : we might want to make geodetic a static method?
	M = MultipathDetector.MultipathDetector()
	xmlFilePath = 'ui.xml'
	
	def __init__(self,notify,thread_stop,**kwargs):
		self.notify = notify
		self.thread_stop = thread_stop
		self.timeout = []
		self.ser = []
		self.active = []
		self.multiQueue = []
		self.multiQueueFlag = False
	
	# Searches and opens serial connections
	# Called from: thread
	def initSerial(self, i, input):
		comNum = self.portSearch(i,input)        
		# configure and open serial connections
		tree = ET.parse(self.xmlFilePath)
		serialConfig = tree.iter('serial')
		serialConfig = list(serialConfig)
		p = serial.Serial()
		p.port = comNum
		p.baudrate = int(serialConfig[0][0].text)
		p.bytesize = int(serialConfig[0][1].text)
		p.stopbits = int(serialConfig[0][2].text)
		p.timeout = int(serialConfig[0][3].text)
		self.active.append(comNum)
		self.ser.append(p)
		try:
			p.open()
			p.isOpen()
			print 'OPEN: '+ self.ser[i].name
		except serial.SerialException:
			print "Error opening port, exiting!!!"
			sys.exit(0)
	
	def passiveThreads(self, r, input):
		global log
		r = int(r)
		self.createQueue(self.multiQueue)
		self.createQueue(self.rawQueue)
		self.multiQueueFlag = True
		logging.info('user search input: %s'%(input))
		log = open('.\output\output_'+ str(datetime.date.today())+'.txt','a') 
		for i in range(0, r):
			if self.thread_stop.is_set():
				self.signalHandler()
				return
			self.initSerial(i,input)
			logging.info('Created Thread: %s'%(i))
			self.timeout.append(0)
		while True:
			if self.thread_stop.is_set():
				self.signalHandler()
				return
			for i in range(0, r):
				self.streamSerial(str(i))
			if (r == 3 and len(self.multiQueue[0]) == 10 and 
					len(self.multiQueue[1]) == 10 and 
					len(self.multiQueue[2]) == 10):
				multipathing = self.M.multipathQueueHandler(self.multiQueue)
				self.notify(int(3),multipathing,self.rawQueue)
				print multipathing
				# if the units are out of order (mislabeled), then exit this loop
				if self.M.mislabeledFlag != 0:
					self.thread_stop.set()
		
	# Handles thread logistics, creates logs, calls multipathQueueHandler
	# Called from: main
	def thread(self):
		global log
		#signal.signal()
		print "How many receivers are you connecting?"
		r = raw_input()
		logging.info('user devices input: %s'%(r))
		if not r.isdigit():
			print "Invalid number of receivers, exiting!!!"
			logging.warn('Bad Input')
			sys.exit(0)
		r = int(r)
		
		if r == 3:
			self.createQueue(self.multiQueue)
			self.multiQueueFlag = True
		print "Use existing(e) devices or scan(s) for devices?"
		input = raw_input()
		logging.info('user search input: %s'%(input))
		log = open('.\output\output_'+ str(datetime.date.today())+'.txt','a') 
		for i in range(0, r):
			self.initSerial(i,input)
			logging.info('Created Thread: %s'%(i))
			self.timeout.append(0)
		while True:
			for i in range(0, r):
				self.streamSerial(str(i))
			if (r == 3 and len(self.multiQueue[0]) == 10 and 
					len(self.multiQueue[1]) == 10 and 
					len(self.multiQueue[2]) == 10):
				multipathing = self.M.multipathQueueHandler(self.multiQueue)
				mult = "Multipathing: " + str(multipathing)
				print mult
	
				# if the units are out of order (mislabeled), then exit this loop
				if self.M.mislabeledFlag != 0:
					break
	
	# Outputs stuff from serial to console and log file
	# Called from: thread
	def streamSerial(self, name):
		global log
		line = self.ser[int(name)].readline()
		if line[3:6] == 'GGA':
			self.timeout[int(name)] = 0
			data = nmea.GPGGA()
			data.parse(line)
			if len(line) > 50:
				lat = self.degrees(data.latitude)
				lon = self.degrees(data.longitude)
				cartesian = self.G.geo(lat, lon)
				northing, easting, k , gamma = cartesian
				c = "cartesian: " + str(cartesian)
				self.xdata.update({'easting': easting,'northing': northing,'latd': lat,'lond': lon}) 
				self.xdata = self.extendData(data,self.xdata)
				if int(data.gps_qual) == 4:
					self.queueAppend(self.multiQueue, name, (northing, easting, data.antenna_altitude))
					self.queueAppend(self.rawQueue, name, self.xdata)
				line_str = name + ":" + str(line)
				self.notify(int(name),self.xdata)
			else:
				line_str = "Bad Signal: " + line  
			print line_str
		else:
			if len(line) == 0:
				self.timeout[int(name)] += 1
				if(self.timeout[int(name)] >= 10):
					print "Receiver %s disconnected"%(name)
					self.ser[int(name)].close()
					while not self.ser[int(name)].isOpen():
						try:
							self.ser[int(name)] = serial.Serial(self.active[int(name)])
							print "Re-established connection to receiver %s"%(name)
						except serial.SerialException:
							print "failed to re-establish connection to receiver %s"%(name)
			else:
				print "Received something other than GGA message from receiver: " + line
		log.writelines(str(line))
	
	def extendData(self,data,xd):
		xd['timestamp'] = data.timestamp
		xd['latitude'] = data.latitude
		xd['lat_direction'] = data.lat_direction
		xd['longitude'] = data.longitude 
		xd['lon_direction'] = data.lon_direction
		xd['gps_qual'] = data.gps_qual
		xd['num_sats'] = data.num_sats
		xd['horizontal_dil'] = data.horizontal_dil
		xd['antenna_altitude'] = data.antenna_altitude
		xd['altitude_units'] = data.altitude_units
		xd['geo_sep'] = data.geo_sep
		xd['geo_sep_units'] = data.geo_sep_units
		xd['age_gps_data'] = data.age_gps_data
		xd['ref_station_id'] = data.ref_station_id
		return xd
		
			# xdata['latitude'] = data.latitude
	
	# Creates a list of queues inside of global list named multiQueue
	# Only used when connecting 3 receivers, sets max length of queues to 10
	# Called from: thread
	def createQueue(self,q):
		for i in range(3):
			temp =  deque(maxlen = 10)
			q.append(temp)
	
	# Append cartesian coordinates to queues within multiQueue list
	# When the length of queue being appended equals 10, it pops left values off queue
	# Called from: stream_serial
	def queueAppend(self, q, name, coor):
		name = int(name)
		if len(q[name]) == 10:
			q[name].popleft()
		q[name].append(coor)
	
	# Converts degrees, minutes and decimal minutes into degrees and decimal degrees
	# Called from: stream_serial
	def degrees(self, coor):
		if len(coor.split('.')[0])%2 == 0:
			degrees = float(coor[:2])
			minutes = float(coor[2:])/60
		else:
			degrees = float(coor[:3])
			minutes = float(coor[3:])/60
		#logging.debug('original Degree minutes: %s \t Converted Degree decimal degree: %s'%(coor,str(degrees + "." + minutes)))
		return degrees + minutes
	
	# Signal handler function, closes log, and closes serial connections
	# Called from: thread
	def signalHandler(self):
		global log
		if log != 0:
			log.close()
			logging.info('Closed log file')
		if len(self.ser) != 0:
			for n in range(0, len(self.ser)):
				self.ser[n].close()
				self.ser.pop(n)
				logging.info('Closing serial port: %s'%(self.ser[n]))
		#sys.exit(0)
	
		# Scan for available ports. Return a list of tuples (num, name)
	# Called from: portSearch
	def scan(self, ports, loc = ['']*256):
		available = []
		for i,loc in zip(ports,loc):
			try:
				s = serial.Serial(i)
				if s.name in self.active:
					break
				else:
					available.append((s.name,loc))
					s.close()   # explicit close 'cause of delayed GC in java
			except serial.SerialException:
				pass
		return available
	
	def portsFound(self, a):
		print "Found Devices:"
		for s, loc in a:
			print "%s" % s
			logging.info('Found ports: %s'%(s))
		print "Choose a COM port #. Enter # only, then enter"
		temp = raw_input()
		if temp == 'q' or not temp.isdigit():
			print "Invalid Port, exiting!!!"
			logging.info('Bad input port, exiting program')
			sys.exit(0)
		return 'COM' + temp #concatenate COM and the port number to define serial port
	
	# Searches for devices or ports available and returns COM number
	# Called from: initSerial
	def portSearch(self, threadNum, input):
		if input == 'e':
			avail = []
			location = []
			tree = ET.parse(self.xmlFilePath)
			RSearch = tree.iter('receiver')
			for r in RSearch:
				if (list(r)[0].text).upper() == 'T' and (('COM'+list(r)[5].text) not in self.active):
					if (list(r)[1].text).upper() == 'T':
						avail.append((int(list(r)[5].text)-1))
						location.append('L')
					elif (list(r)[2].text).upper() == 'T':
						avail.append((int(list(r)[5].text)-1))
						location.append('R')
					elif (list(r)[3].text).upper() == 'T':
						avail.append((int(list(r)[5].text)-1))
						location.append('C')
					else:
						avail.append((int(list(r)[5].text)-1))
			avail = self.scan(avail,location)
			if self.multiQueueFlag == True:
				for s, loc in avail:
					if int(threadNum) == 0 and loc == 'L':
						logging.info('Using %s for left receiver'%(s))
						return s
					if int(threadNum) == 1 and loc == 'C':
						logging.info('Using %s for center receiver'%(s))
						return s
					if int(threadNum) == 2 and loc == 'R':
						logging.info('Using %s for right receiver'%(s))
						return s
			if len(avail) != 0:
				return self.portsFound(avail)
			else:
				if __name__ == "__main__":
					print "No active devices found. Switching to scan mode"
					logging.info('No active devices selected, switching to scan mode')
					self.portSearch(threadNum,'s')
				elif self.thread_stop != None:
					if self.thread_stop.is_set():
						return
					else:
						if __name__ == "__main__":
							print "No active devices found. Switching to scan mode"
							logging.info('No active devices selected, switching to scan mode')
							self.portSearch(threadNum,'s')
						
		elif input == 's':
			avail = self.scan(range(256))
			if len(avail) != 0:   
				return self.portsFound(avail)
			else:
				print "No ports found, exiting!!!"
				sys.exit(0)
		else:
			logging.info('Invalid User input for port search')
			print "Invalid input, exiting!!!"
			sys.exit(0)
	
	
def outputToCSV():
    pass

if __name__ == "__main__":
    connectOutput(None,None).thread()