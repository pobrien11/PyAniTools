"""
Gets copied to c:\users\{user_name}\.nuke\pyanitools\ by install script
"""

import logging

import pyani.nuke.session as session
import pyani.core.error_logging

# logging setup
app_name = "Nuke"
error_level = logging.DEBUG
error_logging = pyani.core.error_logging.ErrorLogging(app_name, error_level)
error_logging.setup_logging()

# check if logging was setup correctly
if error_logging.error_log_list:
    errors = ', '.join(error_logging.error_log_list)
    print "session.py could not set up logging. Errors are {0}".format(errors)

movie_tool = "C:\\PyAniTools\\installed\\PyShoot\\PyShoot.exe"

cmds = session.AniNukeCmds(movie_tool)

# calls nuke.pluginAddPath to add sequence and shot selected from nuke launcher, and sets ani vars for the sequence
# and shot. nuke needs to know about plugins on startup, otherwise will not load them properly
cmds.load_nuke_env()
