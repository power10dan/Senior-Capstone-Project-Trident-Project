from pynmea import nmea
import serial
import sys
import datetime
import signal
from collections import deque
import geodetic
import MultipathDetector
import xml.etree.ElementTree as ET
import logging
from multiprocessing import Process, active_children

LOG_FILENAME = '.\logs\log_'+ datetime.datetime.now().strftime('%Y-%m-%d') +'.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,format='%(asctime)s %(levelname)s: %(message)s')

timeout = [] #used for checking if signal to receiver lost
ser = []
active = []
multiQueue = []
log = 0
G = geodetic.geodetic()   # TODO : we might want to make geodetic a static method?
M = MultipathDetector.MultipathDetector()
xmlFilePath = 'ui.xml'
multiQueueFlag = False  # used to check if multipath queues are allocated and used to auto select receivers
goodNmea = None

class connectOutput(object):
	notify = None
	proc_stop = None
	def __init__(self,notify,proc_stop,**kwargs):
		self.notify = notify
		self.proc_stop = proc_stop
		
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
			#sys.exit(0)
			
	def passiveThreads(self, r, input):
		multiQueueFlag = True
		logging.info('user search input: %s'%(input))
		log = open('.\output\output_'+ str(datetime.date.today())+'.txt','a') 
		for i in range(0, int(r)):
			proc = Process(target=self.initSerial(i,input))
			proc.daemon = True
			proc.start()
			logging.info('Created Thread: %s'%(i))
			timeout.append(0)
		while True:
			if self.proc_stop:
				print "calling signal handler"
				self.signalHandler(0,0)
				return
			for i in range(0, r):
				proc = Process(target=self.streamSerial(str(i)))
				proc.run()
			if (r == 3 and len(multiQueue[0]) == 10 and 
					len(multiQueue[1]) == 10 and 
					len(multiQueue[2]) == 10):
				#print multiQueue
				multipathing = M.multipathQueueHandler(multiQueue)
				mult = "Multipathing: " + str(multipathing)
				print mult
				self.notify(mult)
				# if the units are out of order (mislabeled), then exit this loop
				if M.mislabeledFlag != 0:
					self.proc_stop.set()
	
	# Handles thread logistics, creates logs, calls multipathQueueHandler
	# Called from: main
