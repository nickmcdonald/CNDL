import re
import logging as log

class IesData:

	#def __init__(self):
	#	self.lumens = 600
	#	self.latRes = 50
	#	self.longRes = 1
	#	self.angles = []
	#	self.angles.append(IesAngle(y, latRes, val))

	def __init__(self, lumens, latRes, longRes, val):
		self.lumens = lumens
		self.latRes = latRes
		self.longRes = longRes
		self.angles = []

		y = 0
		while y < 360:
			self.angles.append(IesAngle(y, latRes, val))
			y += 360/longRes

	def getIESOutput(self, clamp):
		out = "IESNA91\n"
		out += "TILT=NONE\n"
		out += "1 {0} 1 {1} {2} 1 2 1 1 1\n1.0 1.0 0.0\n\n".format(self.lumens, len(self.angles[0].points), len(self.angles))

		n = 0
		for point in self.angles[0].points:
			out += "{0:.2f} ".format(point.latAngle)
			if n == 9:
				out += "\n"
				n = 0
			else:
				n = n + 1
		out += "\n\n"

		n = 0
		for angle in self.angles:
			out += "{0:.2f} ".format(angle.longAngle)
			if n == 9:
				out += "\n"
				n = 0
			else:
				n = n + 1
		out += "\n\n"

		for angle in self.angles:
			n = 0
			for point in angle.points:
				i = point.intensity
				if clamp and i > 1:
					i = 1
				out += "{0:.2f} ".format(self.lumens * i)
				if n == 9:
					out += "\n"
					n = 0
				else:
					n = n + 1
			out += "\n\n"

		return out


class IesAngle:

	def __init__(self, longAngle, latRes, intensity):
		self.longAngle = longAngle
		self.latRes = latRes
		self.points = []
		x = 0.00
		while x <= 180:
			self.points.append(IesPoint(longAngle, x, intensity))
			x += 180/(latRes-1)

		self.points[len(self.points)-1].latAngle = 180

	def updateAngle(self, longAngle):
		self.longAngle = longAngle
		for point in self.points:
			point.longAngle = longAngle


class IesPoint:

	def __init__(self, longAngle, latAngle, intensity):
		self.longAngle = longAngle
		self.latAngle = latAngle
		self.intensity = intensity
		self.mask = 0


def readIESData(inp):

	lines = inp.split("\n")

	version = ""
	details = {}
	settings = ""
	unknownNumbers = ""
	latAngleStartIdx = 0
	longAngleStartIdx = 0
	valsStartIdx = 0
	latAngles = []
	longAngles = []

	for idx, line in enumerate(lines):
		l = line.strip()
		if l.startswith('IES'):
			version = l
		elif line.startswith('['):
			name = l.split(']')[0].replace('[','')
			val = l.split(']')[1]
			details[name] = val
		elif l.startswith("TILT"):
			settings = re.sub(' +', ' ', lines[idx+1]).split(' ')
			unknownNumbers = lines[idx+2]
			latAngleStartIdx = idx + 3

	lumens = int(settings[1])
	factor = float(settings[2])
	latNums = int(settings[3])
	longNums = int(settings[4])
	unit = settings[6]
	# openingSize = tuple(settings[7], settings[8], settings[9])

	ies = IesData(lumens, latNums, longNums, 0)

	latAnglesRead = 0
	for idx in range(latAngleStartIdx, len(lines)):
		vals = lines[idx].split()
		for val in vals:
			latAngles.append(float(val))
			latAnglesRead += 1
		if latAnglesRead >= latNums:
			longAngleStartIdx = idx+1
			break

	longAnglesRead = 0
	for idx in range(longAngleStartIdx, len(lines)):
		vals = lines[idx].split()
		for val in vals:
			longAngles.append(float(val))
			longAnglesRead += 1
		if longAnglesRead >= longNums:
			valsStartIdx = idx+1
			break

	brightest = 0
	valsIdx = 0
	angleIdx = 0
	for idx in range(valsStartIdx, len(lines)):
		vals = lines[idx].split()
		for val in vals:
			if float(val) > brightest:
				brightest = float(val)
			if valsIdx >= latNums:
				valsIdx = 0
				angleIdx +=1
			ies.angles[angleIdx].points[valsIdx].intensity = float(val)
			ies.angles[angleIdx].points[valsIdx].latAngle = latAngles[valsIdx]
			valsIdx += 1

	ies.lumens = brightest
	for angle in ies.angles:
		for point in angle.points:
			point.intensity /= brightest

	return ies
