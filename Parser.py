from pynmea import nmea
import serial, time, sys, datetime, shutil, threading
from threading import Lock

######Global Variables#####################################################
# you must declare the variables as 'global' in the fxn before using#
ser = 0
BAUDRATE = 115200
thread_Primary = 0
thread_Left = 0
thread_Right = 0
active = []
mutex = Lock()

######FUNCTIONS############################################################ 
def check_serial():
	print 'Do you have a GPS connected to the serial port? hit y or n, then enter'
	temp = raw_input()
	if temp == 'y':
		init_serial()
	if temp == 'n':
		sys.exit()
	print 'You can enter your own NMEA sentences into a file named nmea.txt'

	
def init_serial():
	global thread_Primary, thread_Left,thread_Right
	#opens the serial port based on the COM number you choose
	print "Found Ports:"
	for n,s in scan():
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
	ser = serial.Serial()
	ser.baudrate = BAUDRATE
	ser.port = comnum
	ser.stopbits = 1
	ser.bytesize = 8
	global active
	active.append(comnum)
	ser.open()
	ser.isOpen()
	print 'OPEN: '+ ser.name
	#while 1:
	    #stream_serial()
	
def position():
    pass

def thread():
    global thread_Primary, thread_Left,thread_Right
    thread_Primary = threading.Thread(target=init_serial(),name="primary")
    #thread_Left = threading.Thread(target=init_serial(),name="left")
    #thread_Right = threading.Thread(target=init_serial(),name="right")
    thread_Primary.daemon = True
    thread_Primary.start()
    #thread_Left.daemon = True
    #thread_Left.start()
    #thread_Right.daemon = True
    #thread_Right.start()
    
    while 1:
	thread_Primary = threading.Thread(target=stream_serial("primary"))
	thread_Primary.run()
	#thread_Left = threading.Thread(target=stream_serial("left"))
	#thread_Left.run()
	#thread_Right = threading.Thread(target=stream_serial("right"))
	#thread_Right.run()
    #ser.close()	
    sys.exit()


def save_raw():
	#this fxn creates a txt file and saves only GPGGA sentences
	while 1:
		line = ser.readline()
		line_str = str(line)
		if(line_str[4] == 'G'): # $GPGGA
			if(len(line_str) > 50): 
				# open txt file and log data
				f = open('nmea.txt', 'a')
				try:
					f.write('{0:}'.format(line_str))
				finally:
					f.close()
			else:
				stream_serial()

def scan():
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

def stream_serial(name):
    #stream data directly from the serial port
    line = ser.readline()
    line_str = str(line)    
    print name + ":" +line_str

########START#####################################################################################
thread()
#main program loop
#while 1:
  # pass
 # ser.close()