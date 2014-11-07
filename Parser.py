from pynmea import nmea
import serial, time, sys, datetime, shutil, threading, signal
#import utm
from threading import Lock

######Global Variables#####################################################
# you must declare the variables as 'global' in the fxn before using#
ser= []
BAUDRATE = 115200
active = []
mutex = Lock()
log = 0 
######FUNCTIONS############################################################ 
class connect_output:
	def init_serial(self, i):
		#opens the serial port based on the COM number you choose
		print "Found Ports:"
		for n,s in self.scan():
			print "%s" % s
		print " "
		#enter your COM port number
		print "Choose a COM port #. Enter # only, then enter"
		temp = raw_input() #waits here for keyboard input
		if temp != 'e' and not temp.isdigit():
			print "Invalid Port, exiting!!!"
			sys.exit(0)
		comnum = 'COM' + temp #concatenate COM and the port number to define serial port
		# configure the serial connections 
		global ser, BAUDRATE
		
		p = serial.Serial()
		p.port = comnum
		p.baudrate = BAUDRATE
		p.bytesize = 8
		p.stopbits = 1
		
		global active
		active.append(comnum)
		ser.append(p)
		
		p.open()
		p.isOpen()
		print 'OPEN: '+ ser[i].name

	def signal_handler(self, signal, frame):
		global ser, log
		if log != 0:
			log.close()
		for	n in range(0,len(ser)):
			ser[n].close()
		sys.exit(0)


	def thread(self):
		global log
		signal.signal(signal.SIGINT, self.signal_handler)
		
		print "How many receivers are you connecting?"
		r = raw_input()
		if not r.isdigit():
			print "Invalid number of receivers, exiting!!!"
			sys.exit(0)
		r = int(r)
		for i in range(0,r):
			thread = threading.Thread(target=self.init_serial(i))
			thread.daemon = True
			thread.start()
		   
		log = open('output_'+ str(datetime.date.today())+'.txt','a')
		print log.name
		while 1:
			for i in range(0,r): 
				thread = threading.Thread(target=self.stream_serial(str(i))).run()
			time.sleep(1)

	def scan(self):
		#scan for available ports. return a list of tuples (num, name)
		available=[]
		for i in range(256):
			try:
				s = serial.Serial(i)
				if s.name in active:
					break
				else:
					available.append( (i, s.name))
					s.close()   # explicit close 'cause of delayed GC in java
			except serial.SerialException:
				pass
		return available  

	def stream_serial(self, name):
		#stream data directly from the serial port
		global log 
		line = ser[int(name)].readline()
		if line[3:6] == 'GGA':
			data = nmea.GPGGA()
			data.parse(line)
			if len(line) > 50:
				print name + " latitude: " + self.degrees(data.latitude)
				print name + " longitude: " + self.degrees(data.longitude)
				#print utm.from_latlon((float(data.latitude)/100), (float(data.longitude)/100))
		line_str = name + ":" + str(line)
		print line_str
		log.writelines(line_str)

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
