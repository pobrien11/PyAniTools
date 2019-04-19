import sys
import os
import argparse
sys.path.append('c:/cgteamwork/bin/base')
sys.path.append('c:/cgteamwork/bin/cgtw/ct')
import cgtw2
from ct_http import ct_http

import cgt_core


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
    :param a: amount downloaded?
    :param b: not sure
    :param c: the total file size?
    :return:
    """
    try:
        print "-->callback:",a,b,c
        if c == 0:
            print "-->progress: 100%"
        else:
            print "-->progress: %0.2f %%"%(float(a*100.00)/c)
    except Exception,e:
        print "error:", e.message


def download_cgt(cgt_path, download_path, database=None, model="eps",
                 ip_addr=None, username=None, password=None):
    """
    Access CGT and download a file, if no login info is given, then CG Teamworks app must be open and logged in,
    otherwise give ip address and login info
    :param filters: used to locate file
    :param filebox: used to locate file
    :param file_name: name of the file to download
    :param data_base: the movie database, if None then defaults to show default in cgt_core
    :param model: unsure what this is, defaults to eps
    :param ip_addr: optional ip address (no http://)
    :param username: optional your username
    :param password:  optional your password
    :returns error if encountered, otherwise True.
    """

    t_tw, t_db, error = cgt_core.login_cgt(ip_addr=ip_addr, username=username, password=password, database=database)
    if error:
        return error

    try:
        t_token = t_tw.login.token()
        t_ip =  t_tw.login.http_server_ip()
        t_http = ct_http(t_ip, t_token)
        file_list = get_file_with_walk_folder(t_tw, t_db, cgt_path)

        if isinstance(file_list, list) and file_list:
            download_paths = [file_path.replace(cgt_path, download_path) for file_path in file_list]
            msg = t_tw.media_file.download_path(t_db, file_list, download_paths, callback)
            if msg == True:
                return None
            else:
                return msg
        else:
            path_parts = cgt_path.split("/")
            filename = path_parts[-1]
            path_to_filename = '/'.join(path_parts[:-1])
            download_path = os.path.normpath(cgt_path.replace(path_to_filename, download_path))
            # pass cgt path and download path as list because t_tw.media_file.download_path expects lists
            msg = t_tw.media_file.download_path(t_db, [cgt_path], [download_path], callback)
            if msg == True:
                return None
            else:
                return msg
    except Exception as e:
        error = "Error downloading {0} from CGT, error reported is {1}".format(cgt_path, e)
        return error

def main():

    cgt_path = sys.argv[1]
    download_path = sys.argv[2]
    ip_addr = sys.argv[3]
    username = sys.argv[4]
    password = sys.argv[5]

    '''
    # To Test:
    cgt_path = "/LongGong/tools/eyeBallNode"
    download_path = "C:\Users\Patrick\Documents\maya\plug-ins\\"
    ip_addr = "172.18.100.246"
    username = "Patrick"
    password = "longgong19"
    '''

    error = download_cgt(cgt_path, download_path, ip_addr=ip_addr, username=username, password=password)
    if error:
        print error
    else:
        print ""

if __name__ == '__main__':
    main()
