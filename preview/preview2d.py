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


from qtpy.QtWidgets import QWidget, QStylePainter
from qtpy.QtGui import QBrush, QColor
from qtpy.QtCore import QRect, QSize, Qt

from ies import createIesData


class Preview2D(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setGeometry(QRect(0, 0, 256, 256))
        self._ies = createIesData()

    def update(self, ies):
        self._ies = ies
        self.repaint()

    def paintEvent(self, e):
        QWidget.paintEvent(self, e)
        painter = QStylePainter(self)
        self.resize(QSize(256, 256))

        brush = QBrush(Qt.SolidPattern)
        canvas = QRect(0, 0, 256, 256)
        painter.setBrush(brush)

        brightest = 0.0

        for point in self._ies.angles[0].points.values():
            if point > brightest:
                brightest = point

        points = self._ies.angles[0].points
        angles = sorted(self._ies.angles[0].points.keys())
        for angle in range(0, len(angles)-1):
            if brightest > 0.0:
                color = int(points[angles[angle]] / brightest * 255)
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
