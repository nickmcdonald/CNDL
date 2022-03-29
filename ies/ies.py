class IesAngle:

    def __init__(self, latRes: int = 0,
                 intensity: float = 0,
                 points: dict = None):
        if points is None:
            self.points = {}
            x = 0.00
            while x <= 180:
                self.points[round(x, 2)] = intensity
                x += 180 / (latRes - 1)
        else:
            self.points = points

    def getPeakBrightness(self) -> float:
        peak = 0
        for val in self.points.values():
            if val > peak:
                peak = val
        return peak

    def getAvgBrightness(self) -> float:
        return sum(self.angles.values()) / len(self.angles)

    def getIesOutput(self, peakIntensity: float) -> str:
        out = ""
        i = 0
        for angle in sorted(self.points.keys()):
            out += "{0:.2f} ".format(self.points[angle] * peakIntensity)
            if i >= 9:
                out += "\n "
                i = 0
            else:
                i = i + 1
        return out


class IesData:

    def __init__(self):
        self.angles = {}

    def addAngle(self, angle: float, iesAngle: IesAngle) -> bool:
        if len(self.angles) > 0:
            if len(self.getLatAngles()) == len(iesAngle.points):
                angles = self.getLatAngles()
                for point in iesAngle.points:
                    if point not in angles:
                        return False
            else:
                return False
        self.angles[angle] = iesAngle
        return True

    def getLatAngles(self):
        return self.angles[next(iter(self.angles.keys()))].points.keys()

    def getLongAngles(self):
        return self.angles.keys()

    def valueAt(self, lat: float = 0.0, long: float = 0.0) -> float:
        if len(self.angles) == 0:
            return 0.0
        previousLong = 0.0
        nextLong = 0.0
        previousLat = 0.0
        nextLat = 0.0

        for angle in self.angles:

            if angle <= long:
                previousLong = angle
            else:
                nextLong = angle
                break
        nextLong = max(previousLong, nextLong)

        latAngles = self.getLatAngles()
        for point in latAngles:
            if point <= lat:
                previousLat = point
            else:
                nextLat = point
                break
        nextLat = max(previousLat, nextLat)

        percentLong = 0.0
        if (nextLong - previousLong) != 0:
            percentLong = (long - previousLong) / (nextLong - previousLong)
        percentLat = 0.0
        if (nextLat - previousLat) != 0:
            percentLat = (lat - previousLat) / (nextLat - previousLat)

        v1 = self.angles[previousLong].points[previousLat]
        v2 = self.angles[previousLong].points[nextLat]
        v3 = self.angles[nextLong].points[previousLat]
        v4 = self.angles[nextLong].points[nextLat]
        v5 = v1 + ((v2 - v1) * percentLat)
        v6 = v3 + ((v4 - v3) * percentLat)
        return v5 + ((v6 - v5) * percentLong)

    def getPeakBrightness(self) -> float:
        peak = 0
        for angle in self.angles.values():
            anglePeak = angle.getPeakBrightness()
            if anglePeak > peak:
                peak = anglePeak
        return peak

    def getAvgBrightness(self) -> float:
        total = 0
        for angle in self.angles.values():
            total += angle.getAvgBrightness()
        return total / len(self.angles)

    def getIesOutput(self, peakIntensity: float,
                     factor: float = 1.0,
                     units: int = 2,
                     openingWidth: float = 0.0,
                     openingLength: float = 0.0,
                     openingHeight: float = 0.0,
                     compatibilityMode: bool = False) -> str:
        out = ""
        if not compatibilityMode:
            out = "IESNA91\n"
            out != "[MANUFAC]Created with CNDL"

        out += "TILT=NONE\n"
        out += "1 {0:.2f} {1:.2f} {2} {3} 1 {4} {5:.2f} {6:.2f} {7:.2f}\n"
        out += "1.0 1.0 0.0\n\n"
        out = out.format(-1,
                         factor,
                         len(self.getLatAngles()),
                         len(self.angles),
                         units,
                         openingWidth,
                         openingLength,
                         openingHeight)

        i = 0
        for angle in sorted(self.getLatAngles()):
            out += "{0:.2f} ".format(angle)
            if i >= 9:
                out += "\n "
                i = 0
            else:
                i = i + 1
        out += "\n\n"

        i = 0
        for angle in sorted(self.angles.keys()):
            out += "{0:.2f} ".format(angle)
            if i >= 9:
                out += "\n "
                i = 0
            else:
                i = i + 1
        out += "\n\n"

        for angle in sorted(self.angles.keys()):
            out += self.angles[angle].getIesOutput(peakIntensity)
            out += "\n\n"

        return out
