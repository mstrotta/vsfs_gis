'''
geo_utils.py
20 November 2013
Mike Trotta

utilities for vsfs_geo_util
'''
import urllib
import json
import os
import atexit
from math import sin,cos,pi,sqrt,asin,atan2


class CoordManager:
	'''Manages coordinate lookup for geographic locations. Stores known location to minimize
	 number of internet queries.  File stored in form: "city, state/country:(lat,lon)\n.
	*ALWAYS USE INSIDE WITH CLAUSE
	'''
	def __init__(self):
		self._fileName = 'coordBase.txt'
		self._locations = _Tree()
		self._queries = 0
		
		fileExists = os.path.isfile(self._fileName)
		if fileExists: # extract data
			f = open(self._fileName, 'r')
			lines = f.readlines()
			f.close()
			for line in lines:
				location,x = line.split(':')
				x = x.strip().strip("()").split(",")
				coord = (float(x[0]),float(x[1]))
				self._locations.add(location, coord)
		#atexit.register(self._close)
	
	def __enter__(self):
		return self
	
	def __exit__(self, type, value, traceback):
		print "%d queries made" %self._queries
		lines = []
		for loc,coord in self._locations:
			lines.append( loc.capitalize() + ":" + str(coord) + "\n" )
		f = open(self._fileName, 'w')
		f.writelines(lines)
		f.close()
		
	def getCoord(self, location):
		location = location.lower()
		if location in self._locations:
			return self._locations[location]
		coord = self._lookup(location)
		self._locations.add(location,coord)
		return coord
		
	def _lookup(self, location):
		'''returns ((lat,lon), errorMsg) or (None, errorMsg) on error'''
		coords = None
		errorMsg = ""
		URL_BASE = 'http://maps.googleapis.com/maps/api/geocode/json?address='
		URL_AFFIX= '&sensor=false'
		
		url = URL_BASE + location + URL_AFFIX 
		url = url.replace(' ','+')
		j = json.load(urllib.urlopen(url)) # google api json object from query
		if not j['status'] == 'OK':
			try: raise {"ZERO_RESULTS":NoResultError,"OVER_QUERY_LIMIT":QueryLimitError}[j['status']]
			except KeyError: raise CoordError(j['status'])
		lat = float(j["results"][0]["geometry"]["location"]["lat"])
		lon = float(j["results"][0]["geometry"]["location"]["lng"])	
		coords = (lat,lon)
		self._queries += 1
		return coords	

class CoordError(Exception):
	pass
class NoResultError(CoordError):
	def __init__(self, msg=""):
		self.msg = msg
	def __str__(self):
		return rep(self.msg)	
class QueryLimitError(CoordError):
	def __str__(self):
		return "Try again later"
	
class GeoWriter:
	'''
	Stores and manages creation of a geoJSON file
	PARAMTERS:
	  fileName
	  objName - name of js object to be created
	'''
	def __init__(self, fileName, objName):
		self._fileName = fileName
		self._curLine = ""
		self._numLines = 0
		self._lines = []
		self._curTab = 0
		
		self._lines.append( "var %s = [" %objName )
		self._numLines += 1
	
	def endFile(self):
		'''writes file'''
		if self._curLine != '':
			self._endLine()
		prevLine = self._lines[ self._numLines - 1 ]
		self._lines[ self._numLines - 1 ] = prevLine.replace('},','}];')

		f = open( self._fileName, 'w' )
		f.writelines( self._lines )
		f.close()

	def beginFeatureCol(self):
		self.beginObj()
		self.addLine('"type": "FeatureCollection",')
		self.addLine('"features": [')
	
	def endFeatureCol(self):
		'''assumes at least one feature'''
		# remove comma on previous line
		prevLine = self._lines[ self._numLines - 1 ]
		self._lines[ self._numLines - 1 ] = prevLine.replace('},','}]')
		self.endObj(includeComma=True)
		
	def _endLine(self):
		self._curLine += "\n"
		self._lines.append( self._curLine )
		self._curLine = ""
		self._numLines += 1

	def _beginLine(self):
		self._curLine = "  " * self._curTab
		
	def beginObj(self):
		'''Includes an indentation suite'''
		self.addLine("{")
		self._curTab += 1
	
	def endObj(self, includeComma=False):
		'''Assumes an indentation suite'''
		if self._curTab > 0:
			self._curTab -= 1
		if includeComma :
			self.addLine("},")
		else:
			self.addLine("}")
		
	def addLine(self, content):
		self._beginLine()
		self._curLine += str(content)
		self._endLine()
	
	def addToCurLine(self, content):
		self._curLine += str(content)

	def beginFeature(self):
		self.beginObj()
		self.addLine('"type": "Feature",')
		
	def endFeature(self):
		self.endObj(includeComma=True)
		
	def beginProperties(self):
		self.addLine('"properties":')
		self.beginObj()
		
	def endProperties(self):
		# remove comma on previous line
		prevLine = self._lines[ self._numLines - 1 ]
		self._lines[ self._numLines - 1 ] = prevLine.replace(',\n','\n')
		self.endObj(includeComma=True)
	
	def beginGeometry(self, aType, coords):
		''' takes geometry type as a string and coords as a list of coordinate pairs'''	
		if type(coords) is not list: # if we get single pair, put it into list
			coords = [coords]
			
		self.addLine('"geometry":')
		self.beginObj()
		self.addLine('"type": "%s",' %aType)
		line = "\"coordinates\": ["
		if len(coords) == 1:
			line += "%f,%f]" %(coords[0][1],coords[0][0])
		else:
			for i in range(len(coords)):
				pair = coords[i]
				line += "[%f,%f]" %(pair[1],pair[0])
				if i == len(coords) - 1:
					line += "]"
				else:
					line += ", "
		self.addLine(line)

	def endGeometry(self):
		self.endObj()
		
