'''
Dependencies

    Python packages
    ----------
    Use pip:
        PyQt4 : need the whl file, get here https://www.lfd.uci.edu/~gohlke/pythonlibs/, then pip install whl_file
        4.11.4
        QDarkStyle : pip install qdarkstyle, https://github.com/ColinDuquesnoy/QDarkStyleSheet, 2.6.4
        psutil : pip install psutil, 5.4.8
    pyani - custom library

Making Executable - Pyinstaller

     cd C:\Users\Patrick\PycharmProjects\PyAniTools\PyAppManager\venv\
     pyinstaller --onefile --noconsole --icon=Resources\pyappmngr_icon.ico --name PyAppMngr main.py

     update app_data.json and changelog

'''

import sys
import qdarkstyle
import os
from pyani.core.appmanager import AniAppMngrGui

# set the environment variable to use a specific wrapper
# it can be set to pyqt, pyqt5, pyside or pyside2 (not implemented yet)
# you do not need to use QtPy to set this variable
os.environ['QT_API'] = 'pyqt'
# import from QtPy instead of doing it directly
# note that QtPy always uses PyQt5 API
from qtpy import QtWidgets


def main():
    # official version of the app
    version = "1.2.0"

    # SETUP ==============================================

    # =====================================================

    # create the application and the main window
    app = QtWidgets.QApplication(sys.argv)
    window = AniAppMngrGui(version)

    # setup stylesheet - note that in pyani.core.ui has some color overrides used by QFrame, and QButtons
    app.setStyleSheet(qdarkstyle.load_stylesheet_from_environment())

    # run
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
