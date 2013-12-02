from distutils.core import setup
import py2exe

setup(
    version = "0.1.0",
    description = "VSFS geoJson generator",
    name = "VSFS Mapper",
	
    console = ['vsfs mapper.py']
)