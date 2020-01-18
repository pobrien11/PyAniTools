import os
import sys
import json
import tempfile
import argparse

sys.path.append('c:/cgteamwork/bin/base')
sys.path.append('c:/cgteamwork/bin/cgtw/ct')
import cgtw2
from ct_http import ct_http

import cgt_core


class CGTFileListing:
    """
    Class that supports getting server file information
    """

    def __init__(self, connection=None, database=None, ip_addr=None, username=None, password=None):
        """
        If no user name, password and ip provided, CGT must be open
        :param connection: optional cgt_core object that provides connection to server
        :param database: optional CGT database to connect to
        :param ip_addr: optional ip address (no http://)
        :param username: optional username
        :param password:  optional password
        """
        if not connection:
            self.cgt_core = cgt_core.CGTCore(
                database=database, ip_addr=ip_addr, username=username, password=password
            )
        else:
            self.cgt_core = connection

    def server_get_file_listing_using_filter(self, root_path, folder_name_filter, json_path):
        """
        Gets the file directory listing for a path on the server. Uses filters to obtain files
        :param root_path: the path to get file directory information for
        :param folder_name_filter: a folder to look for in the path
        :param json_path: the path including file name for the json file that will hold the server file data retrieved
        :return: None if file directory information retrieved and written to disk, otherwise error
        """

        try:
            # get the folder id for the root path
            root_folder_id = self.cgt_core.connection.send_web(
                'c_media_file',
                'get_folder_id',
                {'db': self.cgt_core.database, 'path': root_path}
            )
            # search filter
            # the cgtw path must contain the filter
            filter_list = [
                ["#concat(array_to_string(media_folder.all_p_path, '/'),'/',media_folder.folder, '/')", "has",
                 "/" + folder_name_filter + "/"]
            ]
            # search only for files under the root path
            filter_list += [
                "and",
                "(",
                ["#array_position(media_folder.all_p_id, ""'" + root_folder_id + "')", "!is", "null"],
                "or",
                ["#media_folder.id", "=", root_folder_id], ")"
            ]
            # get the list of files from CGTW as a dictionary list according to the filter
            files_in_path = self.cgt_core.connection.send_web(
                "c_media_file",
                "get_online_file_with_filter",
                {"db": self.cgt_core.database, "filter_array": filter_list}
            )
        except Exception as e:
            error = "Error getting file information from CGT, error reported is {0}".format(e)
            return error

        # make sure the directory holding json file exists
        json_dir = '\\'.join(json_path.split("\\")[0:-1])
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)

        # save the cache data from the server to disk
        error = cgt_core.write_json(json_path, files_in_path)
        if error:
            return error

        return None

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
            files_in_path = self._get_cgt_dir_listing(dir_path)
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

    def get_modified_date(self, cgt_path):
        """
        Gets a file's last modified time
        :param cgt_path: a cgt server path
        :return: empty string if can't get file info, otherwise modify date/time of file as string
        """
        # get file list from cgt as list of dicts
        file_info = self._get_file_info_for_file(cgt_path)
        if not file_info:
            return ""

        return file_info['modify_time']

    def is_file(self, cgt_path):
        """
        Checks if the path is a file or directory
        :param cgt_path: a cgt server path
        :return True if its a file, False if not
        """
        # get file list from cgt as list of dicts
        file_info = self._get_file_info_for_file(cgt_path)

        if not file_info:
            return False

        if file_info['is_file'].lower() == 'y':
            return True
        else:
            return False

    def file_path_exists(self, cgt_path):
        """
        Check if a file path exists
        :param cgt_path: a cgt server path
        :return True if exists, False if not
        """
        # get file list from cgt as list of dicts
        file_info = self._get_file_info_for_file(cgt_path)

        if not file_info:
            return False
        else:
            return True

    def _get_file_info_for_file(self, cgt_path):
        """
        Gets the file dictionary from cgt containing information about the file
        :param cgt_path: a cgt server path
        :return a dict containing the files info or None if file doesn't exist
        """
        # split path so can get parent folder listing
        path_parts = cgt_path.split("/")
        # parent folder
        parent_dir = "/".join(path_parts[:-1])
        # folder or file to check
        name = path_parts[-1]
        # get file list from cgt as list of dicts
        files_in_path = self._get_cgt_dir_listing(parent_dir)

        for file_info in files_in_path:
            if file_info['name'] == name:
                return file_info
        return None

    def _get_cgt_dir_listing(self, dir_path):
        """
        utility function to get file list from cgt.
        :param dir_path: path to get file listing
        :return: a list of dicts
        """
        return self.cgt_core.connection.send_web(
            "c_media_file", "search_folder", {"db": self.cgt_core.database, "dir": dir_path + "/"}
        )


