'''
Dependencies
    FFmpeg, 4.1
    ----------
    https://ffmpeg.zeranoe.com/builds/
    There is no install package, so move the ffmpeg folder where you want it, for example C:\FFmpeg\
    Open windows system environment variables, add the path where the ffmpeg executable is, for example
    C:\FFMpeg
    Restart any IDEs and command interfaces like cmdyer or cmd.

    Python packages
    ----------
    Use pip:
        OpenEXR : need the whl file, get here https://www.lfd.uci.edu/~gohlke/pythonlibs/, then pip install whl_file
        1.3.2
        ffmpeg : pip install ffmpeg-python, 1.4
        scandir pip install scandir (in python 3 this is built-in), 1.9.0
        PyQt4 : need the whl file, get here https://www.lfd.uci.edu/~gohlke/pythonlibs/, then pip install whl_file
        4.11.4
        QDarkStyle : pip install qdarkstyle, https://github.com/ColinDuquesnoy/QDarkStyleSheet, 2.6.4
        Natural Sort : pip install natsort, 5.5.0
        Opencv : pip install opencv-python
        Colorama : pip install colorama, 0.4.1
        Psutil : pip install psutil, 5.4.8

Making Executable - Pyinstaller
     ---------

     cd C:\Users\Patrick\PycharmProjects\PyAniTools\PyShoot\venv\
     pyinstaller --onefile --noconsole --icon=Resources\pyshoot_icon.ico --name PyShoot main.py
'''

import sys
import qdarkstyle
import os
import pyani.media.movie.create.ui


# set the environment variable to use a specific wrapper
# it can be set to pyqt, pyqt5, pyside or pyside2 (not implemented yet)
# you do not need to use QtPy to set this variable
os.environ['QT_API'] = 'pyqt'

# import from QtPy instead of doing it directly
# note that QtPy always uses PyQt5 API
from qtpy import QtWidgets


def main():

    # SETUP ==============================================
    # path to ffmpeg executable, bundled with PyShoot
    movie_generation = "C:\\PyAniTools\\installed\\ffmpeg\\bin\\ffmpeg"
    # path to playback tool, using rv
    movie_playback = r'C:\Program Files\Shotgun\RV-7.2.1\bin\rv'
    # enforce strict padding
    # enforce the same padding for whole image sequence
    strict_pad = True
    # =====================================================


    # make command line interface object (pyani.media.movie.create.ui)
    cli = pyani.media.movie.create.ui.AniShootCLI(movie_generation, movie_playback, strict_pad)

    # check if user passed no gui flag
    if not cli.args.nogui:

        # create the application and the main window
        app = QtWidgets.QApplication(sys.argv)
        window = pyani.media.movie.create.ui.AniShootGui(movie_generation, movie_playback, strict_pad)

        # setup stylesheet - note that in pyani.core.ui has some color overrides used by QFrame, and QButtons
        app.setStyleSheet(qdarkstyle.load_stylesheet_from_environment())

        # run
        window.show()
        app.exec_()
    else:
        log = cli.run()


if __name__ == '__main__':
    main()
