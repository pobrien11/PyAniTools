'''
Dependencies Outside Main Python Lib

    Python packages
    ----------
    Use pip:
        PyQt4 : need the whl file, get here https://www.lfd.uci.edu/~gohlke/pythonlibs/, then pip install whl_file
        4.11.4
        QDarkStyle : pip install qdarkstyle, https://github.com/ColinDuquesnoy/QDarkStyleSheet, 2.6.4
    pyani - custom library

    # need console for grabbing output from external python scripts
    cd C:\Users\Patrick\PycharmProjects\PyAniTools\P\venv\
    pyinstaller --onefile --console --icon=Resources\setup.ico --name PyAniToolsUpdate main.py
'''

import sys
import os
import datetime
import tempfile
import zipfile
import qdarkstyle
import pyani.core.util


# set the environment variable to use a specific wrapper
# it can be set to pyqt, pyqt5, pyside or pyside2 (not implemented yet)
# you do not need to use QtPy to set this variable
os.environ['QT_API'] = 'pyqt'
# import from QtPy instead of doing it directly
# note that QtPy always uses PyQt5 API
from qtpy import QtWidgets, QtGui, QtCore


class AniToolsPackager(QtWidgets.QDialog):
    """
    Class to create the PyANiToolsPackage.zip. Has options for which parts of the package need to be updated. Does
    the versioning, copying and zipping needed to make the package
    """

    def __init__(self):
        super(AniToolsPackager, self).__init__()


        self.setWindowTitle('Py Ani Tools Setup')


        # set default window size
        self.resize(450, 600)

        # text entry for version info
        self.release_notes = QtWidgets.QTextEdit()
        # check box options - set in create_layout()
        self.update_cgt = None
        self.update_pyani = None
        self.update_menupy = None
        self.update_initpy = None
        self.update_scandirpy = None
        # list of checkboxes, one per app
        self.update_apps = []

        self.create_layout()
        self.set_slots()


    def create_layout(self):

        # parent to this class, this is the top level layout (self)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addStretch(1)
        h_layout_progress_label = QtWidgets.QHBoxLayout()
        h_layout_progress_label.addStretch(1)
        h_layout_progress_label.addWidget(self.progress_label)
        h_layout_progress_label.addStretch(1)
        main_layout.addLayout(h_layout_progress_label)
        h_layout_progress = QtWidgets.QHBoxLayout()
        h_layout_progress.addStretch(1)
        h_layout_progress.addWidget(self.progress)
        h_layout_progress.addStretch(1)
        main_layout.addLayout(h_layout_progress)
        h_layout_btn = QtWidgets.QHBoxLayout()
        h_layout_btn.addStretch(1)
        h_layout_btn.addWidget(self.close_btn)
        h_layout_btn.addStretch(1)
        main_layout.addLayout(h_layout_btn)
        main_layout.addItem(QtWidgets.QSpacerItem(5, 20))
        h_layout_report = QtWidgets.QHBoxLayout()
        h_layout_report.addStretch(1)
        h_layout_report.addWidget(self.report_txt)
        h_layout_report.addStretch(1)
        main_layout.addLayout(h_layout_report)
        main_layout.addStretch(1)

    def set_slots(self):
        pass


def main():

    # create the application and the main window
    app = QtWidgets.QApplication(sys.argv)
    window =

    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt())

    # run
    window.show()
    window.run()
    app.exec_()


if __name__ == '__main__':
    main()
