#tinker2.py

class CoordError(Exception):
	pass
	
class NoResultError(CoordError):
	pass
class QueryLimitError(CoordError):
	pass

err = "this is an error msg"

try:
	raise NoResultError(err)
except QueryLimitError:
	print "not"
except CoordError as e:
	print type(e) == NoResultError

from math import *
D2R = pi / 180
lat1 = 55.75 
lon1 = 37.6167
lat2 = 38.895
lon2 = -77.0367
lat1R = D2R * lat1
lat2R = D2R * lat2
lon1R = D2R * lon1
lon2R = D2R * lon2

d = 2*asin(sqrt((sin((lat1R-lat2R)/2))**2 + cos(lat1R)*cos(lat2R)*(sin((lon1R-lon2R)*.5))**2))
d2 = sin(lat1R)*sin(lat2R) + cos(lat1R)*cos(lat2R)*cos(abs(lon1R-lon2R))
#print "d: %f"%d
#print "d2: %f"%d2

