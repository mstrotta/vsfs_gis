vsfs_gis
========
README

VSFS Map Creation

Project Goal:
  - To visually display locations of students and their relation to the projects
     they are working on, all over the world.

-----------------------------------------------------

Files:
 REQUIRED TO RUN
  JSON-js-master - only /json2.js is referenced
  geo_utils.py - referenced by vsfs mapper.py
  vsfs mapper.py - main script to create geojson
  vsfs_data.geojson - file read by vsfs_map.html and output by vsfs mapper.py
  vsfs_map.html - HTML/ javascript/ leaflet code
  vsfs_project_descriptions.csv
  vsfs_project_data.csv
  vsfs_student_data.csv
 
 NOT REQUIRED
  /dist - folder created by 'python setup.py py2exe' command
  coordBase.txt - local database maintained by vsfs mapper.py to minimize Google geocode queries
  geoChecker.py - some basic checks on geojson files for debugging
  logTime.txt - output by vsfs mapper.py for debugging
  setup.py - creates /dist folder for .exe version (for use on open-net/ without Python)
  
-----------------------------------------------------

Basic steps to open map in Chrome:

    1) Create the three CSV files student_data.csv, project_data.csv, project_description.csv,
       according to the specifications (below), and place them in the vsfs root directory
    2) Run vsfs mapper.exe 
    3) Open the vsfs_map.html file in chrome

* Currently the map needs to be connected to the internet, since it depends on
  loading a layer from openstreemap.org


-----------------------------------------------------


Developer:
 - To avoid the need for a Python interpreter, a windows executable is created
   using py2exe. If you make changes to the python code, recompile the 
   executable using the DOS command: python setup.py py2exe

 - The base-map tiles are from OpenStreetMap. A suitable replacement needs to be
   chosen since openstreemap's license does not allow for large-scale public use.
  
Design decisions:
 - projects without students are skipped

TODO:
 - add circle icons to key
 - For projects that share the same location, we currently merge all students to 
   a single project.  This needs to be re-worked so that no projects are discarded.
   Then, project markers which overlap need to be dealt with

 
-----------------------------------------------------
CSV file specification:
 *include at least one blank line at the end

CSV INDICES

student_data.csv:
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

project_data.csv:
PROJ_PROJECT_ID = 0
PROJ_PROJECT_TAG = 1
PROJ_PROJECT_NAME = 2
PROJ_COUNTRY = 3
FFICE = 4
PROJ_POST = 5
PROJ_SECTION = 6

project_description.csv:
DESC_PROJECT_TAG = 0
DESC_AGENCY = 1
DESC_POST = 2
DESC_COUNTRY = 3
DESC_PROJECT_NAME = 4
DESC_SUMMARY = 5
