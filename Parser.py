from pynmea import nmea
import serial, time, sys, datetime, shutil

######Global Variables#####################################################
# you must declare the variables as 'global' in the fxn before using#
ser = 0
BAUDRATE = 115200

######FUNCTIONS############################################################ 
def check_serial():
	print 'Do you have a GPS connected to the serial port? hit y or n, then enter'
	temp = raw_input()
	if temp == 'y':
		init_serial()
	if temp == 'n':
		print 'You can enter your own NMEA sentences into a file named nmea.txt'
	
def init_serial():
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
	ser.timeout = none
	ser.open()
	ser.isOpen()
	
	print 'OPEN: '+ ser.name
	print ''
	
	while 1:
		stream_serial()
	ser.close()	
	sys.exit()
	
	
def position():
  pass

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
    available = []
    for i in range(256):
        try:
            s = serial.Serial(i)
            available.append( (i, s.name))
            s.close()   # explicit close 'cause of delayed GC in java
        except serial.SerialException:
            pass
    return available  

def stream_serial():
    #stream data directly from the serial port
    line = ser.readline()
    line_str = str(line)    
    print line_str

########START#####################################################################################
check_serial()

#main program loop
while 1:
  # pass
  ser.close()
#sys.exit()
