import sys

sys.path.append(r"c:\cgteamwork\bin\base")
sys.path.append('C:/cgteamwork/bin/cgtw')
import cgtw2
import ct

def login_cgt(ip_addr=None, database=None, username=None, password=None):
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
