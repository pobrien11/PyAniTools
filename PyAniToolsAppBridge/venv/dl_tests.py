import sys
import os
import json
import traceback


sys.path.append('c:/cgteamwork/bin/base')
sys.path.append('c:/cgteamwork/bin/cgtw/ct')
import cgtw2
from ct_http import ct_http

# list of cgt file paths and download locations
file_path_json = "C:\\Users\\Patrick\\Downloads\\dl_test\\dl_test_filepaths.json"
# processed cgt file paths
file_path_processed_json = "C:\\Users\\Patrick\\Downloads\\dl_test\\dl_test_filepaths_processed.json"


""" 
MULTI-THREADING METHODS
"""
# set the environment variable to use a specific wrapper
# it can be set to pyqt, pyqt5, pyside or pyside2 (not implemented yet)
# you do not need to use QtPy to set this variable
os.environ['QT_API'] = 'pyqt'
# import from QtPy instead of doing it directly
# note that QtPy always uses PyQt5 API
from qtpy import QtGui, QtWidgets, QtCore
from PyQt4.QtCore import pyqtSlot, pyqtSignal

class WorkerSignals(QtCore.QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QtCore.QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param fn: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type fn: function
    :param use_progress_callback: whether to use progress callback
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """
    def __init__(self, fn, use_progress_callback, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        if use_progress_callback:
            self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        """
        Initialize the runner function with passed args, kwargs.
        """
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exception_type, value = sys.exc_info()[:2]
            self.signals.error.emit((exception_type, value, traceback.format_exc()))
        else:
            # Return the result of the processing
            self.signals.result.emit(result)
        finally:
            # complete
            self.signals.finished.emit()


class CGTDownload():
    """
    class object that provides support to download files and get file lists from CGT
    """

    def __init__(self, database=None, ip_addr=None, username=None, password=None):
        """
        If no user name, password and ip provided, CGT must be open
        :param database: the CGT database to connect to
        :param ip_addr: optional ip address (no http://)
        :param username: optional username
        :param password:  optional password
        """

        self.thread_pool = QtCore.QThreadPool()
        self.thread_total = 0.0
        self.threads_done = 0.0


        if username == "":
            username = None
        if password == "":
            password = None

        # cgt connection member variables
        connection, database, error = self.login_cgt(
            ip_addr=ip_addr, username=username, password=password, database=database
        )

        self.connection_error_msg = ""

        if error:
            self.connection = None
            self.database = None
            # save the message
            self.connection_error_msg = error
        else:
            self.connection = connection
            self.database = database

    def login_cgt(self, ip_addr=None, database=None, username=None, password=None):
        """
        Log in to CGT, if no ip, username or password is provided then CGT must be open and you must be logged in
        :param ip_addr: optional ip address (no http://)
        :param database: optional the movie's database, defaults to show default set above in __t_db
        :param username: optional your username
        :param password:  optional your password
        :return: the connection and database and any errors. If can't connect returns None for the connection and database
        """
        try:
            # If you are logged in to CGT, can do "cgtw2.tw()", otherwise need username and password
            if ip_addr is None and username is None and password is None:
                t_tw = cgtw2.tw()
            else:
                t_tw = cgtw2.tw(ip_addr, username, password)
            # save databse if one provided, otherwise use show default
            if database:
                t_db = database
            else:
                t_db = "proj_longgong_0"
            return t_tw, t_db, None
        except Exception as e:
            error = "Could not connect to CGT using IP: {0}, Username: {1}, Password: {2}. Error is {3}".format(
                ip_addr,
                username,
                password,
                e
            )
            return None, None, error

    def valid_connection(self):
        """
        Check that a connection was made
        :return: True if connected to cgt, false if not
        """
        if not self.connection and not self.database:
            return False
        else:
            return True

    def is_file(self, cgt_path):
        """
        Checks if the path is a file or directory
        :param cgt_path: a cgt server path
        :return True if exists, False if not
        """

        # split path so can get parent folder listing
        path_parts = cgt_path.split("/")
        # parent folder
        parent_dir = "/".join(path_parts[:-1])
        # folder or file to check
        name = path_parts[-1]
        # get file list from cgt as list of dicts
        files_in_path = self.connection.send_web(
            "c_media_file", "search_folder", {"db": self.database, "dir": parent_dir}
        )

        for file_info in files_in_path:
            if file_info['name'] == name:
                if file_info['is_file'].lower() == 'y':
                    return True

        return False

    def get_file_list(self, dir_path, walk=True, files_only=False, dirs_only=False):
        """
        Walks a directory path in CGT (online/cloud area) to find all files. Uses recursion
        :param dir_path: the path as a string
        :param walk: use recursion to follow sub folders
        :param files_only: whether to only return files
        :param dirs_only: whether to only return directories
        :return: the file paths list, or string error message
        """
        # add end slash
        if dir_path[-1] != '/':
            dir_path = dir_path + '/'

        dir_path = dir_path.encode('utf-8')
        file_list = []
        try:
            # get file list from cgt as list of dicts
            files_in_path = self.connection.send_web(
                "c_media_file", "search_folder", {"db": self.database, "dir": dir_path}
            )
            # remove blank files
            files_in_path = [file_path for file_path in files_in_path if file_path['name'].strip() != ""]
            for file_path in files_in_path:
                if dirs_only:
                    if file_path['is_file'].lower() == 'n':
                        file_list.append(dir_path + file_path['name'].encode('utf-8'))
                elif files_only:
                    if file_path['is_file'].lower() == 'y':
                        file_list.append(dir_path + file_path['name'].encode('utf-8'))
                else:
                    file_list.append(dir_path + file_path['name'].encode('utf-8'))
                # get file list in sub folder
                if walk:
                    if file_path['is_file'].lower() == 'n':
                        file_list += self.get_file_list(
                            (dir_path + file_path['name']), walk=walk, files_only=files_only, dirs_only=dirs_only
                        )
            return file_list

        except Exception, e:
            print e.message

    @staticmethod
    def download_progress_callback(a, b, c):
        """
        From CGT dev
        :param a: amount downloaded
        :param b: not sure
        :param c: the total file size
        :return:
        """
        try:
            print "-->callback:", a, b, c
            print "-->file_size:{0}".format(c)
            if c == 0:
                print "-->progress:100"
            else:
                print "-->progress: %0.2f %%" % (float(a * 100.00) / c)
        except Exception, e:
            print "error:", e.message

    def thread_complete(self):
        """
        Called when a thread that checks an audio's timestamp completes
        """
        print "here"
        # a thread finished, increment our count
        self.threads_done += 1.0
        if self.threads_done > self.thread_total:
            return
        else:
            # get the current progress percentage
            print (self.threads_done / self.thread_total) * 100.0

            # check if we are finished
            if progress >= 100.0:
                print "finished threading"

    def download_cgt(
            self,
            cgt_paths,
            download_paths,
            use_callback=False,
            download_all_at_once = True,
            multi_thread = False
    ):
        """
        Access CGT and download a file, if no login info is given, then CG Teamworks app must be open and logged in,
        otherwise give ip address and login info
        :param cgt_paths: a list of file paths on CGT to download
        :param download_paths: a list of corresponding file paths on the C or Z drive that specify where the downloaded
        files go
        :param use_callback: optional, callback function
        :param download_all_at_once: boolean, should we call download on each file or make one large file list
        :param multi_thread: boolean, should we multi-thread the downloading
        :returns error if encountered, otherwise None.
        """

        try:
            # list of files on cgt to download
            file_list_to_dl = []
            # list of file paths on local machine corresponding to the file on cgt, where to put cgt file downloaded
            download_loc_list = []

            try:
                with open(file_path_processed_json, "r") as read_file:
                    file_paths_processed = json.load(read_file)
                file_list_to_dl = file_paths_processed['cgt']
                download_loc_list = file_paths_processed['local']
            except:
                print "prepping file list..."
                # loop through the cgt paths provided and get the files to download
                for index in range(0, len(cgt_paths)):
                    print "processing file {0} of {1}".format(index, len(cgt_paths))
                    # if this is a directory, get file listing
                    if not self.is_file(cgt_paths[index]):
                        # get the list of files.
                        file_list = self.get_file_list(cgt_paths[index], files_only=True)
                        # check if there are files, if not folder is empty so don't download anything
                        if file_list:
                            file_list_to_dl.extend(file_list)
                            download_loc_list.extend(
                                [file_path.replace(cgt_paths[index], download_paths[index]).replace("/", "\\") for file_path
                                 in
                                 file_list]
                            )
                    # its a single file
                    else:
                        # file to download
                        file_list_to_dl.extend([cgt_paths[index]])
                        # make the download path
                        path_parts = cgt_paths[index].split("/")
                        path_to_filename = '/'.join(path_parts[:-1])
                        download_loc_list.extend(
                            [os.path.normpath(cgt_paths[index].replace(path_to_filename, download_paths[index]))]
                        )
                # done processing write to file
                with open(file_path_processed_json, "w") as write_file:
                    d = {
                        "cgt": file_list_to_dl,
                        "local": download_loc_list
                    }
                    json.dump(d, write_file, indent=4)
                print "done with file prep."

            print "downloading files..."

            if download_all_at_once:
                # check if files to download
                if file_list_to_dl:
                    # download the files from CGT
                    if use_callback:
                        msg = self.connection.media_file.download_path(
                            self.database, file_list_to_dl, download_loc_list, self.download_progress_callback
                        )
                    else:
                        msg = self.connection.media_file.download_path(self.database, file_list_to_dl, download_loc_list)
                    # set explicit == True because msg may be True, or have content. Just putting if msg, would return
                    # None when msg has content which is wrong
                    if msg == True:
                        return None
                    else:
                        return msg
                else:
                    return None
            elif multi_thread:
                print ("Multi-threading with maximum %d threads" % self.thread_pool.maxThreadCount())

                for index in range(0, len(file_list_to_dl)):
                    # cgt method needs a list
                    file_to_dl = [file_list_to_dl[index]]
                    download_loc = [download_loc_list[index]]


                    # server_download expects a list of files, so pass list even though just one file
                    worker = Worker(
                        self.connection.media_file.download_path,
                        False,
                        self.database,
                        file_to_dl,
                        download_loc
                    )
                    self.thread_total += 1.0
                    self.thread_pool.start(worker)

                    # slot that is called when a thread finishes
                    worker.signals.finished.connect(self.thread_complete)
            else:
                for index in range(0, len(file_list_to_dl)):
                    # cgt method needs a list
                    file_to_dl = [file_list_to_dl[index]]
                    download_loc = [download_loc_list[index]]

                    print "downloading file {0} of {1}".format(index, len(file_list_to_dl))

                    msg = self.connection.media_file.download_path(self.database, file_to_dl,
                                                                   download_loc)
                    
                    # set explicit == True because msg may be True, or have content. Just putting if msg, would return
                    # None when msg has content which is wrong
                    if msg == True:
                        pass
                    else:
                        print msg


        except Exception as e:
            error = "Error downloading from CGT, error reported is {0}".format(e)
            return error

def main():

    test_num = 1

    # load file paths
    with open(file_path_json, "r") as read_file:
        file_paths = json.load(read_file)
    cgt_path = file_paths['cgt']
    local_path = file_paths['local']

    ip_addr = "172.18.100.246"
    username = "publish"
    password = "publish"

    # make a cgt object
    cgt_dl = CGTDownload(ip_addr=ip_addr, username=username, password=password)
    # make sure we connected
    if not cgt_dl.valid_connection():
        print cgt_dl.connection_error_msg
        return

    '''
    ##############################################
    TEST
    ##############################################
    '''


    # tests downloading a large file list (600+ files) by passing file list all at once. So one downlaod call
    if test_num == 1:
        error = cgt_dl.download_cgt(cgt_path, local_path, use_callback=True)
        if error:
            print error

    # tests downloading a large file list (600+ files) by calling download function per file. So 600+ downlaod calls
    elif test_num == 2:
        error = cgt_dl.download_cgt(cgt_path, local_path, download_all_at_once=False)
        if error:
            print error

    # multi-threading test
    elif test_num == 3:
        error = cgt_dl.download_cgt(cgt_path, local_path, download_all_at_once=False, multi_thread=True)
        if error:
            print error


if __name__ == '__main__':
    main()
    print "done."
