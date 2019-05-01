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
    cd C:\Users\Patrick\PycharmProjects\PyAniTools\PyAniToolsUpdate\venv\
    pyinstaller --onefile --console --icon=Resources\setup.ico --name PyAniToolsUpdate main.py
'''

import mmap
import logging
import sys
import os
import datetime
import tempfile
import zipfile
import qdarkstyle
import pyani.core.error_logging
from pyani.core.toolsinstall import AniToolsSetupGui

# set the environment variable to use a specific wrapper
# it can be set to pyqt, pyqt5, pyside or pyside2 (not implemented yet)
# you do not need to use QtPy to set this variable
os.environ['QT_API'] = 'pyqt'
# import from QtPy instead of doing it directly
# note that QtPy always uses PyQt5 API
from qtpy import QtWidgets


logger = logging.getLogger()


def main():
    app_name = "PyAniToolsUpdate"
    error_level = logging.DEBUG
    error_logging = pyani.core.error_logging.ErrorLogging(app_name, error_level)
    error_logging.setup_logging()
    
    force_update = False
    for arg in sys.argv:
        if "force_update" in arg:
            force_update = True

    # create the application and the main window
    app = QtWidgets.QApplication(sys.argv)
    window = AniToolsSetupGui("update", error_logging, testing=False)

    # setup stylesheet
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt())

    # run
    window.show()
    logging.info("force_update is {0}".format(force_update))
    window.run(force_update=force_update)
    app.exec_()


if __name__ == '__main__':
    main()
