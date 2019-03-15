
# -*- coding: utf-8 -*-
"""
Simple example using BarGraphItem
"""

import qdarkstyle
import pyqtgraph as pg
import os
import numpy as np

# set the environment variable to use a specific wrapper
# it can be set to pyqt, pyqt5, pyside or pyside2 (not implemented yet)
# you do not need to use QtPy to set this variable
os.environ['QT_API'] = 'pyqt'
# import from QtPy instead of doing it directly
# note that QtPy always uses PyQt5 API
from qtpy import QtWidgets, QtGui, QtCore


class BarGraph(pg.GraphicsView):
    def __init__(self, x, y, width=1.0, brush=QtGui.QColor(150, 150, 150)):
        super(BarGraph, self).__init__()

        plt = pg.PlotItem(labels={'left': 'Time', 'bottom': 'Frame'})
        self.setCentralWidget(plt)

        # the bar graph
        self.bar_graph_item = pg.BarGraphItem(x=x, height=y, width=width, brush=brush)
        self.__bar_graph_width = width

        plt.addItem(self.bar_graph_item)

        # save the view box
        self.vb = plt.vb
        self.vb.setMouseEnabled(x=True, y=False)
        self.vb.enableAutoRange(axis=self.vb.XAxis, enable=True)

        self.set_slots()

    def set_slots(self):
        self.scene().sigMouseClicked.connect(self.onClick)

    def onClick(self, event):
        pos = QtCore.QPointF(event.scenePos())
        mouse_point = self.vb.mapSceneToView(pos)
        print round(mouse_point.x())
        x = np.array([10, 12.5, 15, 20, 25, 30])
        y = np.array([25, 35, 27, 22, 29, 40])
        self.bar_graph_item.setOpts(x=x, height=y, width=2)

    @staticmethod
    def find_closest_shot(pos, shot_list, interval):
        """

        :param pos: mouse x position
        :param shot_list:
        :param interval: width of bars in graph
        :return:
        """
        half_interval = interval / 2
        for shot in shot_list:
            if (shot - half_interval) <= pos < (shot + half_interval):
                return shot


class Window(QtWidgets.QDialog):
    def __init__(self):
        super(Window, self).__init__()
        yellow = QtGui.QColor(234, 192, 25)
        x = np.arange(1001,1020)
        y = np.arange(1,20)
        self.bar_graph = BarGraph(x, y, width=1, brush=yellow)
        self.bar_graph.setStyle(QtWidgets.QCommonStyle())

        self.create_layout()

    def create_layout(self):
        layout = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel("TEST")
        layout.addWidget(title)
        layout.addWidget(self.bar_graph)
        self.setLayout(layout)


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    # create the application and the main window
    app = QtWidgets.QApplication(sys.argv)
    window = Window()

    # setup stylesheet - note that in pyani.core.ui has some color overrides used by QFrame, and QButtons
    app.setStyleSheet(qdarkstyle.load_stylesheet_from_environment())

    # run
    window.show()
    app.exec_()

