import sys
import json

sys.path.append(r"c:\cgteamwork\bin\base")
sys.path.append('C:/cgteamwork/bin/cgtw')
import cgtw2
import ct


class CGTCore:
    """
    class object that provides support to connect to CGT
    """

    def __init__(self, database=None, ip_addr=None, username=None, password=None):
        """
        If no user name, password and ip provided, CGT must be open
        :param database: the CGT database to connect to
        :param ip_addr: optional ip address (no http://)
        :param username: optional username
        :param password:  optional password
        """
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

    def valid_connection(self):
        """
        Check that a connection was made
        :return: True if connected to cgt, false if not
        """
        if not self.connection and not self.database:
            return False
        else:
            return True

    @staticmethod
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
                connection = cgtw2.tw()
            else:
                connection = cgtw2.tw(ip_addr, username, password)
            # use database if one provided, otherwise use show default
            if not database:
                database = "proj_longgong_0"
            return connection, database, None
        except Exception as e:
            error = "Could not connect to CGT using IP: {0}, Username: {1}, Password: {2}. Error is {3}".format(
                ip_addr,
                username,
                password,
                e
            )
            return None, None, error


def write_json(json_path, user_data, indent=4):
    """
    Write to a json file
    :param json_path: the path to the file
    :param user_data: the data to write
    :param indent: optional indent, defaults to 4 spaces for each line
    :return: None if wrote to disk, error if couldn't write
    """
    try:
        with open(json_path, "w") as write_file:
            json.dump(user_data, write_file, indent=indent)
            return None
    except (IOError, OSError, EnvironmentError, ValueError) as e:
        error_msg = "Problem loading {0}. Error reported is {1}".format(json_path, e)
        return error_msg
