'''
Dependencies

    Python packages
    ----------
    Use pip:
        PyQt4 : need the whl file, get here https://www.lfd.uci.edu/~gohlke/pythonlibs/, then pip install whl_file
        4.11.4
        QDarkStyle : pip install qdarkstyle, https://github.com/ColinDuquesnoy/QDarkStyleSheet, 2.6.4
    pyani - custom library

Making Executable - Pyinstaller, console needed due to external libs being called

     cd C:\Users\Patrick\PycharmProjects\PyAniTools\PyReviewDownload\venv\
     pyinstaller --onefile --console --icon=images\setup.ico --name review_download main.py

'''

import sys
import qdarkstyle
import os
import logging
import pyani.review.gui
import pyani.core.error_logging


# set the environment variable to use a specific wrapper
# it can be set to pyqt, pyqt5, pyside or pyside2 (not implemented yet)
# you do not need to use QtPy to set this variable
os.environ['QT_API'] = 'pyqt'
# import from QtPy instead of doing it directly
# note that QtPy always uses PyQt5 API
from qtpy import QtWidgets


def main():

    app_name = "Review_Download"
    error_level = logging.DEBUG
    error_logging = pyani.core.error_logging.ErrorLogging(app_name, error_level)
    error_logging.setup_logging()

    # create the application and the main window
    app = QtWidgets.QApplication(sys.argv)

    steps = [
        "Finding latest assets for review..This may take a few seconds",
        "Downloading assets for review"
    ]

    window = pyani.review.gui.AniReviewAssetDownloadGui(error_logging, steps)

    # setup stylesheet - note that in pyani.core.ui has some color overrides used by QFrame, and QButtons
    app.setStyleSheet(qdarkstyle.load_stylesheet_from_environment())

    # run
    window.show()
    window.run()
    app.exec_()


if __name__ == '__main__':
    main()
