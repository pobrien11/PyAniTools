"""
Boilerplate script to update apps to the latest version using the pyani.core.appmanager.AppManager class

v 1.0.1

pyinstaller --onefile --name PyAniAppUpdater appupdater.py
"""

from pyani.core.appmanager import AppManager
import colorama


def main():

    # init the colored output to terminal
    colorama.init()

    # app properties
    app_update_script = "C:\\PyAniTools\\PyAniAppManagerUpdater.exe"
    app_name = "PyShoot"
    app_dl_path = "Z:\\LongGong\\PyAniTools\\PyAniTools.PyShoot.zip"
    app_install_path = "C:\\PyAniTools\\PyShoot\\"
    app_dist_path = "Z:\\LongGong\\PyAniTools\\dist\\"
    app_data_path = "Z:\\LongGong\\PyAniTools\\app_data\\"
    app_manager = AppManager(app_update_script, app_name, app_dl_path, app_install_path, app_dist_path, app_data_path)

    msg = "Starting update {0}.".format(app_manager.app_name)
    print ("{0}{1}".format(colorama.Fore.GREEN, msg))
    print(colorama.Style.RESET_ALL)

    error = app_manager.verify_paths()

    if error:
        print error

    error = app_manager.install(has_pref=True)
    if error:
        print ("{0}{1}".format(colorama.Fore.RED, error))
        print(colorama.Style.RESET_ALL)
    else:
        msg = "Successfully updated {0}.".format(app_manager.app_name)
        print ("{0}{1}".format(colorama.Fore.GREEN, msg))
        print(colorama.Style.RESET_ALL)


if __name__ == '__main__':
    main()
