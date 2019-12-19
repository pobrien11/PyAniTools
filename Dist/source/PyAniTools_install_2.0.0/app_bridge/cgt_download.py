import sys
import os
import json
import re
import argparse

sys.path.append('c:/cgteamwork/bin/base')
sys.path.append('c:/cgteamwork/bin/cgtw/ct')
import cgtw2
from ct_http import ct_http

import cgt_core
import cgt_file_info


class CGTDownload:
    """
    class object that provides support to download files from CGT
    """

    def __init__(self, database=None, ip_addr=None, username=None, password=None):
        """
        If no user name, password and ip provided, CGT must be open
        :param database: the CGT database to connect to
        :param ip_addr: optional ip address (no http://)
        :param username: optional username
        :param password:  optional password
        """
        self.cgt_core = cgt_core.CGTCore(database=database, ip_addr=ip_addr, username=username, password=password)
        self.cgt_file_info_obj = cgt_file_info.CGTFileListing(connection=self.cgt_core)

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

    def download_cgt(
            self,
            cgt_paths,
            download_paths,
            use_callback=False,
            show_file_info=True
    ):
        """
        Access CGT and download a file, if no login info is given, then CG Teamworks app must be open and logged in,
        otherwise give ip address and login info
        :param cgt_paths: a list of file paths on CGT to download
        :param download_paths: a list of corresponding file paths on the C or Z drive that specify where the downloaded
        files go
        :param use_callback: optional, callback function
        :param show_file_info: optional, shows the files to be downloaded and number of files
        :returns error if encountered, otherwise None.
        """
        try:
            # list of files on cgt to download
            file_list_to_dl = []
            # list of file paths on local machine corresponding to the file on cgt, where to put cgt file downloaded
            download_loc_list = []

            # loop through the cgt paths provided and get the files to download
            for index in range(0, len(cgt_paths)):
                # check if path exists, if not no need to proceed
                if not self.cgt_file_info_obj.file_path_exists(cgt_paths[index]):
                    return "Error downloading from CGT, the file path {0} doesn't exist".format(cgt_paths[index])

                # if this is a directory, get file listing
                if not self.cgt_file_info_obj.is_file(cgt_paths[index]):
                    # get the list of files.
                    file_list = self.cgt_file_info_obj.get_file_list(cgt_paths[index], files_only=True)
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

            # todo: deprecate
            show_file_info = False
            if show_file_info:
                # print the number of files to download
                print "file_total:{0}".format(len(file_list_to_dl))
                # print the files that will be downloaded so old files can be removed, use a '#' because a ":" will
                # break parsing since these are files and they have C:\ in it. Also put files to download
                # and files on cgt on same line otherwise can have issues where it doesn't process in order, ie.
                # with separate print statements
                print u"file_dirs_to_dl#{0}@file_names#{1}".format(
                    ','.join(download_paths),  # lets us find the existing files
                    ",".join(download_loc_list)  # lets us know what files are on CGT
                )

            # check if files to download
            if file_list_to_dl:
                # download the files from CGT
                if use_callback:
                    msg = self.cgt_core.connection.media_file.download_path(
                        self.cgt_core.database, file_list_to_dl, download_loc_list, self.download_progress_callback
                    )
                else:
                    msg = self.cgt_core.connection.media_file.download_path(
                        self.cgt_core.database, file_list_to_dl, download_loc_list
                    )
                # set explicit == True because msg may be True, or have content. Just putting if msg, would return
                # None when msg has content which is wrong
                if msg == True:
                    return None
                else:
                    return msg
            else:
                return None

        except Exception as e:
            error = "Error downloading from CGT, error reported is {0}".format(e)
            return error


def main():
    debug = False

    if debug:
        # To Test multi file d/l:
        cgt_path = []
        download_path = []

        # cgt_path = "/LongGong/tools/maya/scripts/anim_startup/longgong_startup.mel,/LongGong/tools/maya/scripts/anim_startup/icons/animBot.BMP"
        # download_path = "Z:\LongGong\\tools\maya\scripts\\anim_startup\\,Z:\LongGong\\tools\maya\scripts\\anim_startup\\icons\\"

        # cgt_path.append("/LongGong/tools/maya/scripts/rig_picker/")
        # download_path.append("Z:\LongGong\\tools\maya\scripts\\rig_picker\\")

        # single file d/l
        # cgt_path.append("/LongGong/tools/PyAniToolsPackage.zip")
        # download_path.append("C:\Users\Patrick\Documents\maya\plug-ins\\")

        # cgt_path = "/LongGong/tools/maya/plugins/AOV_CC.gizmo"
        cgt_path = u'/LongGong/tools/maya/plugins/lt_awesome.lt'
        download_path = u'c:\\users\\patrick\\appdata\\local\\temp\\pyanitools\\maya_plugins'

        ip_addr = "172.18.100.246"
        username = "publish"
        password = "publish"
    else:
        cgt_path = sys.argv[1]
        download_path = sys.argv[2]
        ip_addr = sys.argv[3]
        username = sys.argv[4]
        password = sys.argv[5]

    # make a cgt object
    cgt_dl = CGTDownload(ip_addr=ip_addr, username=username, password=password)
    # make sure we connected
    if not cgt_dl.cgt_core.valid_connection():
        print cgt_dl.cgt_core.connection_error_msg
        return

    # prepare multiple paths into a list - python lists are passed as file1,file2,... since you can't pass
    # an actual list, i.e. [file1, file2]
    cgt_path = cgt_path.split(",")
    download_path = download_path.split(",")
    error = cgt_dl.download_cgt(cgt_path, download_path)
    if error:
        print error
    else:
        print ""


if __name__ == '__main__':
    main()
