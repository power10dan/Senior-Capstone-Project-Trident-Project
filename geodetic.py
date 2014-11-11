import math, time
import xml.etree.ElementTree as ET

a = 6378137
f = 1/298.257222101
e = math.sqrt((2*f)-(f**2))

class geodetic:
	def geo(self, lat,long):
		global a,f,e
	
		tree = ET.parse('ui.xml')
		root = tree.getroot()
		zone = tree.find("ui/zone").text
		if zone == '3601':
			lambdacm = 120.5
			LatO = 43.0+(40.0/60.0)
			LatS = 44.0+20.0/60.0
			LatN = 46.0
			Eo = 2500000 #meters
			Nb = 0
		if zone == '3602':
			lambdacm = 120.5
			LatO = 41.0+40.0/60.0
			LatS = 42.0+20.0/60.0
			LatN = 44.0
			Eo = 1500000 #meters
			Nb = 0
		
		lat = math.radians(lat)
		long = math.radians(long)
		LatO = math.radians(LatO)	
		LatS = math.radians(LatS)
		LatN = math.radians(LatN)	

		W = math.sqrt(1-(e**2)*((math.sin(lat))**2))
		M = math.cos(lat)/W
		T = math.sqrt(((1-math.sin(lat))/(1+math.sin(lat)))*(((1+e*math.sin(lat))/(1-e*math.sin(lat)))**e))
		
		
		w1 = math.sqrt(1-(e**2)*((math.sin(LatS))**2))
		w2 = math.sqrt(1-(e**2)*((math.sin(LatN))**2))

		m1 = math.cos(LatS)/w1
		m2 = math.cos(LatN)/w2
		t0 = math.sqrt(((1-math.sin(LatO))/(1+math.sin(LatO)))*((1+e*math.sin(LatO))/(1-e*math.sin(LatO)))**e)
		t1 = math.sqrt(((1-math.sin(LatS))/(1+math.sin(LatS)))*(((1+e*math.sin(LatS)))/(1-e*math.sin(LatS)))**e)
		t2 = math.sqrt(((1-math.sin(LatN))/(1+math.sin(LatN)))*(((1+e*math.sin(LatN)))/(1-e*math.sin(LatN)))**e)
		
		n = (math.log(m1)-math.log(m2))/((math.log(t1)-math.log(t2)))
		F = m1/(n*t1**n)
		Rb = a*F*t0**n

		gamma = (lambdacm-math.degrees(long))*n #convergency angle in decimal degrees
	
		R = a*F*T**n
		
		k = (R*n)/(a*M) #grid_factor
		gamma = math.radians(gamma)
		easting = (R*math.sin(gamma))+Eo
		northing = Rb-(R*math.cos(gamma))+Nb
		
		return(northing,easting,k,gamma)
	
		