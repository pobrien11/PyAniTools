'''
Dependencies

    Python packages
    ----------
    Use pip:
        PyQt4 : need the whl file, get here https://www.lfd.uci.edu/~gohlke/pythonlibs/, then pip install whl_file
        4.11.4
        QDarkStyle : pip install qdarkstyle, https://github.com/ColinDuquesnoy/QDarkStyleSheet, 2.6.4

     Making Executable - Pyinstaller
     ---------

     cd C:\Users\Patrick\PycharmProjects\PyImageViewer\venv\
     pyinstaller --onefile --name PyImageViewer main.py

'''

import sys
import qdarkstyle
import os
from pyani.media.image.exr_viewer import AniExrViewerGui

# set the environment variable to use a specific wrapper
# it can be set to pyqt, pyqt5, pyside or pyside2 (not implemented yet)
# you do not need to use QtPy to set this variable
os.environ['QT_API'] = 'pyqt'

# import from QtPy instead of doing it directly
# note that QtPy always uses PyQt5 API
from qtpy import QtWidgets


def main():
    # official version of the app
    __version__ = "1.0.0"

    # SETUP ==============================================

    # =====================================================

    # create the application and the main window
    app = QtWidgets.QApplication(sys.argv)
    window = AniExrViewerGui(
        __version__,
    )

    # setup stylesheet - note that in pyani.core.ui has some color overrides used by QFrame, and QButtons
    app.setStyleSheet(qdarkstyle.load_stylesheet_from_environment())

    # run
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
