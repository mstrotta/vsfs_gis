'''
vsfs_geo_util.py
18 November 2013
Mike Trotta

Reads two spreadsheets containing project and student data and outputs a geoJSON
 for use in the leaflet map.
'''

from geo_utils import *
from time import sleep
import csv
import atexit

# -- dbg -- #
from time import time
dbg_startTime = time()
dbg_prevTime = time()
dbg_logLines = ["%20s\t%s\t\t%s\n" %("SECTION","TIME","TOTAL")]
def dbg_log(section):
	t = time()
	global dbg_prevTime
	toWrite = "%20s:\t%f ms\t%f ms\n"%(section,1000*(t-dbg_prevTime),1000*(t-dbg_startTime))
	#print toWrite.strip()
	dbg_logLines.append(toWrite)
	dbg_prevTime = t
def dbg_log2_start(section):
	t = time()
	
def dbg_saveLog(dbg_logLines):
	dbg_log("final")
	f = open('logTime.txt','w')
	f.writelines(dbg_logLines)
	f.close()
	print "log written"
atexit.register(dbg_saveLog,dbg_logLines)
# --------- #

# ---------------------------------------------------------------------------------
# settings
STUDENT_FILE = 'student_data.csv'
PROJECT_FILE = 'project_data.csv'
GEOJSON_FILE = 'vsfs_data.geojson'
DESCRIP_FILE = 'vsfs_project_descriptions.csv'
GEO_VAR_NAME = 'geo_data' # js variable name for geoJSON object (var [name] = ...)


# ---------------------------------------------------------------------------------
# CSV INDICES
# STUDENT
STUD_PROJECT_ID = 7
STUD_PROJECT_TAG = 6
STUD_LAST_NAME = 0
STUD_FIRST_NAME = 1
STUD_CITY = 3
STUD_STATE = 4
STUD_COUNTRY = 5
STUD_UNDERGRAD = 10
STUD_MAJOR1 = 11
STUD_MAJOR2 = 12
STUD_GRAD = 16

# PROJECT
PROJ_PROJECT_ID = 0
PROJ_PROJECT_TAG = 1
PROJ_PROJECT_NAME = 2
PROJ_COUNTRY = 3
PROJ_OFFICE = 4
PROJ_POST = 5
PROJ_SECTION = 6

# DESCRIPTION
DESC_PROJECT_TAG = 0
DESC_AGENCY = 1
DESC_POST = 2
DESC_COUNTRY = 3
DESC_PROJECT_NAME = 4
DESC_SUMMARY = 5

dbg_log("preliminaries")
# ---------------------------------------------------------------------------------
# Read files / extract entries
# ASSUMPTIONS
#  + description file sorted by tag increasing
#  + student file sorted by metastorm ID increasing
#  + project file sorted by metastorm ID increasing
studentRows = []
projectRows = []
descripRows = []
with open(DESCRIP_FILE, 'rb') as f:
	reader = csv.reader(f, dialect='excel')
	for row in reader:
		descripRows.append(row)
with open(STUDENT_FILE, 'rb') as f:
	reader = csv.reader(f, dialect='excel')
	for row in reader:
		studentRows.append(row)
with open(PROJECT_FILE, 'rb') as f:
	reader = csv.reader(f, dialect='excel')
	for row in reader:
		projectRows.append(row)
dbg_log("file reading")


# ---------------------------------------------------------------------------------
# Data reformatting
# CSV data will be extracted and stored in the form:
#
#  projLocationData: [location A, location B,...] - an alphabetized list of strings
#  projectData: [{name:"",location:"",...}, {...}*, ...] - lists contain dictionaries of projectdata
#  studentData: [[{},{...},...], [...]*, ...]  - a list of lists; sublists contain dictionaries of student data
#
# *indexes match, so studentData[4] contains the list of students' data matched with projectData[4] at projLocationData[4]
# *we throw away projects/students with no corresponding student/project

projectData = []      # list of dictionaries containing info
studentData = []      # list of student-lists containing dictionaries containing info
projLocationData = [] # list of strings