def main():
    debug = False

    # First lets create a new parser to parse the command line arguments
    # The arguments are  displayed when a user incorrectly uses your tool or if they ask for help
    parser = argparse.ArgumentParser(
        description="Get arguments for file list options",
        usage=""
    )

    if debug:
        ip_addr = "172.18.100.246"
        username = "publish"
        password = "publish"
        cgt_path = "/LongGong/sequences"
        folder_filter = "audio"
        temp_path = os.path.normpath(
            os.path.join(tempfile.gettempdir(), "pyanitools", "{0}_cgt_file_dict.json".format(folder_filter))
        )

        file_list_no_walk = None
        file_mode = None
        is_file = "False"
        path_exists = "False"
        modified_date = "False"
    else:
        # Positional Arguments
        parser.add_argument('ip_addr')
        parser.add_argument('username')
        parser.add_argument('password')
        parser.add_argument('cgt_path')

        # Keyword / Optional Arguments - action is value when provided, default is value when not provided

        # this indicates whether we will recurse through folder structure
        parser.add_argument('-nw', '--no_walk', default="")
        # this indicates if we are getting files only, directories only, or both, passed as:
        # "dirs" for directories only
        # "files" for files only
        # "files_and_dirs" for both
        parser.add_argument('-m', '--file_mode', default="")
        # a folder to filter, gets only files in folder, allows file info to be gotten all at once.
        parser.add_argument('-flt', '--folder_filter', default="")
        # when getting lots of file info put it in here, used with folder filter
        parser.add_argument('-tmp', '--temp_file', default="")
        # check if path is a file
        parser.add_argument('-f', '--is_file', default="")
        # check if path exists
        parser.add_argument('-fpe', '--path_exists', default="")
        # get date modified for file
        parser.add_argument('-md', '--modified_date', default="")

        args = parser.parse_args()

        ip_addr = args.ip_addr
        username = args.username
        password = args.password
        cgt_path = args.cgt_path
        folder_filter = args.folder_filter
        temp_path = args.temp_file

        file_list_no_walk = args.no_walk
        file_mode = args.file_mode
        is_file = args.is_file
        path_exists = args.path_exists
        modified_date = args.modified_date

    # make a cgt object
    cgt_file_listing = CGTFileListing(ip_addr=ip_addr, username=username, password=password)
    # make sure we connected
    if not cgt_file_listing.cgt_core.valid_connection():
        print cgt_file_listing.cgt_core.connection_error_msg
        return

    # getting all file info at once under a specified folder
    if folder_filter and temp_path:
        error = cgt_file_listing.server_get_file_listing_using_filter(
            cgt_path, folder_filter, temp_path
        )
        if error:
            print error
        else:
            print ""
        return

    # if checking a file for modified date, we can exit after done, no need to get file listing
    # or download files
    if modified_date:
        print cgt_file_listing.get_modified_date(cgt_path)
        return

    # if checking a path to see if its a file or directory, we can exit after done, no need to get file listing
    # or download files
    if is_file:
        if cgt_file_listing.is_file(cgt_path):
            print "True"
        else:
            print "False"
        return

    # if checking a path to see if it exists, we can exit after done, no need to get file listing
    # or download files
    if path_exists:
        if cgt_file_listing.file_path_exists(cgt_path):
            print "True"
        else:
            print "False"
        return

    # don't walk and get only directories. The default mode if no file mode is passed is directory only
    if file_list_no_walk == "True" and (not file_mode or file_mode == "dirs"):
        results = cgt_file_listing.get_file_list(cgt_path, dirs_only=True, walk=False)
        if isinstance(results, list):
            print ",".join(results)
        else:
            # print error
            print results
    # don't walk and get only files
    elif file_list_no_walk == "True" and file_mode == "files":
        results = cgt_file_listing.get_file_list(cgt_path, files_only=True, walk=False)
        if isinstance(results, list):
            print ",".join(results)
        else:
            # print error
            print results
    # don't walk, list both files and directories
    elif file_list_no_walk == "True" and file_mode == "files_and_dirs":
        results = cgt_file_listing.get_file_list(cgt_path, walk=False)
        if isinstance(results, list):
            print ",".join(results)
        else:
            # print error
            print results
    # walk recursively and get only files
    elif file_mode == "files":
        results = cgt_file_listing.get_file_list(cgt_path, files_only=True, walk=True)
        if isinstance(results, list):
            print ",".join(results)
        else:
            # print error
            print results
    # walk recursively and get only directories
    elif file_mode == "dirs":
        results = cgt_file_listing.get_file_list(cgt_path, dirs_only=True, walk=True)
        if isinstance(results, list):
            print ",".join(results)
        else:
            # print error
            print results
    # walk recursively and get both files and directories
    elif file_mode == "files_and_dirs":
        results = cgt_file_listing.get_file_list(cgt_path, walk=True)
        if isinstance(results, list):
            print ",".join(results)
        else:
            # print error
            print results
    else:
        print "WARNING: No action performed."


if __name__ == '__main__':
    main()
