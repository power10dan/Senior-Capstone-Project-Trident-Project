from pynmea import nmea
import serial, time, sys, datetime, shutil, threading, signal
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
		if temp == 'e':
			sys.exit()
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
		log.close()
		for	n in range(0,len(ser)):
			ser[n].close()
		sys.exit(0)


	def thread(self):
		global log
		print "How many receivers are you connecting?"
		r = int(raw_input())
		for i in range(0,r):
			thread = threading.Thread(target=self.init_serial(i))
			thread.daemon = True
			thread.start()
		   
		signal.signal(signal.SIGINT, self.signal_handler)
		log = open('output_'+ str(datetime.date.today())+'.txt','a')
		print log.name
		while 1:
			for i in range(0,r): 
				thread = threading.Thread(target=self.stream_serial(str(i))).run()

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
		line_str = name + ":" + str(ser[int(name)].readline())
		print line_str
		log.writelines(line_str)

########START#####################################################################################
run = connect_output()
run.thread()
