import math, time
import xml.etree.ElementTree as ET

a = 6378137
f = (1/298.257222101)
q = math.sqrt((2*f)-(f**2))

class geodetic:
	def geo(self,lat,long):
		global a,f,q

		lat = math.radians(lat)
		long = math.radians(long)
	
		tree = ET.parse('ui.xml')
		root = tree.getroot()
		zone = tree.find("ui/zone").text
		if zone == '3601':
			lambdacm = -120.5
			LatO = 43+(40/60)
			LatS = 44+(20/60)
			LatN = 46
			Eo = 2500000 #meters
			Nb = 0
		if zone == '3602':
			lambdacm = -120.5
			LatO = 41+(40/60)
			LatS = 42+(20/60)
			LatN = 44
			Eo = 1500000 #meters
			Nb = 0

		W = math.sqrt(1-(q**2)*((math.sin(lat))**2))
		print W
		M = math.degrees(math.cos(lat))/W
		print M
		T = math.sqrt(((1-math.degrees(math.sin(lat)))/(1+math.degrees(math.sin(lat))))*(((1+q*math.degrees(math.sin(lat)))/(1-q*math.degrees(math.sin(lat))))**q))

		w1 = math.sqrt(1-(q**2)*((math.degrees(math.sin(LatS)))**2))
		w2 = math.sqrt(1-(q**2)*((math.degrees(math.sin(LatN)))**2))

		m1 = math.degrees(math.cos(LatS))/w1
		m2 = math.degrees(math.cos(LatN))/w2
		t0 = math.sqrt(((1-math.degrees(math.sin(LatO)))/(1+math.degrees(math.sin(LatO))))*(((1+q*math.degrees(math.sin(LatO)))/(1-q*math.degrees(math.sin(LatO))))**q))
		t1 = math.sqrt(((1-math.degrees(math.sin(LatS)))/(1+math.degrees(math.sin(LatS))))*(((1+q*math.degrees(math.sin(LatS)))/(1-q*math.degrees(math.sin(LatS))))**q))
		t2 = math.sqrt(((1-math.degrees(math.sin(LatN)))/(1+math.degrees(math.sin(LatN))))*(((1+q*math.degrees(math.sin(LatN)))/(1-q*math.degrees(math.sin(LatN))))**q))

		n = (math.log(m1)-math.log(m2))/((math.log(t1)-math.log(t2)))
		F = m1/n*t1**n
		Rb = a*F*(t0**n)

		gamma = (lambdacm-long)*n #convergency angle in decimal degrees

		R = a*F*(T**n)

		k = (R*n)/(a*M) #grid_factor

		easting = (R*math.sin(gamma).degrees)+Eo
		northing = Rb-(R*math.cos(gamma).degrees)+Nb
		
		return (northing,easting,k,gamma)
		
Y = geodetic()
Y.geo(44.5,(-123))		
		