class _Tree:
	'''a binary _Tree assuming no duplicates built to take a value for sorting and a related \
	peice of data (in our case a (location,coord) tuple)'''
	def __init__(self):
		self._root = None
		self._size = 0
		self._list = []
		self._iterNdx = -1
		
	def add(self, val, data=None):
		if type(val) == str:
			val = val.lower()
		cur = self._root
		new = _Node(val, data)
		self._size += 1
		
		if self._root is None:
			self._root = new
			return
		while 1:
			if val < cur.val:
				if cur.left:
					cur = cur.left
				else:
					cur.left = new
					break
			elif val > cur.val:
				if cur.right:
					cur = cur.right
				else:
					cur.right = new
					break
			else:
				return	
	def __getitem__(self, key):
		if type(key) == str:
			key = key.lower()
		data = self._search(key)[1]
		if data:
			return data
		else: 
			raise KeyError(str(data))
		
	def __contains__(self, query):
		if type(query) == str:
			query = query.lower()
		return self._search(query)[0]
	
	def __iter__(self):
		if self._size != self._list:
			self._traverse()
			self._iterNdx = -1
		return self
	
	def next(self):
		if self._iterNdx + 1 < len(self._list):
			self._iterNdx += 1
			return self._list[self._iterNdx]
			
		else:	
			raise StopIteration
			
	def _search(self, query):
		if type(query) == str:
			query = query.lower()
		cur = self._root
		while cur is not None:
			if query < cur.val:
				cur = cur.left
			elif query > cur.val:
				cur = cur.right
			else:
				return (True,cur.data)
		return (False,None)
	
	def _traverse(self): #breadth-first
		queue = []
		self._list = []
		queue.append( self._root )
		while len(queue) > 0:
			x = queue.pop(0)
			self._list.append( (x.val,x.data) )
			if x.left:
				queue.append(x.left)
			if x.right:
				queue.append(x.right)
		
class _Node:
	def __init__(self, val, data):
		self.val = val
		self.data = data
		self.left = None
		self.right = None


def getDescRowNdx( descRows, tagColumn, tag ):
	'''Returns index corresponding to given tag'''
	if type(tag) is str:
		for i in range(len(descRows)):
			if descRows[i][tagColumn] == tag:
				return i
	else:
		guessNdx = tag
		guessVal = descRows[ guessNdx ][ tagColumn ]
		while guessVal != tag:
			if curTag > tag:
				guessNdx -= 1
			else:
				guessNdx += 1
			if guessVal < 0 or guessVal >= descRows.length:
				return -1
			guessVal = descRows[ guessNdx ][ tagColumn ]
		return guessNdx
	return -1

	
def almostEquals( a, b, tol = .01 ):
	# tolerance for use with coords only
	return abs(a-b) < tol
def lineToGreatCircle( startPnt, endPnt, numSegments=10 ):
	'''takes two end points and returns a list of points following the great circle'''
	R2D = 180 / pi
	D2R = pi / 180
	r_earth = 6367 # km
	greatCircPnts = []
	
	# return straight line if near
	if almostEquals( startPnt[0], endPnt[0] ) and almostEquals( startPnt[1], endPnt[1] ):
		return [ (startPnt[1],startPnt[0]), (endPnt[1],endPnt[0]) ]
	
	# coordinates in radians
	lat1R = startPnt[0] * D2R
	lon1R = startPnt[1] * D2R
	lat2R = endPnt[0] * D2R
	lon2R = endPnt[1] * D2R
	
	d=2*asin(sqrt((sin((lat1R-lat2R)/2))**2 + cos(lat1R)*cos(lat2R)*(sin((lon1R-lon2R)*.5))**2))
	#d = sin(lat1)*sin(lat2) + cos(lat1)*cos(lat2)*cos(abs(lon1-lon2))
	for i in range(numSegments + 1):
		sinD = sin(d)
		if sinD == 0: # no need for great circle
			pass # handle? (we think handled above)
		f = float(i)/numSegments
		A = sin((1-f)*d)/sinD
		B = sin(f*d)/sinD
		x = A*cos(lat1R)*cos(lon1R) + B*cos(lat2R)*cos(lon2R)
		y = A*cos(lat1R)*sin(lon1R) + B*cos(lat2R)*sin(lon2R)
		z = A*sin(lat1R) + B*sin(lat2R)
		latR = atan2(z,sqrt(x*x+y*y))
		lonR = atan2(y,x)
		lat = R2D * latR
		lon = R2D * lonR
		greatCircPnts.append( (lon,lat) )
	return greatCircPnts