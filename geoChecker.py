#geoChecker.py

GEO_FILE = 'vsfs_data.geojson'

f = open(GEO_FILE,'r')
lines = f.readlines()
f.close()

print lines[0].strip().strip('[{').strip().strip('=')

class matchingError( Exception ): pass
class objectError( Exception ): pass

stack = []
linesRead = 0
itemCountStack = []
commaCountStack = []
matchMap = {"{":"}","[":"]"}
inString = False
numFeatures = 0
numProperty = 0
numGeometry = 0
numCollects = 0
for line in lines:
	
	# features
	if "\"Feature\"" in line:
		numFeatures += 1
	if "\"properties\"" in line:
		numProperty += 1
	if "\"geometry\"" in line:
		numGeometry += 1
	if "\"FeatureCollection\"" in line:
		numCollects += 1
	
	
	# paren matching
	for char in line:
		if char == '"':
			if stack[ len(stack) - 1 ] == '"':
				stack.pop()
				inString = False
			else:
				stack.append('"')
				inString = True
		if inString:
			continue
		elif char in ["{","["]:
			stack.append( char )
			itemCountStack.append(0)
			commaCountStack.append(0)
		elif char in ["}","]"]:
			if matchMap[ stack[ len(stack) - 1] ] == char:
				ending = stack.pop()
			else:
				raise matchingError("LinesRead: %d"%linesRead)
			# check last object
			if ending == "}":
				commaCount = commaCountStack.pop()
				itemCount = itemCountStack.pop()
				if commaCount != itemCount - 1:
					raise objectError("LinesRead: %d"%linesRead)

				
		elif char == ":":
			itemCountStack[ len(itemCountStack) - 1 ] += 1
		elif char == "," and stack[ len(stack) - 1 ] != "[":
			commaCountStack[ len(commaCountStack) - 1 ] += 1
		
	prevLine = line
	linesRead += 1
	
print linesRead,"lines read. No errors detected"
print "Features:",numFeatures
print "Property:",numProperty
print "Geometry:",numGeometry
print "Collects:",numCollects