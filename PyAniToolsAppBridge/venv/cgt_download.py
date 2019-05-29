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

class CGTDownload():
    def __init__(self, database=None, ip_addr=None, username=None, password=None):
        # cgt connection member variables
        connection, self.database, error = cgt_core.login_cgt(
            ip_addr=ip_addr, username=username, password=password, database=database
        )
        if error:
            self.connection = None
        else:
            self.connection = connection

        # rig approved / published folders and work folders
        self._rig_approved_dir = "rig/approved/"
        self._rig_work_dir = "rig/work"

        # list of asset types to exclude
        self.exclude_asset_list = ["lgt"]
        # get a list of the asset types
        self.asset_types_cgt_path = "/LongGong/assets/"
        # get the full path to the asset type in cgt, i.e. '/LongGong/assets/char/'
        self.asset_types_paths = [
            asset_type for asset_type in self._get_directory_list(self.asset_types_cgt_path, abs_path=True)
            if asset_type.split("/")[-1] not in self.exclude_asset_list
        ]
        '''
        now build an asset list as a nested dict in format:
        {
            <asset type> : {
                'asset type path' = "path to these asset types ex: /LongGong/assets/char",
                '<asset name>' = { 
                    'rig path' : "path to asset rig root directory 
                                  ex: /LongGong/assets/char/charHei/rig/approved or work/"
                    'rig version' : "<version>, ex: 001"
                    
            },...
        }
        '''
        self.asset_list = {}
        for asset_type_path in self.asset_types_paths:
            asset_type_name = asset_type_path.split("/")[-1]
            self.asset_list[asset_type_name] = {}
            self.asset_list[asset_type_name]['asset type path'] = asset_type_path
            # build the asset names
            asset_names = self._get_directory_list(asset_type_path)
            for asset_name in asset_names:
                self.asset_list[asset_type_name][asset_name] = {}
                if self.has_rig(asset_type_name, asset_name):
                    if self.is_rig_published(asset_type_name, asset_name):
                        self.asset_list[asset_type_name][asset_name]['rig path'] = "{0}/{1}/rig/approved".format(
                            asset_type_path,
                            asset_name
                        )
                        version_path = "{0}/history/".format(self.asset_list[asset_type_name][asset_name]['rig path'])
                    else:
                        self.asset_list[asset_type_name][asset_name]['rig path'] = "{0}/{1}/rig/work/".format(
                            asset_type_path,
                            asset_name
                        )
                        version_path = self.asset_list[asset_type_name][asset_name]['rig path']
                    # list of file names which contain the version in the name. don't need full path, just file name
                    version_list = self._get_directory_list(version_path)
                    # get the latest version of the rig
                    self.asset_list[asset_type_name][asset_name]['rig version'] = None
                    #self.get_latest_version(version_list)
                else:
                    self.asset_list[asset_type_name][asset_name]['rig path'] = None
                    self.asset_list[asset_type_name][asset_name]['rig version'] = None

        print json.dumps(self.asset_list, indent=4)

    def has_rig(self, asset_type, asset_name):
        rig_dir = "{0}/{1}/rig/".format(self.asset_list[asset_type]['asset type path'], asset_name)
        if self._get_directory_list(rig_dir):
            return True
        else:
            return False

    def is_rig_published(self, asset_type, asset_name):
        rig_published_path = "{0}/{1}/{2}".format(
            self.asset_list[asset_type]['asset type path'],
            asset_name,
            self._rig_approved_dir
        )
        if self._get_directory_list(rig_published_path):
            return True
        else:
            return False

    def get_latest_version(self, file_list):
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(file_list, key=alphanum_key)

    def _get_directory_list(self, dir_path, abs_path=False):
        # add end slash
        if dir_path[-1] != '/':
            dir_path = dir_path + '/'

        file_list = []
        files_in_path = self.connection.send_web(
            "c_media_file", "search_folder", {"db": self.database, "dir": dir_path}
        )
        files_in_path = [file_path for file_path in files_in_path if file_path['name'].strip() != ""]
        for file_path in files_in_path:
            if file_path['is_file'].lower() == 'n':
                if abs_path:
                    file_list.append(dir_path + file_path['name'])
                else:
                    file_list.append(file_path['name'])
        return file_list


def get_file_with_walk_folder(cgt_connection, database, dir_path):
    """
    Walks a directory path in CGT (online/cloud area) to find all files. Uses recursion
    :param cgt_connection: the connection to cgt
    :param database: the database as a string
    :param dir_path: the path as a string
    :return: the file list, or false if can't get files
    """
    # check for valid database and path
    if not isinstance(database, (str, unicode)) or not isinstance(dir_path, (str, unicode)) \
            or database.strip() == '' or dir_path.strip() == '':
        return False

    # add end slash
    if dir_path[-1] != '/':
        dir_path = dir_path + '/'

    file_list = []
    try:
        # get file list from cgt as list of dicts
        files_in_path = cgt_connection.send_web("c_media_file", "search_folder", {"db": database, "dir": dir_path})
        files_in_path = [file_path for file_path in files_in_path if file_path['name'].strip() != ""]
        for file_path in files_in_path:
            if file_path['is_file'].lower() == 'y':
                file_list.append(dir_path + file_path['name'])
            else:
                file_list += get_file_with_walk_folder(cgt_connection, database, dir_path + file_path['name'])
        return file_list
    except Exception, e:
        print e.message
        return False


def callback(a, b, c):
    """
    From CGT dev
    :param a: amount downloaded
    :param b: not sure
    :param c: the total file size
    :return:
    """
    try:
        print "-->callback:",a,b,c
        print "-->file_size:{0}".format(c)
        if c == 0:
            print "-->progress:100"
        else:
            print "-->progress: %0.2f %%"%(float(a*100.00)/c)
    except Exception,e:
        print "error:", e.message


