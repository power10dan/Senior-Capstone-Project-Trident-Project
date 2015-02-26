import pynmea.streamer
import pynmea.nmea
import datetime
import geodetic
import MultipathDetector

M = MultipathDetector.MultipathDetector()
G = geodetic.geodetic()

def degrees(coor):
    if len(coor.split('.')[0])%2 == 0:
        degrees = float(coor[:2])
        minutes = float(coor[2:])/60
    else:
        degrees = float(coor[:3])
        minutes = float(coor[3:])/60
    return degrees + minutes
    
with open('.\output\output_2015-02-05.txt', 'r') as data_file:
    streamer = pynmea.streamer.NMEAStream(data_file)
    next_data = streamer.get_strings()
    data = []
    while next_data:
        data += next_data
        next_data = streamer.get_strings()

talker = []             #queue of receivers
talkerData = []         #list of receiver data
cartesianQueue = []     #Queue of converted cartesian
#length = []
      
for i in data:
    i.partition(':')
    if i[:2] not in talker:
        talker.append(i[:2])
        talkerData.append([])
        cartesianQueue.append([])
        talkerData[(talker.index(i[:2]))].append(i)
    else: 
        talkerData[(talker.index(i[:2]))].append(i)
print talker
cart = open('.\output\cart_'+ str(datetime.date.today())+'.txt','w')
d = pynmea.nmea.GPGGA()

for i in range(len(talker)):
    cart.writelines(str(i) + "\n")
    # length.append(len(talkerData[i]))
    for j in range(len(talkerData[i])):
        if len(talkerData[i][j]) > 40:
            d.parse(talkerData[i][j])       
            if int(d.gps_qual) == 4:
                lat = degrees(d.latitude)
                long = degrees(d.longitude)
                cartesian = G.geo(lat,long)
                northing, easting, k ,gamma = cartesian
                cartesianQueue[i].append((d.timestamp,northing,easting,float(d.antenna_altitude)))
                cart.writelines("\t%s\t%s\t%s\t%s\t%s\n"%(d.timestamp,northing,easting,d.gps_qual,d.antenna_altitude))           
cart.close()

common = open('.\output\common_'+ str(datetime.date.today())+'.txt','w')
commonQueue = []
commonQueue.append([i for i in cartesianQueue[0] if i[0] in [j[0] for j in cartesianQueue[1]] and i[0] in [k[0] for k in cartesianQueue[2]]])
commonQueue.append([j for j in cartesianQueue[1] if j[0] in [i[0] for i in cartesianQueue[0]] and j[0] in [k[0] for k in cartesianQueue[2]]])
commonQueue.append([k for k in cartesianQueue[2] if k[0] in [i[0] for i in cartesianQueue[0]] and k[0] in [j[0] for j in cartesianQueue[1]]])

for i in range(len(commonQueue)):
    common.writelines("%i\n"%(i))
    for com in commonQueue[i]:
        common.write("\t%s\t%s\t%s\t%s\n"%(com[0],com[1],com[2],com[3]))
common.close()

print len(commonQueue[0])
print len(commonQueue[1])
print len(commonQueue[2])

for i in range(len(commonQueue[0])):
    Queue = [[],[],[]]
    for j in range(len(talker)):
        for k in range(i,i+10):
            Queue[j].append(commonQueue[j][k][1:])
    if len(Queue[0]) == 10 and len(Queue[1]) == 10 and len(Queue[2]) == 10:
        mult = M.multipathQueueHandler(Queue)
        print mult
        if not mult:
            print Queue
        
    
# parse_map = (
            # ('Timestamp', 'timestamp'),
            # ('Latitude', 'latitude'),
            # ('Latitude Direction', 'lat_direction'),
            # ('Longitude', 'longitude'),
            # ('Longitude Direction', 'lon_direction'),
            # ('GPS Quality Indicator', 'gps_qual'),
            # ('Number of Satellites in use', 'num_sats'),
            # ('Horizontal Dilution of Precision', 'horizontal_dil'),
            # ('Antenna Alt above sea level (mean)', 'antenna_altitude'),
            # ('Units of altitude (meters)', 'altitude_units'),
            # ('Geoidal Separation', 'geo_sep'),
            # ('Units of Geoidal Separation (meters)', 'geo_sep_units'),
            # ('Age of Differential GPS Data (secs)', 'age_gps_data'),
            # ('Differential Reference Station ID', 'ref_station_id'))
