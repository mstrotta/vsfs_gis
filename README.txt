README

VSFS Map Creation

Project Goal:
  - To visually display locations of students and their relation to the projects
     they are working on, all over the world.

Introduction:
  The following steps should be followed to make the map:
    1) Create the three CSV files student_data.csv, project_data.csv, project_description.csv,
       according to the specifications (below), and place them in the vsfs root directory
    2) Run vsfs mapper.exe 
    3) Open the vsfs_map.html file in chrome

CSV file specification:
-include at least one blank line at the end


* Currently the map needs to be connected to the internet, since it depends on
  loading a layer from openstreemap.org

Developer:
 - To avoid the need for a Python interpreter, a windows executable is created
   using py2exe. If you make changes to the python code, recompile the 
   executable using the DOS command: python setup.py py2exe

 - The base-map tiles are from OpenStreetMap. A suitable replacement needs to be
   chosen since openstreemap's license does not allow for large-scale public use.
  

Code Run-through
 - 
 


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
PROJ_OFFICE = 4
PROJ_POST = 5
PROJ_SECTION = 6

project_description.csv:
DESC_PROJECT_TAG = 0
DESC_AGENCY = 1
DESC_POST = 2
DESC_COUNTRY = 3
DESC_PROJECT_NAME = 4
DESC_SUMMARY = 5