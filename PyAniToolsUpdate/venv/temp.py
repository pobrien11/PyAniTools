import sys
import os
from subprocess import Popen, PIPE, STDOUT

import pyani.core.util

# set the environment variable to use a specific wrapper
# it can be set to pyqt, pyqt5, pyside or pyside2 (not implemented yet)
# you do not need to use QtPy to set this variable
os.environ['QT_API'] = 'pyqt'
# import from QtPy instead of doing it directly
# note that QtPy always uses PyQt5 API
from qtpy import QtWidgets, QtCore, QtGui
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

        files_total = 0
        files_downloaded = 0

        # Poll process for new output until finished
        while True:
            next_line = process.stdout.readline()
            if next_line == '' and process.poll() is not None:
                break

            if 'file_total' in next_line:
                files_total = int(next_line.split(":")[-1])

            if files_total > 1:
                self.data_downloaded.emit("file_total:{0}".format(files_total))
            else:
                if 'file_size' in next_line:
                    bytes_size = float(next_line.split(":")[-1])
                    num_digits = pyani.core.util.number_of_digits(bytes_size)
                    if num_digits < 7:
                        converted_size = "{0} KB".format(bytes_size / 1000.0)
                    elif num_digits < 10:
                        converted_size = "{0} MB".format(bytes_size / 1000000.0)
                    else:
                        converted_size = "{0} GB".format(bytes_size / 1000000000.0)
                    self.data_downloaded.emit("file_size:{0}".format(converted_size))

            if 'progress' in next_line:
                percent_done = next_line.split(" ")[1]
                # if there are multiple files, show download progress as files downloaded / files total
                if files_total > 1:
                    if float(percent_done) == 100.0:
                        files_downloaded += 1
                        percent = float(files_downloaded) / float(files_total) * 100.0
                        self.data_downloaded.emit(percent)
                # one file, show actual progress
                else:
                    self.data_downloaded.emit(float(percent_done))

            sys.stdout.write(next_line)
            sys.stdout.flush()

        self.data_downloaded.emit("done")

        output = process.communicate()[0]
        exit_code = process.returncode

        if exit_code == 0:
            print output
        else:
            print "error : exit code {0}".format(exit_code)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        cmd = ["C:\cgteamwork\python\python.exe", "C:\Users\Patrick\PycharmProjects\PyAniTools\PyAniToolsAppBridge\\venv\cgt_download.py"]
        self.downloader = CGTDownloadMonitor(cmd)

        self.button = QtWidgets.QPushButton("Start")
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_label = QtWidgets.QLabel("Checking for downloads...")
        self.progress_label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_label)

        self.setLayout(layout)
        self.set_slots()

    def set_slots(self):
        self.downloader.data_downloaded.connect(self.progress_received)
        self.button.clicked.connect(self.start_download)

    def start_download(self):
        self.downloader.start()

    def progress_received(self, data):

        if isinstance(data, basestring):
            if "file_total" in data:
                self.progress_label.setText("Downloading {0} files.".format(data.split(":")[1]))
            elif "file_size" in data:
                self.progress_label.setText("Downloading {0}.".format(data.split(":")[1]))
            elif "done" in data:
                self.progress_label.setText("Downloading Complete.")
        else:
            self.progress_bar.setValue(data)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 480)
    window.show()
    sys.exit(app.exec_())