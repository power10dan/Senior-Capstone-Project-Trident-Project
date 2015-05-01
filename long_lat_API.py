import geodetic
import sys

def oregon_planar(lat, longitude):
    lat = 0
    lon = 0
    #check user input
    try:
        lat = float(lat)
        lon = float(longitude)
    except ValueError:
        print('Your input(s) is / are not integers or floats. Please reinput')
        exit()
    n,e,k,g = geodetic.geodetic.geo(lat,lon)
    print 'Northing: %f  Easting: %f  K: %f Gamma: %f' % (n,e,k,g)

if __name__ == '__main__':
    lat = sys.argv[0]
    lon = sys.argv[1]
    oregon_planar(lat, lon)

