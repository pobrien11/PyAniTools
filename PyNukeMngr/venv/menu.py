"""
Gets copied to c:\users\{user_name}\.nuke\pyanitools\ by install script
"""

import session

menu = nuke.menu("Nuke")
menu.addCommand("My Menu/Run My Awesome Code", lambda: session.my_function())