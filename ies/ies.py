########################################################
#
# Copyright (C) 2020-2021 Nick McDonald <nick@lazymorninggames.com>
#
# This file is part of CNDL.
#
# CNDL can not be copied and/or distributed without the express
#
# permission of Nick McDonald
########################################################


class IesData:

    def __init__(self, lumens, factor=1.0, units=2,
                 openingWidth=0.0, openingLength=0.0, openingHeight=0.0):
        self.lumens = float(lumens)
        self.factor = float(factor)
        self.units = units
        self.openingWidth = float(openingWidth)
        self.openingLength = float(openingLength)
        self.openingHeight = float(openingHeight)
        self.angles = {}

    def addAngle(self, angle, iesAngle):
        self.angles[angle] = iesAngle

    def valueAt(self, lat, long=0) -> float:
        return 1.0

    def __str__(self) -> str:
        out = "IESNA91\n"
        out += "TILT=NONE\n"
        out += "1 {0:.2f} {1:.2f} {2} {3} 1 {4} {5:.2f} {6:.2f} {7:.2f}\n1.0 1.0 0.0\n\n"

        out = out.format(self.lumens,
                         self.factor,
                         len(self.angles[0].points),
                         len(self.angles),
                         self.units,
                         self.openingWidth,
                         self.openingLength,
                         self.openingHeight)

        out += self.angles[0].getLatAnglesOutput()
        out += "\n\n"

        for angle in sorted(self.angles.keys()):
            out += "{0:.2f} ".format(angle)
        out += "\n\n"

        for angle in sorted(self.angles.keys()):
            out += str(self.angles[angle])
            out += "\n\n"

        return out


class IesAngle:

    def __init__(self, latRes=0, intensity=0, points=None):
        if points is None:
            self.points = {}
            x = 0.00
            while x <= 180:
                self.points[round(x, 2)] = intensity
                x += 180 / (latRes - 1)
        else:
            self.points = points

    def getLatAnglesOutput(self) -> str:
        out = ""
        for angle in sorted(self.points.keys()):
            out += "{0:.2f} ".format(angle)
        return out

    def __str__(self) -> str:
        out = ""
        for angle in sorted(self.points.keys()):
            out += "{0:.2f} ".format(self.points[angle])
        return out


def createIesData(lumens=800, latRes=50, longRes=1, intensity=0) -> IesData:
    ies = IesData(lumens)
    y = 0
    while y < 360:
        ies.addAngle(round(y, 2), IesAngle(latRes=latRes, intensity=intensity))
        y += 360/longRes

    return ies


def parseIesData(inp) -> IesData:

    lines = [line.rstrip('\n') for line in inp]

    dataStartLine = "TILT=NONE"

    for idx, line in enumerate(lines):
        ln = line.strip()
        if ln.startswith("TILT"):
            dataStartLine = line
            break

    data = inp.split(dataStartLine)[1].split(None)

    lumens = float(data[1])
    multiplyFactor = float(data[2])
    latAnglesNum = int(float(data[3]))
    longAnglesNum = int(float(data[4]))
    units = int(float(data[6]))
    openingWidth = float(data[7])
    openingLength = float(data[8])
    openingHeight = float(data[9])

    ies = IesData(lumens, multiplyFactor, units,
                  openingWidth, openingLength, openingHeight)

    latAnglesStart = 13
    longAnglesStart = latAnglesStart + latAnglesNum
    valuesStart = longAnglesStart + longAnglesNum

    for angle in range(longAnglesStart, longAnglesStart + longAnglesNum):
        angleNum = angle - longAnglesStart
        angleDataStart = valuesStart + (angleNum * latAnglesNum)
        points = {}
        for lat in range(latAnglesStart, latAnglesStart + latAnglesNum):
            latNum = lat - latAnglesStart
            points[float(data[lat])] = float(data[angleDataStart + latNum])
        print(points)
        ies.addAngle(float(data[angle]), IesAngle(points=points))

    return ies
