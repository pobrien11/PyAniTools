import sys
import os
from subprocess import Popen, PIPE, STDOUT

# set the environment variable to use a specific wrapper
# it can be set to pyqt, pyqt5, pyside or pyside2 (not implemented yet)
# you do not need to use QtPy to set this variable
os.environ['QT_API'] = 'pyqt'
# import from QtPy instead of doing it directly
# note that QtPy always uses PyQt5 API
from qtpy import QtWidgets

from PyQt4.QtCore import pyqtSignal, QThread



class CGTDownloadMonitor(QThread):
    """
    Monitors the output from CGT's download process. Looks for the line of output:
    -->progress number %

    Takes a command to execute - should be python interpreter path and then the python file as a list, for example:
    ["C:\cgteamwork\python\python.exe", "C:\PyAniTools\lib\cgt\cgt_download.py"]

    """

    # signal to fire when have progress to send
    data_downloaded = pyqtSignal(object)

    def __init__(self, cmd):
        QThread.__init__(self)
        self.cmd = cmd

    def run(self):
        process = Popen(self.cmd, shell=True, stdout=PIPE, stderr=STDOUT)

        # Poll process for new output until finished
        while True:
            next_line = process.stdout.readline()
            if next_line == '' and process.poll() is not None:
                break
            if 'progress' in next_line:
                percent_done = next_line.split(" ")[1]
            self.data_downloaded.emit("{0}\n".format(next_line))
            sys.stdout.write(next_line)
            sys.stdout.flush()

        output = process.communicate()[0]
        exit_code = process.returncode

        if exit_code == 0:
            print output
        else:
            print "error : exit code {0}".format(exit_code)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        cmd = ["C:\cgteamwork\python\python.exe", "C:\PyAniTools\lib\cgt\cgt_download.py"]
        self.downloader = CGTDownloadMonitor(cmd)

        self.list_widget = QtWidgets.QListWidget()
        self.button = QtWidgets.QPushButton("Start")
        self.progressBar = QtWidgets.QProgressBar(self)
        self.button.clicked.connect(self.start_download)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.progressBar)
        layout.addWidget(self.list_widget)

        self.setLayout(layout)
        self.set_slots()

    def set_slots(self):
        self.downloader.data_downloaded.connect(self.progress_received)

    def start_download(self):
        self.downloader.start()

    def progress_received(self, data):
        self.list_widget.addItem(unicode(data))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 480)
    window.show()
    sys.exit(app.exec_())