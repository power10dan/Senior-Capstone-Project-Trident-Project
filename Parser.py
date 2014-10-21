#
#	Python GPS Tracking Example
#	SparkFun Electronics, A.Weiss
#	Beerware: if you use this and meet me, you must buy me a beer
#	
#	Function:
#	Takes GPS position and altitude data and plots it on a scaled map image of your
#	choice. Altitude can also be displayed in a separate graph. 
#	
#	The program has a console menu that allows you to configure your connection. 
#	The program will run with either a GPS moudle connected or no moudle connected.
#	If a GPS is connected, the position and altitude data is automatically saved
#	to a file called nmea.txt. If no GPS is connected, you must create your own
#	nmea.txt and fill it with GPGGA NMEA sentences. 
#	A map needs to be created and saved as a file called map.png. When you create
#	your map, note the lat and long of the bottom left and top right corner, in decimal 
#	degrees. Then enter this information into the global variables below. This way, 
#	your the border of your map image can be used as the graph mins and maxs.
#	Once you have a map loaded and a GPS connected, you can run the program and select
#	either your position to be displayed on your map, or display altitude on a separate
#	graph. The maps are not updated in realtime, so you must close the map and run 
#	the map command again in order to read new data. 

from pynmea import nmea
import serial, time, sys, datetime, shutil

######Global Variables#####################################################
# you must declare the variables as 'global' in the fxn before using#
i = 0 #x units for altitude measurment
BAUDRATE = 4800

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
	ser.timeout = 1
	ser.open()
	ser.isOpen()
	
	print 'OPEN: '+ ser.name
	print ''
	
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
  available = scan()
  
  ser.close()
#sys.exit()
