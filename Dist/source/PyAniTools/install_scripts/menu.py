"""
Gets copied to c:\users\{user_name}\.nuke\pyanitools\ by install script
"""

import pyani.nuke.session as session

menu = session.AniNukeGui()

# created in custom init.py in C:\PyAniTools\lib
menu.setup_menu()
