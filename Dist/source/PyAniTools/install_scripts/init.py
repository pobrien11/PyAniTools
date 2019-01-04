"""
Gets copied to c:\users\{user_name}\.nuke\pyanitools\ by install script
"""

import pyani.nuke.session as session

movie_tool = "C:\\PyAniTools\\installed\\PyShoot\\PyShoot.exe"

cmds = session.AniNukeCmds(movie_tool)

# calls nuke.pluginAddPath on each sequences plugins, scripts, templates
# nuke needs to know about these on startup.
cmds.load_plugin_paths()
