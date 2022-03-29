from enum import Enum

import math
import random

from ies import IesData, IesAngle


DEFAULT_LAT = 180
DEFAULT_LONG = 1


class MixMethod(Enum):
    ADD = 'Add'
    SUBTRACT = 'Subtract'
    MULTIPLY = 'Multiply'
    AVERAGE = 'Average'
    MIN = 'Minimum'
    MAX = 'Maximum'


class FalloffMethod(Enum):
    SMOOTH = 'Smooth'
    LINEAR = 'Linear'
    SHARP = 'Sharp'
    ROOT = 'Root'


class LightDirection(Enum):
    DOWN = 'Down'
    UP = 'Up'


def linearInterpolate(a: float, b: float, x: float):
    return a * (1 - x) + b * x


def smoothInterpolate(a: float, b: float, x: float):
    ft = x * math.pi
    f = (1 - math.cos(ft)) / 2
    return a * (1 - f) + b * f


def sharpInterpolate(a: float, b: float, x: float):
    return (b - a) * x ** 2 + a


def rootInterpolate(a: float, b: float, x: float):
    return (b - a) * math.sqrt(x) + a


def mixIesData(ies1: IesData, ies2: IesData, method: MixMethod) -> IesData:
    newIes = IesData()

    longAngles = list(set().union(ies1.getLongAngles(), ies2.getLongAngles()))
    latAngles = list(set().union(ies1.getLatAngles(), ies2.getLatAngles()))

    for angle in longAngles:
        points = {}

        for point in latAngles:

            val1 = ies1.valueAt(long=angle, lat=point)
            val2 = ies2.valueAt(long=angle, lat=point)

            if method == MixMethod.ADD:
                points[point] = val1 + val2
            elif method == MixMethod.SUBTRACT:
                points[point] = val1 - val2
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


def blankIesData(latRes: int = DEFAULT_LAT,
                 longRes=DEFAULT_LONG, intensity=0) -> IesData:
    ies = IesData()
    long = 0.0
    while long < 360:
        ies.addAngle(round(long, 2),
                     IesAngle(latRes=latRes, intensity=intensity))
        long += round(360 / longRes, 2)

    return ies


def spotlightIesData(angle, falloff, falloffMethod=FalloffMethod.SMOOTH,
                     lightDirection=LightDirection.DOWN,
                     latRes=DEFAULT_LAT, longRes=DEFAULT_LONG) -> IesData:
    ies = IesData()
    long = 0.0
    while long <= 360:
        points = {}
        lat = 0
        while lat <= 180:
            if lightDirection is LightDirection.DOWN:
                if lat < angle:
                    falloffSize = angle * falloff
                    falloffStart = angle - falloffSize
                    if lat > falloffStart and falloffSize != 0.0:
                        amount = (lat - falloffStart) / falloffSize
                        if falloffMethod == FalloffMethod.SMOOTH:
                            points[lat] = smoothInterpolate(1, 0, amount)
                        elif falloffMethod == FalloffMethod.LINEAR:
                            points[lat] = linearInterpolate(1, 0, amount)
                        elif falloffMethod == FalloffMethod.SHARP:
                            points[lat] = sharpInterpolate(1, 0, amount)
                        elif falloffMethod == FalloffMethod.ROOT:
                            points[lat] = rootInterpolate(1, 0, amount)
                    else:
                        points[lat] = 1.0
                else:
                    points[lat] = 0.0
            else:
                if lat > 180 - angle:
                    falloffStart = 180 - angle
                    falloffSize = angle * falloff
                    if lat < falloffStart + falloffSize and falloffSize != 0.0:
                        amount = (lat - falloffStart) / falloffSize
                        if falloffMethod == FalloffMethod.SMOOTH:
                            points[lat] = smoothInterpolate(0, 1, amount)
                        elif falloffMethod == FalloffMethod.LINEAR:
                            points[lat] = linearInterpolate(0, 1, amount)
                        elif falloffMethod == FalloffMethod.SHARP:
                            points[lat] = sharpInterpolate(0, 1, amount)
                        elif falloffMethod == FalloffMethod.ROOT:
                            points[lat] = rootInterpolate(0, 1, amount)
                    else:
                        points[lat] = 1.0
                else:
                    points[lat] = 0.0

            lat += round(180 / latRes, 2)

        ies.addAngle(round(long, 2), IesAngle(points=points))

        long += 360 / longRes

    return ies


def normalizeIesData(ies: IesData) -> IesData:
    newIes = IesData()

    peak = ies.getPeakBrightness()
    for long in ies.getLongAngles():
        points = {}
        for lat in ies.getLatAngles():
            if peak != 0:
                points[lat] = ies.angles[long].points[lat] / peak
            else:
                points[lat] = 1
        newIes.addAngle(long, IesAngle(points=points))
    return newIes


def noiseIesData(latscale: float, latintensity: float,
                 longscale: float, longintensity: float,
                 seed: int = 0) -> IesData:
    ies = blankIesData(latRes=latscale, longRes=longscale)
    latnoise = {}
    longnoise = {}
    random.seed(seed)
    for lat in ies.getLatAngles():
        latnoise[lat] = 1-(random.randrange(0, int(latintensity*100), 1)/100)
    for long in ies.getLongAngles():
        longnoise[long] = 1-(random.randrange(0, int(latintensity*100), 1)/100)

    for long in ies.getLongAngles():
        for lat in ies.getLatAngles():
            ies.angles[long].points[lat] = latnoise[lat] * longnoise[long]

    return ies


def parseIesData(inp: str) -> IesData:

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