i = 1 # student row ndx
for projRow in projectRows[1:]: # skip header
	projTagFromProj = projRow[ PROJ_PROJECT_ID ]
	
	# project data
	projDict = {}
	studList = []
	projTag = projRow[ PROJ_PROJECT_TAG ].capitalize()
	descRowNdx = getDescRowNdx( descripRows, DESC_PROJECT_TAG, projTag )
	projDict['summary'] = descripRows[ descRowNdx ][ DESC_SUMMARY ].replace('"','\\"')
	projDict['name'] = projRow[ PROJ_PROJECT_NAME ].capitalize()
	country = projRow[ PROJ_COUNTRY ]
	if country.upper() == 'UNITED STATES':
		city = 'Washington, D.C.'
		projDict['office'] = projRow[ PROJ_OFFICE ]
	else:
		city = projRow[ PROJ_POST ]
		projDict['post'] = projRow[ PROJ_POST ].capitalize()
		projDict['section'] = projRow[ PROJ_SECTION ].capitalize()
	projLocation = city + ", " + country
	projDict['location'] = projLocation.capitalize()
	

	for studRow in studentRows[i:]:
		i += 1
		projTagFromStud = studRow[ STUD_PROJECT_ID ]
		studDict = {}
		if projTagFromStud > projTagFromProj : # advance project row
			i -= 1 # keep student row where it is
			break
		elif projTagFromStud < projTagFromProj : # advance student row
			continue
		else:
			# student data
			studDict['name'] = studRow[ STUD_FIRST_NAME ].capitalize().replace('"','\\"')
			country = studRow[ STUD_COUNTRY ]
			city = studRow[ STUD_CITY ]
			if country.upper() == 'UNITED STATES':
				state = studRow[ STUD_STATE ]
				studDict['location'] = city + ", " + state
			else:
				studDict['location'] = city + ", " + country
			#TODO: resolve university/hometown unknown
			grad = studRow[ STUD_GRAD ]
			undergrad = studRow[ STUD_UNDERGRAD ]
			major = studRow[ STUD_MAJOR1 ].replace('Other','').strip().strip('0123456789()').strip()
			major2 = studRow[ STUD_MAJOR2 ].replace('Other',"").strip().strip('0123456789()').strip()
			empty = ["NA","NULL",""]
			if grad not in empty:
				studDict['grad'] = grad.strip().strip('0123456789()')
			if undergrad not in empty:
				studDict['undergrad'] = undergrad.strip().strip('0123456789()')
			if major not in empty:
				if major2 not in empty:
					major = major + ", " + major2
				studDict['major'] = major
			studList.append( studDict )
	projLocationData.append( projLocation )
	projectData.append( projDict )
	studentData.append( studList )
	
dbg_log("data reformatting")
# ---------------------------------------------------------------------------------	
# Duplication handle (moved to geo_utils)



projectData, studentData = duplicationMerge(projLocationData,projectData,studentData)

#dbg_log("duplicate handling")
# ---------------------------------------------------------------------------------		
# GeoJSON file creation from our studentData, projectData data storage

gw = GeoWriter( GEOJSON_FILE, GEO_VAR_NAME )
with CoordManager() as cm: # 'with' ensures cm's exit fn called on error
	for i in range(len(projectData)): # each project
		project = projectData[i]
		students = studentData[i]
		try: # coord lookup
			projCoord = cm.getCoord(project["location"])
		except NoResultError:
			continue
		except QueryLimitError:
			sleep(2)
			projCoord = cm.getCoord(project["location"])
		# else...
		gw.beginFeatureCol()
	
		# Add project
		gw.beginFeature()
		gw.beginProperties()
		gw.addLine('"class": "project",')
		for prop in project.keys():
			gw.addLine('"%s": "%s",' %(prop, project[prop]))
		gw.endProperties()
		gw.beginGeometry('Point',projCoord)
		gw.endGeometry()
		gw.endFeature()
		
		# add students
		for student in students:
			#dbg_log("")
			try: #coord lookup
				studCoord = cm.getCoord(student["location"])
			except NoResultError:
				continue # skip student
			except QueryLimitError:
				sleep(2)
				try: studCoord = cm.getCoord(student["location"]) #TODO: REMOVE TRY
				except QueryLimitError:
					pass
			# else
			gw.beginFeature()
			gw.beginProperties()
			gw.addLine('"class": "student",')
			for prop in student.keys():
				
				gw.addLine('"%s": "%s",' %( prop, student[prop]) )
			gw.endProperties()
			gw.beginGeometry('Point',studCoord)
			gw.endGeometry()
			gw.endFeature()
			#dbg_log("plot coord")
			
			# add routes
			circleCoords = lineToGreatCircle( projCoord, studCoord, 20 )
			gw.beginFeature()
			gw.beginProperties()
			gw.addLine('"class": "route"')
			gw.endProperties()
			gw.beginGeometry('MultiLineString',circleCoords)
			gw.endGeometry()
			gw.endFeature()
			#dbg_log("plot line")
	
		gw.endFeatureCol()

	#dbg_log("geojson writing")
	gw.endFile()
	#dbg_log("endfile")

dbg_log("geojson writing")
print "complete"

# -- dbg -- #
#dbg_saveLog()

# --------- #

# utils

def removeWash( geo, complement=False ):
	f = open(geo,'r')
	lines = f.readlines()
	f.close()
	newLines = []
	onWash = False
	for i in range(len(lines)):
		line = lines[i]
		if "FeatureCollection" in line:
			if not onWash:
				onWash = True
			else:
				newLines.extend(lines[i:])
				if complement:
					newLines = lines[:i-1]
					newLines[ i-2 ] = "}];"
				break
		elif onWash:
			pass
		else:
			newLines.append(line)
	f = open(geo,'w')
	f.writelines(newLines)
	f.close()
		
	
#removeWash( GEOJSON_FILE, complement=True )