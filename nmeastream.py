import pynmea.streamer
import pynmea.nmea

with open('.\output\output_2014-11-13.txt', 'r') as data_file:
    streamer = pynmea.streamer.NMEAStream(data_file)
    next_data = streamer.get_strings()
    data = []
    while next_data:
        data += next_data
        next_data = streamer.get_strings()

talker = []
talkerData = []        
for i in data:
    if i[:2] not in talker:
        talker.append(i[:2])
        talkerData.append([])
    else: 
        talkerData[(talker.index(i[:2])-1)].append(i)
        
d = pynmea.nmea.GPGGA()
#d.parse(data[105])

#print d.ref_station_id

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