#	def thread(self):
#		global log, multiQueue, M, multiQueueFlag
#		signal.signal(signal.SIGINT, self.signalHandler)
#		print "How many receivers are you connecting?"
#		r = raw_input()
#		logging.info('user devices input: %s'%(r))
#		if not r.isdigit():
#			print "Invalid number of receivers, exiting!!!"
#			logging.warn('Bad Input')
#			sys.exit(0)
#		r = int(r)
#		
#		if r == 3:
#			self.createQueue()
#			multiQueueFlag = True
#		print "Use existing(e) devices or scan(s) for devices?"
#		input = raw_input()
#		logging.info('user search input: %s'%(input))
#		log = open('.\output\output_'+ str(datetime.date.today())+'.txt','a') 
#		for i in range(0, r):
#			print threading.enumerate()
#			thread = threading.Thread(target=self.initSerial(i,input))
#			thread.daemon = True
#			thread.start()
#			logging.info('Created Thread: %s'%(i))
#			timeout.append(0)
#		while True:
#			for i in range(0, r):
#				thread = threading.Thread(target=self.streamSerial(str(i))).run()
#			if (r == 3 and len(multiQueue[0]) == 10 and 
#					len(multiQueue[1]) == 10 and 
#					len(multiQueue[2]) == 10):
#				#print multiQueue
#				multipathing = M.multipathQueueHandler(multiQueue)
#				mult = "Multipathing: " + str(multipathing)
#				print mult
#				
#				# if the units are out of order (mislabeled), then exit this loop
#				if M.mislabeledFlag != 0:
#					break

					
	# Outputs stuff from serial to console and log file
	# Called from: thread
	def streamSerial(self, name):
		global log, goodNmea
		line = ser[int(name)].readline()
		if line[3:6] == 'GGA':
			timeout[int(name)] = 0
			data = nmea.GPGGA()
			data.parse(line)
			if len(line) > 50:
				lat = self.degrees(data.latitude)
				lon = self.degrees(data.longitude)
				cartesian = G.geo(lat, lon)
				northing, easting, k , gamma = cartesian
				c = "cartesian: " + str(cartesian)
				if int(data.gps_qual) == 4:
					self.queueAppend(name, (northing, easting, data.antenna_altitude))
					goodNmea = line
				line_str = name + ":" + str(line)
			else:
				line_str = "Bad Signal: " + line  
			print line_str
		else:
			if len(line) == 0:
				timeout[int(name)] += 1
				if(timeout[int(name)] >= 10):
					print "Receiver %s disconnected"%(name)
					ser[int(name)].close()
					while not ser[int(name)].isOpen():
						try:
							ser[int(name)] = serial.Serial(active[int(name)])
							print "Re-established connection to receiver %s"%(name)
						except serial.SerialException:
							print "failed to re-establish connection to receiver %s"%(name)
			else:
				print "Received something other than GGA message from receiver: " + line
		log.writelines(str(line))
		
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
		#logging.debug('original Degree minutes: %s \t Converted Degree decimal degree: %s'%(coor,str(degrees + "." + minutes)))
		return degrees + minutes
	
	# Signal handler function, closes log, and closes serial connections
	# Called from: thread
	def signalHandler(self, signal, frame):
		global ser, log
		if log != 0:
			log.close()
			logging.info('Closed log file')
		for n in range(0, len(ser)):
			ser[n].close()
			logging.info('Closing serial port: %s'%(ser[n]))
		print "in signal handler"
		if __name__ == "__main__":
			sys.exit(0)
	
		# Scan for available ports. Return a list of tuples (num, name)
	# Called from: portSearch
	def scan(self, ports, loc = ['']*256):
		global active
		available = []
		for i,loc in zip(ports,loc):
			try:
				s = serial.Serial(i)
				if s.name in active:
					break
				else:
					available.append((s.name,loc))
					s.close()   # explicit close 'cause of delayed GC in java
			except serial.SerialException:
				pass
		return available
	
	def portsFound(self, available):
		print "Found Devices:"
		for s, loc in available:
			print "%s" % s
			logging.info('Found ports: %s'%(s))
		print "Choose a COM port #. Enter # only, then enter"
		temp = raw_input()
		if temp == 'q' or not temp.isdigit():
			print "Invalid Port, exiting!!!"
			logging.info('Bad input port, exiting program')
			if __name__ == "__main__":
				sys.exit(0)
		return 'COM' + temp #concatenate COM and the port number to define serial port
	
	# Searches for devices or ports available and returns COM number
	# Called from: initSerial
	def portSearch(self, threadNum, input):
		global active
		if input == 'e':
			available = []
			location = []
			tree = ET.parse(xmlFilePath)
			RSearch = tree.iter('receiver')
			for r in RSearch:
				if (list(r)[0].text).upper() == 'T' and (('COM'+list(r)[5].text) not in active):
					if (list(r)[1].text).upper() == 'T':
						available.append((int(list(r)[5].text)-1))
						location.append('L')
					elif (list(r)[2].text).upper() == 'T':
						available.append((int(list(r)[5].text)-1))
						location.append('R')
					elif (list(r)[3].text).upper() == 'T':
						available.append((int(list(r)[5].text)-1))
						location.append('C')
					else:
						available.append((int(list(r)[5].text)-1))
			available = self.scan(available,location)
			if multiQueueFlag == True:
				for s, loc in available:
					if int(threadNum) == 0 and loc == 'L':
						logging.info('Using %s for left receiver'%(s))
						return s
					if int(threadNum) == 1 and loc == 'C':
						logging.info('Using %s for center receiver'%(s))
						return s
					if int(threadNum) == 2 and loc == 'R':
						logging.info('Using %s for right receiver'%(s))
						return s
			if len(available) != 0:
				return self.portsFound(available)
			else:
				print "No active devices found. Switching to scan mode"
				logging.info('No active devices selected, switching to scan mode')
				self.portSearch(threadNum,'s')  
		elif input == 's':
			available = self.scan(range(256))
			if len(available) != 0:   
				return self.portsFound(available)
			else:
				print "No ports found, exiting!!!"
				self.proc_stop = True
				if __name__ == "__main__":
					sys.exit(0)
				return
		else:
			logging.info('Invalid User input for port search')
			print "Invalid input, exiting!!!"
			self.proc_stop = True
			if __name__ == "__main__":
				sys.exit(0)
	
	
def outputToCSV():
    pass

if __name__ == "__main__":
    connectOutput(None,None).thread()