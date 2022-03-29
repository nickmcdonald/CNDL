from ies import IesData

from qtpy.QtWidgets import QWidget, QStylePainter
from qtpy.QtGui import QBrush, QColor
from qtpy.QtCore import QRect, QSize, Qt


class Preview2D(QWidget):

    def __init__(self, ies: IesData, parent=None):
        QWidget.__init__(self, parent)
        self._ies = None

    def update(self, ies: IesData):
        self._ies = ies
        self.repaint()

    def sizeHint(self):
        return QSize(256, 256)

    def paintEvent(self, e):
        QWidget.paintEvent(self, e)
        painter = QStylePainter(self)
        painter.setRenderHint(QStylePainter.Antialiasing)

        brush = QBrush(Qt.SolidPattern)
        canvas = QRect(0, 0, 256, 256)
        painter.setBrush(brush)
        painter.setPen(QColor(0.0, 0.0, 0.0))
        painter.drawPie(canvas, 0, 360 * 16)

        if self._ies is None:
            return

        brightest = self._ies.angles[0].getPeakBrightness()

        points = self._ies.angles[0].points
        angles = sorted(self._ies.angles[0].points.keys())
        for angle in range(0, len(angles)-1):
            if brightest > 0.0:
                # color = int(points[angles[angle]] / brightest * 255)
                color = min(int(points[angles[angle]] * 255), 255)
            else:
                color = 0
            brush.setColor(QColor(color, color, color))
            painter.setBrush(brush)
            painter.setPen(QColor(color, color, color))

            startAngle = (-90 + angles[angle]) * 16
            spanAngle = (angles[angle+1] - angles[angle]) * 16
            painter.drawPie(canvas, startAngle, spanAngle)

            startAngle = (-90 - angles[angle]) * 16
            spanAngle = -(angles[angle+1] - angles[angle]) * 16
            painter.drawPie(canvas, startAngle, spanAngle)