def download_cgt(cgt_paths, download_paths, database=None, ip_addr=None, username=None, password=None):
    """
    Access CGT and download a file, if no login info is given, then CG Teamworks app must be open and logged in,
    otherwise give ip address and login info
    :param cgt_paths: a list of file paths on CGT to download
    :param download_paths: a list of corresponding file paths on the C or Z drive that specify where the downloaded
    files go
    :param database: the CGT database to connect to
    :param ip_addr: optional ip address (no http://)
    :param username: optional username
    :param password:  optional password
    :returns error if encountered, otherwise None.
    """

    t_tw, t_db, error = cgt_core.login_cgt(ip_addr=ip_addr, username=username, password=password, database=database)
    if error:
        return error

    try:
        # list of files on cgt to download
        file_list_to_dl = []
        # list of file paths on local machine corresponding to the file on cgt, where to put cgt file downloaded
        download_loc_list = []

        # loop through the cgt paths provided and get the files to download
        for index in range(0, len(cgt_paths)):
            # get the list of files. Note if this is a single file, and empty list is returned
            file_list = get_file_with_walk_folder(t_tw, t_db, cgt_paths[index])
            # check if this is a list of files or single file
            if isinstance(file_list, list) and file_list:
                file_list_to_dl.extend(file_list)
                download_loc_list.extend(
                    [file_path.replace(cgt_paths[index], download_paths[index]) for file_path in file_list]
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
        # print the number of files to download
        print "file_total:{0}".format(len(file_list_to_dl))

        # print the files that will be downloaded so old files can be removed, use a '#' because a ":" will
        # break parsing since these are files and they have C:\ in it. Also put files to download and files on cgt
        # on same line otherwise can have issues where it doesn't process in order, ie. with separate print statements
        print "file_dirs_to_dl#{0}@file_names#{1}".format(
            ','.join(download_paths),                 # lets us find the existing files
            ",".join(download_loc_list)               # lets us know what files are on CGT
        )

        # download the files from CGT
        msg = t_tw.media_file.download_path(t_db, file_list_to_dl, download_loc_list, callback)
        # set explicit == True because msg may be True, or have content. Just putting if msg, would return None when msg
        # has content which is wrong
        if msg == True:
            return None
        else:
            return msg
    except Exception as e:
        error = "Error downloading from CGT, error reported is {0}".format(e)
        return error


def download_cgt2(cgt_paths, download_paths, database=None, ip_addr=None, username=None, password=None):
    """
    Access CGT and download a file, if no login info is given, then CG Teamworks app must be open and logged in,
    otherwise give ip address and login info
    :param cgt_paths: a list of file paths on CGT to download
    :param download_paths: a list of corresponding file paths on the C or Z drive that specify where the downloaded
    files go
    :param database: the CGT database to connect to
    :param ip_addr: optional ip address (no http://)
    :param username: optional username
    :param password:  optional password
    :returns error if encountered, otherwise None.
    """

    t_tw, t_db, error = cgt_core.login_cgt(ip_addr=ip_addr, username=username, password=password, database=database)

    # download the files from CGT
    msg = t_tw.media_file.download_path(t_db, cgt_paths, download_paths, callback)

def main():

    '''
    cgt_path = sys.argv[1]
    download_path = sys.argv[2]
    ip_addr = sys.argv[3]
    username = sys.argv[4]
    password = sys.argv[5]

    # prepare multiple paths into a list - python lists are passed as file1,file2,... since you can't pass
    # an actual list, i.e. [file1, file2]
    cgt_path = cgt_path.split(",")
    download_path = download_path.split(",")

    '''
    # To Test multi file d/l:
    cgt_path = []
    download_path = []

    #cgt_path.append("/LongGong/tools/eyeBallNode/")
    #download_path.append("C:\Users\Patrick\Documents\maya\plug-ins\\eyeBallNode\\")

    #cgt_path.append("/LongGong/assets/char/")
    #download_path.append("Z:\LongGong\\tools\maya\scripts\\rig_picker\\")

    # single file d/l
    #cgt_path.append("/LongGong/tools/PyAniToolsPackage.zip")
    #download_path.append("C:\Users\Patrick\Documents\maya\plug-ins\\")

    ip_addr = "172.18.100.246"
    username = "Patrick"
    password = "longgong19"

    import pyani.core.anivars
    import time
    ani_vars = pyani.core.anivars.AniVars()
    ani_vars.load_seq_shot_list()
    ani_vars.update(seq_name="Seq040")
    print "Shot count: ", len(ani_vars.get_shot_list())
    for shot in ani_vars.get_shot_list():
        path = "/LongGong/sequences/Seq040/{0}/audio/approved/Seq040_{0}.wav".format(shot)
        cgt_path.append(path)
        download_path.append("C:\Users\Patrick\Desktop\\temp\\Seq040_{0}.wav".format(shot))
    s= time.time()
    error = download_cgt2(cgt_path, download_path, ip_addr=ip_addr, username=username, password=password)
    e=time.time()
    print e-s
    if error:
        print error
    else:
        print ""



    """
    import time
    s= time.time()
    cgt_download = CGTDownload(ip_addr=ip_addr, username=username, password=password)
    e = time.time()
    print e-s

    #error = download_cgt(cgt_path, download_path, ip_addr=ip_addr, username=username, password=password)
    error = False
    if error:
        print error
    else:
        print ""
    """
if __name__ == '__main__':
    main()
