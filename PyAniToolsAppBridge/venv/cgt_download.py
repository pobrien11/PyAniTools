import sys
import argparse

sys.path.append(r"c:\cgteamwork\bin\base")
sys.path.append('C:/cgteamwork/bin/cgtw')
import cgtw2
import ct

import cgt_core


def download_cgt(filters, filebox, file_name, database=None, model="eps",
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
        t_id_list = t_tw.task.get_id(t_db, model, filters)
        t_filebox_dict =  t_tw.task.get_sign_filebox(t_db, model, t_id_list[0], filebox)
        t_filebox_path = t_filebox_dict['path']
        t_upload_path = t_filebox_dict["path"].replace(t_filebox_dict['server'], '')

        # online file path
        t_online_file_path = t_tw.send_web('c_media_file', 'get_online_file_path',
                                           {'db': t_db, 'path': t_upload_path + '/' + file_name})

        # download
        msg = ct.http(t_ip, t_token).download(t_online_file_path, t_filebox_path + '/' + file_name)
        if msg == True:
            return None
        else:
            return msg
    except Exception as e:
        error = "Error downloading {0} from CGT, error reported is {1}".format(file_name, e)
        return error

def main():
    filters = [["eps.eps_name", "=", "Seq050"], ["task.task_name", "=", "Lighting"]]
    filebox = sys.argv[1]
    file_name = sys.argv[2]
    ip_addr = sys.argv[3]
    username = sys.argv[4]
    password = sys.argv[5]
    error = download_cgt(filters, filebox, file_name, ip_addr=ip_addr, username=username, password=password)
    if error:
        print error
    else:
        print ""

if __name__ == '__main__':
    main()
