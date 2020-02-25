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


from enum import Enum

from ies import IesData, IesAngle

DEFAULT_LAT = 180
DEFAULT_LONG = 1


class MixMethod(Enum):
    ADD = 'Add'
    MULTIPLY = 'Multiply'
    AVERAGE = 'Average'
    MIN = 'Minimum'
    MAX = 'Maximum'


class FalloffMethod(Enum):
    SMOOTH = 'Smooth'
    LINEAR = 'Linear'
    SHARP = 'Sharp'


class LightDirection(Enum):
    UP = 1
    DOWN = 2


def mixIesData(ies1, ies2, method) -> IesData:
    newIes = IesData()

    longAngles = list(set().union(ies1.getLongAngles(), ies1.getLongAngles()))
    latAngles = list(set().union(ies1.getLatAngles(), ies1.getLatAngles()))

    for angle in longAngles:
        points = {}

        for point in latAngles:

            val1 = ies1.valueAt(long=angle, lat=point)
            val2 = ies2.valueAt(long=angle, lat=point)

            if method == MixMethod.ADD:
                points[point] = val1 + val2
            elif method == MixMethod.MULTIPLY:
                points[point] = val1 * val2
            elif method == MixMethod.AVERAGE:
                points[point] = (val1 + val2) / 2
            elif method == MixMethod.MIN:
                points[point] = min(val1, val2)
            elif method == MixMethod.MAX:
                points[point] = max(val1, val2)

        newIes.addAngle(angle, IesAngle(points=points))

    return newIes


def blankIesData(latRes=DEFAULT_LAT,
                 longRes=DEFAULT_LONG, intensity=0) -> IesData:
    ies = IesData()
    y = 0
    while y < 360:
        ies.addAngle(round(y, 2), IesAngle(latRes=latRes, intensity=intensity))
        y += 360/longRes

    return ies


def spotlightIesData(lumens, angle, falloff, falloffMethod,
                     lightDirection=LightDirection.DOWN,
                     latRes=DEFAULT_LAT, longRes=DEFAULT_LONG):
    pass


def normalizeIesData(ies) -> IesData:
    peak = ies.getPeakBrightness()
    for angle in ies.angles:
        for point in ies.angles[angle].points:
            ies.angles[angle].points[point] /= peak
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

    # lumens = float(data[1])
    # multiplyFactor = float(data[2])
    latAnglesNum = int(float(data[3]))
    longAnglesNum = int(float(data[4]))
    # units = int(float(data[6]))
    # openingWidth = float(data[7])
    # openingLength = float(data[8])
    # openingHeight = float(data[9])

    ies = IesData()

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
        ies.addAngle(float(data[angle]), IesAngle(points=points))

    return normalizeIesData(ies)
