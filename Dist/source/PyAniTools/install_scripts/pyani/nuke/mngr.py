import os
import pyani.core.util
import pyani.core.ui
import pyani.core.appmanager


# set the environment variable to use a specific wrapper
# it can be set to pyqt, pyqt5, pyside or pyside2 (not implemented yet)
# you do not need to use QtPy to set this variable
os.environ['QT_API'] = 'pyqt'
# import from QtPy instead of doing it directly
# note that QtPy always uses PyQt5 API
from qtpy import QtGui, QtWidgets, QtCore


class AniNukeMngr(object):
    def __init__(self):
        self.ani_vars = pyani.core.util.AniVars()
        self.plugin_ext = (".gizmo", ".so")
        self.script_ext = ".py"
        self.template_ext = ".nk"
        self.plugins_json_name = self.ani_vars.plugins_json_name
        self.templates_json_name = self.ani_vars.templates_json_name

    def is_shot_localized(self, seq, shot):
        """
        Checks if the shot has copies of the sequence plugins
        :param seq: sequence name as Seq###
        :param shot: shot name as Shot###
        :return: True if has copies, false if not
        """
        if self.get_shot_localized_items(seq, shot):
            return True
        else:
            return False

    def has_localized_shots(self):
        """
        Check all shots to see if sequence has any shots that are localized
        :return: True if at least one localized shot, False if none
        """
        # build a list of all non localized shots, calls is_shot_localized
        shot_list = [shot for shot in self.ani_vars.get_shot_list()
                     if not self.is_shot_localized(self.ani_vars.seq_name, shot)]

        # if these lists are equal then no localized shots
        if len(shot_list) == len(self.ani_vars.get_shot_list()):
            return False
        return True

    def get_shot_localized_items(self, seq, shot):
        """
        gets a list of the localized plugins
        :param seq: sequence name as Seq###
        :param shot: shot name as Shot###
        :return: a list of all copied plugins - does not include json files
        """
        files = None
        self.ani_vars.update(seq, shot)
        shot_path = self.ani_vars.shot_comp_plugin_dir
        if os.path.exists(shot_path):
            # skip json files
            files = [ f for f in os.listdir(shot_path) if not f.endswith("json")]
        return files


class AniNukeMngrGui(pyani.core.ui.AniQMainWindow):
    def __init__(self):
        # build main window structure
        app_name = "PyNukeMngr"
        app_mngr = pyani.core.appmanager.AniAppMngr(app_name)
        # pass win title, icon path, app manager, width and height
        super(AniNukeMngrGui, self).__init__("Py Nuke Manager", "Resources\\pynukemngr.png", app_mngr, 1000, 1000 )

        self.nuke_mngr = AniNukeMngr()

        # main ui elements - styling set in the create ui functions
        self.btn_seq_setup = QtWidgets.QPushButton("Setup Sequence")
        self.btn_seq_update = QtWidgets.QPushButton("Update Sequence")
        self.btn_shot_script_update = QtWidgets.QPushButton("Update Shot Nuke Script")
        self.btn_shot_local = QtWidgets.QPushButton("Localize")
        self.btn_shot_unlocal = QtWidgets.QPushButton("Un-Localize")
        self.seq_select_menu = QtWidgets.QComboBox()
        self.localize_info_label = QtWidgets.QLabel("")
        # set later in create_ui() - use a custom function to generate labels, and don't really need the labels
        # to be class variables
        self.copy_gizmos_cbox = None
        self.copy_template_cbox = None
        self.create_shot_nuke_scripts = None
        self.show_local_cbox = None
        # populated by selection
        self.seq_update_tree = pyani.core.ui.CheckboxTreeWidget()
        self.shot_update_tree = pyani.core.ui.CheckboxTreeWidget()

        # make layout for this app and set signal / slots
        self.create_layout()
        self.set_slots()

    def create_layout(self):

        self.g_layout_vert_item_spacing = 5

        # SEQUENCE MENU
        h_layout_seq_menu = QtWidgets.QHBoxLayout()
        seq_select_label = QtWidgets.QLabel("Select Sequence:")
        seq_select_label.setFont(self.titles)
        h_layout_seq_menu.addWidget(seq_select_label)
        self.seq_select_menu.addItem("------")
        for seq in self.nuke_mngr.ani_vars.get_sequence_list():
            self.seq_select_menu.addItem(seq)
        h_layout_seq_menu.addWidget(self.seq_select_menu)
        h_layout_seq_menu.addStretch(1)
        self.main_layout.addLayout(h_layout_seq_menu)
        self.main_layout.addItem(self.v_spacer)

        # SEQUENCE SETUP -----------------------------------
        # title
        g_layout_seq_setup = QtWidgets.QGridLayout()
        seq_setup_title = QtWidgets.QLabel("Sequence Setup")
        seq_setup_title.setFont(self.titles)
        self.btn_seq_setup.setStyleSheet("background-color:{0};".format(pyani.core.ui.GREEN))
        self.btn_seq_setup.setMinimumSize(150, 30)
        g_layout_seq_setup.addWidget(seq_setup_title, 0, 0)
        g_layout_seq_setup.setColumnStretch(0, 1)
        g_layout_seq_setup.addWidget(self.btn_seq_setup, 0, 2)
        self.main_layout.addLayout(g_layout_seq_setup)
        self.main_layout.addWidget(pyani.core.ui.QHLine(pyani.core.ui.CYAN))
        # layout for options
        g_layout_seq_setup_opt = QtWidgets.QGridLayout()
        g_layout_seq_setup_opt.setHorizontalSpacing(20)
        g_layout_seq_setup_opt.setVerticalSpacing(self.g_layout_vert_item_spacing)
        # options
        copy_gizmos_cbox_label, self.copy_gizmos_cbox = pyani.core.ui.build_checkbox(
            "Copy Gizmos",
            True,
            "Copy Gizmos from the show to the sequence library"
        )
        copy_template_cbox_label, self.copy_template_cbox = pyani.core.ui.build_checkbox(
            "Copy Templates",
            True,
            "Copy the show's templates to the sequence library"
        )
        create_shot_nuke_scripts_cbox_label, self.create_shot_nuke_scripts_cbox = pyani.core.ui.build_checkbox(
            "Create Shot Nuke Comps",
            True,
            "Copy the show's nuke comp template to all shots in the sequence"
        )

        # use a list with a for loop to layout, don't have to keep changing rows and column numbers
        # when want to re-order, just change in list below
        # list of the widgets, put in order that they should be added
        widget_list = [(copy_gizmos_cbox_label, self.copy_gizmos_cbox),
                       (copy_template_cbox_label, self.copy_template_cbox),
                       (create_shot_nuke_scripts_cbox_label, self.create_shot_nuke_scripts_cbox)]
        self.main_layout.addLayout(self._grid_auto_layout(widget_list, g_layout_seq_setup_opt))
        self.main_layout.addItem(self.v_spacer)

        # UPDATE SEQUENCE -----------------------------------
        g_layout_seq_update = QtWidgets.QGridLayout()
        seq_update_title = QtWidgets.QLabel("Sequence Level")
        seq_update_title.setFont(self.titles)
        self.btn_seq_update.setStyleSheet("background-color:{0};".format(pyani.core.ui.GREEN))
        self.btn_seq_update.setMinimumSize(150, 30)
        g_layout_seq_update.addWidget(seq_update_title, 0, 0)
        g_layout_seq_update.setColumnStretch(0, 1)
        g_layout_seq_update.addWidget(self.btn_seq_update, 0, 2)
        self.main_layout.addLayout(g_layout_seq_update)
        self.main_layout.addWidget(pyani.core.ui.QHLine(pyani.core.ui.CYAN))
        # sequence menu and tree
        self.main_layout.addWidget(self.seq_update_tree)
        self.main_layout.addItem(self.v_spacer)

        # UPDATE SHOT -----------------------------------
        # title
        g_layout_shot_update = QtWidgets.QGridLayout()
        shot_update_title = QtWidgets.QLabel("Shot Level")
        shot_update_title.setFont(self.titles)
        self.btn_shot_script_update.setStyleSheet("background-color:{0};".format(pyani.core.ui.CYAN))
        self.btn_shot_script_update.setMinimumSize(150, 30)
        self.btn_shot_local.setStyleSheet("background-color:{0};".format(pyani.core.ui.GREEN))
        self.btn_shot_local.setMinimumSize(150, 30)
        self.btn_shot_unlocal.setStyleSheet("background-color:{0};".format(pyani.core.ui.GOLD))
        self.btn_shot_unlocal.setMinimumSize(150, 30)
        g_layout_shot_update.addWidget(shot_update_title, 0, 0)
        g_layout_shot_update.setColumnStretch(0, 1)
        g_layout_shot_update.addWidget(self.btn_shot_script_update, 0, 2)
        g_layout_shot_update.addWidget(self.btn_shot_local, 0, 3)
        g_layout_shot_update.addWidget(self.btn_shot_unlocal, 0, 4)
        self.main_layout.addLayout(g_layout_shot_update)
        self.main_layout.addWidget(pyani.core.ui.QHLine(pyani.core.ui.CYAN))
        # instructions
        h_layout_localize_instructions = QtWidgets.QHBoxLayout()
        instructions_label_title = QtWidgets.QLabel("To Localize:")
        instructions_label_title.setFont(self.bold_font)
        instructions_label = QtWidgets.QLabel("Select the plugin(s) you want to copy under the Sequence "
                                              "level. Next select the shots to copy to under the Shot Level. Finally "
                                              "click the green localize button.")
        instructions_label.setStyleSheet("color: gray;")
        h_layout_localize_instructions.addWidget(instructions_label_title)
        h_layout_localize_instructions.addWidget(instructions_label)
        h_layout_localize_instructions.addStretch(1)

        self.main_layout.addLayout(h_layout_localize_instructions)
        # layout for options
        g_layout_shot_update_opt = QtWidgets.QGridLayout()
        g_layout_shot_update_opt.setHorizontalSpacing(20)
        g_layout_shot_update_opt.setVerticalSpacing(self.g_layout_vert_item_spacing)
        # options
        show_local_cbox_label, self.show_local_cbox = pyani.core.ui.build_checkbox(
            "Show Only Localized Plugins",
            True,
            "Show only shots that have copies of the sequence Gizmos and Plugins"
        )
        widget_list = [(show_local_cbox_label, self.show_local_cbox)]
        # layout the widgets
        self.main_layout.addLayout(self._grid_auto_layout(widget_list, g_layout_shot_update_opt))
        self.localize_info_label.setStyleSheet("color:{0}".format(pyani.core.ui.CYAN))
        self.main_layout.addWidget(self.localize_info_label)
        self.main_layout.addWidget(self.shot_update_tree)

        self.add_layout_to_win()

    def set_slots(self):
        """Create the slots/actions that UI buttons / etc... do
        """
        self.btn_seq_setup.clicked.connect(self.seq_setup)
        self.btn_seq_update.clicked.connect(self.seq_update)
        self.seq_select_menu.currentIndexChanged.connect(self.update_ui)
        self.btn_shot_script_update.clicked.connect(self.update_shot_nuke_script)
        self.btn_shot_local.clicked.connect(self.shot_localize)
        self.btn_shot_unlocal.clicked.connect(self.shot_unlocalize)
        self.show_local_cbox.clicked.connect(self.set_shot_tree_display_mode)

    def seq_setup(self):
        """Copies plugins, and templates from the show to sequence library. Makes these directories if they
        don't exist. Also sets up shots creating the shot directory if doesn't exist, the shot comp directory if
        doesn't exist, and the shot comp plugins directory if doesn't exist
        """
        if self.seq_select_menu.currentIndex() == 0:
            self.msg_win.show_error_msg("Invalid Selection", "Please select a sequence first.")
            return

        progress = QtWidgets.QProgressDialog("Setting Up Sequence", "Cancel Setup", 0, 100)
        QtWidgets.QApplication.processEvents()

        # check if sequence lib exists, if not create
        if not os.path.exists(self.nuke_mngr.ani_vars.seq_lib):
            pyani.core.util.make_dir(self.nuke_mngr.ani_vars.seq_lib)

        # check if sequence comp lib exists, if not create
        if not os.path.exists(self.nuke_mngr.ani_vars.seq_comp_lib):
            pyani.core.util.make_dir(self.nuke_mngr.ani_vars.seq_comp_lib)

        # if plugins checked, then copy
        if self.copy_gizmos_cbox.checkState():
            # check if directory exists, if not make it
            if not os.path.exists(self.nuke_mngr.ani_vars.plugin_seq):
                pyani.core.util.make_dir(self.nuke_mngr.ani_vars.plugin_seq)
            # only copy if the directory is empty, otherwise user should be using update sequence area to install
            # new plugins.
            if not os.listdir(self.nuke_mngr.ani_vars.plugin_seq):
                pyani.core.util.copy_files(self.nuke_mngr.ani_vars.plugin_show, self.nuke_mngr.ani_vars.plugin_seq)

        progress.setValue(20)
        QtWidgets.QApplication.processEvents()

        # if templates checked, then copy
        if self.copy_template_cbox.checkState():
            # check if directory exists, if not make it
            if not os.path.exists(self.nuke_mngr.ani_vars.templates_seq):
                pyani.core.util.make_dir(self.nuke_mngr.ani_vars.templates_seq)
            # only copy if the directory is empty, otherwise user should be using update sequence area to install
            # new templates.
            if not os.listdir(self.nuke_mngr.ani_vars.templates_seq):
                pyani.core.util.copy_files(self.nuke_mngr.ani_vars.templates_show, self.nuke_mngr.ani_vars.templates_seq)

        progress.setValue(40)
        QtWidgets.QApplication.processEvents()

        error_log = []
        # if create shot nuke scripts checked, then create directories and copy show template to shots
        if self.create_shot_nuke_scripts_cbox.checkState():
            percent_inc = 60.0 / float(len(self.nuke_mngr.ani_vars.get_shot_list()))
            for shot in self.nuke_mngr.ani_vars.get_shot_list():
                # update ani vars
                self.nuke_mngr.ani_vars.update(self.nuke_mngr.ani_vars.seq_name, shot)
                # list of paths to check for existence
                path_checklist = [self.nuke_mngr.ani_vars.shot_dir,
                                  self.nuke_mngr.ani_vars.shot_comp_dir,
                                  self.nuke_mngr.ani_vars.shot_comp_plugin_dir,
                                  self.nuke_mngr.ani_vars.shot_comp_work_dir]
                for path in path_checklist:
                    # check if directory exists, if not make it
                    if not os.path.exists(path):
                        pyani.core.util.make_dir(path)

                # build name for comp file
                comp_source = os.path.join(self.nuke_mngr.ani_vars.templates_seq,
                                           self.nuke_mngr.ani_vars.shot_master_template)
                comp_name = "{0}_{1}_V001.nk".format(self.nuke_mngr.ani_vars.seq_name,
                                                     self.nuke_mngr.ani_vars.shot_name)
                comp_dest = os.path.join(self.nuke_mngr.ani_vars.shot_comp_work_dir, comp_name)
                # only copy if doesn't exist
                if not os.path.exists(comp_dest):
                    error = pyani.core.util.copy_file(comp_source, comp_dest)
                    if error:
                        error_log.append(error)

                progress.setValue(progress.value() + percent_inc)
                QtWidgets.QApplication.processEvents()
            if error_log:
                self.msg_win.show_error_msg("Copy Error", ", ".join(error_log))

        self.update_ui()
        self.progress_win.msg_box.hide()
        self.msg_win.show_info_msg("Setup Complete", "Sequence {0} is setup.".format(self.nuke_mngr.ani_vars.seq_name))

    def update_ui(self):
        """rebuilds both version trees
        """
        # update ani vars with the selected sequence
        self.nuke_mngr.ani_vars.update(self.seq_select_menu.currentText())
        self.populate_seq_vers_tree()
        self.populate_shot_vers_tree()

    def populate_seq_vers_tree(self):
        """
        Builds the version tree - structure is:
        plugins
            each plugin below with version and description. red if missing, yellow if out of date, white current vers
        templates
            same as plugins
        """
        # clear the tree, so we can rebuild
        self.seq_update_tree.clear_all_items()

        tree_items = []
        tree_items.append(
            self._build_seq_vers_tree_item(
                self.nuke_mngr.ani_vars.plugin_show,
                self.nuke_mngr.ani_vars.plugin_seq,
                "Plugins",
                self.nuke_mngr.plugins_json_name
            )
        )
        tree_items.append(
            self._build_seq_vers_tree_item(
                self.nuke_mngr.ani_vars.templates_show,
                self.nuke_mngr.ani_vars.templates_seq,
                "Templates",
                self.nuke_mngr.templates_json_name
            )
        )
        self.seq_update_tree.build_checkbox_tree(tree_items, 3,  True)

    def update_shot_nuke_script(self):
        """Update the selected shots nuke scripts. Tells users progress and which shots it updated and any errors
        """
        shots = [item for item in self.shot_update_tree.get_tree_checked() if "Shot" in item]
        error_log = []
        shot_log = []
        progress = QtWidgets.QProgressDialog("Updating Shots", "Cancel Setup", 0, 100)
        percent_inc = 100.0 / float(len(shots))
        QtWidgets.QApplication.processEvents()
        for shot in shots:
            # update ani vars
            self.nuke_mngr.ani_vars.update(self.nuke_mngr.ani_vars.seq_name, shot)
            # build name for comp file
            comp_source = os.path.join(self.nuke_mngr.ani_vars.templates_seq,
                                       self.nuke_mngr.ani_vars.shot_master_template)
            comp_name = "{0}_{1}_V001.nk".format(self.nuke_mngr.ani_vars.seq_name,
                                                 self.nuke_mngr.ani_vars.shot_name)
            comp_dest = os.path.join(self.nuke_mngr.ani_vars.shot_comp_work_dir, comp_name)
            error = pyani.core.util.copy_file(comp_source, comp_dest)
            # log error, or if no error log shot so can report success
            if error:
                error_log.append(error)
            else:
                shot_log.append(shot)
            progress.setValue(progress.value() + percent_inc)
            QtWidgets.QApplication.processEvents()

        if error_log:
            self.msg_win.show_error_msg("Copy Error", ", ".join(error_log))

        progress.setValue(100)
        QtWidgets.QApplication.processEvents()
        self.progress_win.msg_box.hide()
        # show a message since there is no visual indication in gui that shots updated
        self.msg_win.show_info_msg("Update Complete",
                                   "Shot Update Complete. Updated: {0}".format(", ".join(shot_log)))

    def seq_update(self):
        """Update seq library files with show library files
        """
        plugins = [item for item in self.seq_update_tree.get_tree_checked()
                   if item.endswith(self.nuke_mngr.plugin_ext)]
        templates = [item for item in self.seq_update_tree.get_tree_checked()
                     if item.endswith(self.nuke_mngr.template_ext)]

        error_log = []
        error = self.copy_lib_to_seq(self.nuke_mngr.ani_vars.plugin_show,
                                     self.nuke_mngr.ani_vars.plugin_seq,
                                     plugins,
                                     self.nuke_mngr.plugins_json_name)
        if error:
            error_log.extend(error)

        error = self.copy_lib_to_seq(self.nuke_mngr.ani_vars.templates_show,
                                     self.nuke_mngr.ani_vars.templates_seq,
                                     templates,
                                     self.nuke_mngr.templates_json_name)
        if error:
            error_log.extend(error)

        # show final error log
        if error_log:
            self.msg_win.show_error_msg("Copy Error", ", ".join(error_log))

        # refresh the ui
        self.populate_seq_vers_tree()

    def copy_lib_to_seq(self, show_lib, seq_lib, lib_items, json_name):
        """
        Copies files in the show library to the sequence library along with the json file
        :param show_lib: path to show comp lib
        :param seq_lib: path to seq comp lib
        :param lib_items: the files to copy
        :param json_name: name of the json file for the library items. contains version info
        :return: any errors encountered, as a list
        """
        error_log = []
        # copy the lib items (ie plugins etc...) that are checked
        for lib_item in lib_items:
            show_path = os.path.join(show_lib, lib_item)
            seq_path = os.path.join(seq_lib, lib_item)
            error = pyani.core.util.copy_file(show_path, seq_path)
            if error:
                error_log.append(error)
        # also update the json file
        error = self.update_version_in_json(show_lib, seq_lib, lib_items, json_name)
        if error:
            error_log.append(error)

        return error_log

    @staticmethod
    def update_version_in_json(show_lib, seq_lib, lib_items, json_name):
        """
        Updates the sequence json version with the show version for the selected lib items
        :param show_lib: path to show comp lib
        :param seq_lib: path to seq comp lib
        :param lib_items: the files to copy
        :param json_name: name of the json file for the library items. contains version info
        :return error if any encountered, otherwise None
        """
        # build the json paths
        show_lib_json_path = os.path.join(show_lib, json_name)
        seq_lib_json_path = os.path.join(seq_lib, json_name)
        # open the json
        show_lib_json = pyani.core.util.load_json(show_lib_json_path)
        seq_lib_json = pyani.core.util.load_json(seq_lib_json_path)

        # if not a dict then is an error
        if not isinstance(show_lib_json, dict):
            return show_lib_json
        if not isinstance(seq_lib_json, dict):
            return seq_lib_json

        # modify version for each lib item
        for lib_item in lib_items:
            # get show version
            show_vers = show_lib_json[lib_item]["version"]
            # set seq version to show version
            seq_lib_json[lib_item]["version"] = show_vers

        # save to disk
        error = pyani.core.util.write_json(seq_lib_json_path, seq_lib_json, indent=2)
        if error:
            return error

        # no problems, return none
        return None

    def populate_shot_vers_tree(self):
        """
        Builds the version tree - structure is:
        shot - yellow if has localized plugins, white if no localized plugins
            each plugin below with version and description. red if missing, yellow if out of date, white current vers
            if the plugin is unknown show as grey
        """
        tree_items = []
        seq_versions = pyani.core.util.load_json(os.path.join(self.nuke_mngr.ani_vars.plugin_seq,
                                                              self.nuke_mngr.plugins_json_name))
        seq = self.nuke_mngr.ani_vars.seq_name
        # clear the tree, so we can rebuild
        self.shot_update_tree.clear_all_items()

        # skip if the sequence isn't setup correctly - ie missing json info
        if not seq_versions:
            tree_item = {"root": pyani.core.ui.CheckboxTreeWidgetItem(
                ["Sequence missing json information, Please run sequence setup."], [pyani.core.ui.RED]
            )}
            tree_items.append(tree_item)
            self.shot_update_tree.build_checkbox_tree(tree_items, 1)
        else:
            # label lets user know when no shots are localized
            if self.nuke_mngr.has_localized_shots():
                self.localize_info_label.setText("")
            else:
                self.localize_info_label.setText("No shots in this sequence are localized.")

            for shot in self.nuke_mngr.ani_vars.get_shot_list():
                # check if shot has localized plugins color yellow
                if self.nuke_mngr.is_shot_localized(seq, shot):
                    shot_version = pyani.core.util.load_json(
                        os.path.join(self.nuke_mngr.ani_vars.shot_comp_plugin_dir, self.nuke_mngr.plugins_json_name)
                    )
                    tree_item = {"root": pyani.core.ui.CheckboxTreeWidgetItem([shot], [pyani.core.ui.RED])}
                    # get list of localized plugins and build tree items for each
                    localized_items = self.nuke_mngr.get_shot_localized_items(seq, shot)
                    tree_child_items = []
                    for item in localized_items:
                        # item is in sequence, a known plugin
                        if item in seq_versions.keys() and item.endswith(self.nuke_mngr.plugin_ext):
                            # check version - yellow if not the latest version
                            if not seq_versions[item]["version"] == shot_version[item]["version"]:
                                # show version of shot, and version of the seq in parenthesis
                                version_text = "{0}     ({1})".format(
                                    shot_version[item]["version"],
                                    seq_versions[item]["version"]
                                )
                                text = [item, version_text, seq_versions[item]["desc"]]
                                color = [pyani.core.ui.YELLOW, pyani.core.ui.YELLOW, QtCore.Qt.gray]
                            else:
                                text = [item, shot_version[item]["version"], seq_versions[item]["desc"]]
                                color = [None, None, QtCore.Qt.gray]
                            tree_child_items.append(pyani.core.ui.CheckboxTreeWidgetItem(text, color))
                        # unknown plugin
                        else:
                            text = [item, "unknown plugin"]
                            color = [QtCore.Qt.gray, QtCore.Qt.gray]
                            tree_child_items.append(pyani.core.ui.CheckboxTreeWidgetItem(text, color))
                    tree_item["children"] = tree_child_items
                else:
                    tree_item = {"root": pyani.core.ui.CheckboxTreeWidgetItem([shot])}
                tree_items.append(tree_item)
            self.shot_update_tree.build_checkbox_tree(tree_items, 3)
            # call to hide or show only localized shots based off default checkbox state
            self.set_shot_tree_display_mode()

    def set_shot_tree_display_mode(self):
        """Shows all shots or just localized shots based off user selection. Displays message if no localized shots
        """
        seq = self.nuke_mngr.ani_vars.seq_name
        if self.nuke_mngr.ani_vars.is_valid_seq(seq):
            if self.show_local_cbox.checkState():
                # if shot doesn't have localized plugins add to list to hide
                shot_list = [shot for shot in self.nuke_mngr.ani_vars.get_shot_list()
                             if not self.nuke_mngr.is_shot_localized(seq, shot)]
                self.shot_update_tree.hide_items(shot_list)
            else:
                # show all shots
                self.shot_update_tree.show_items(self.nuke_mngr.ani_vars.get_shot_list())

    def shot_localize(self):
        """
        copy plugins from the sequence lib to the shot comp dir. copies the json file too for version info. skips
        templates
        :except if there is an error copying, an error is displayed in a pop window
        """
        # filter out non plugins
        plugins = [item for item in self.seq_update_tree.get_tree_checked() if item.endswith(self.nuke_mngr.plugin_ext)]
        shots = [item for item in self.shot_update_tree.get_tree_checked() if "Shot" in item]

        missing_shots = []
        error_log = []
        for shot in shots:
            # update our vars to get the correct paths
            self.nuke_mngr.ani_vars.update(self.nuke_mngr.ani_vars.seq_name, shot)
            if not os.path.exists(self.nuke_mngr.ani_vars.shot_dir):
                missing_shots.append(shot)
            # copy the json file
            json_plugin_path = os.path.join(self.nuke_mngr.ani_vars.plugin_seq, self.nuke_mngr.plugins_json_name)
            error = pyani.core.util.copy_file(json_plugin_path, self.nuke_mngr.ani_vars.shot_comp_plugin_dir)
            if error:
                error_log.append(error)
            # copy the plugins selected
            for plugin in plugins:
                plugin_path = os.path.join(self.nuke_mngr.ani_vars.plugin_seq, plugin)
                error = pyani.core.util.copy_file(plugin_path, self.nuke_mngr.ani_vars.shot_comp_plugin_dir)
                if error:
                    error_log.append(error)
        # refresh the ui
        self.populate_shot_vers_tree()
        # report any unsuccessful copies
        if missing_shots or error_log:
            if missing_shots:
                self.msg_win.show_error_msg("Shot Error",
                                            "The shot(s) {0} do not exist on disk. Could not localize. "
                                            "Please use the 'Create shot nuke scripts' option under Sequence "
                                             "Setup to create the shots. Then localize."
                                            .format(", ".join(missing_shots)))
            if error_log:
                self.msg_win.show_error_msg("Copy Error", ", ".join(error_log))

    def shot_unlocalize(self):
        """
        removes plugins from the shot comp dir
        :except if there is an error deleting, an error is displayed in a pop window
        """
        selection_list = self.shot_update_tree.get_tree_checked()
        shot_plugins = {}
        current_shot = None
        # build a dict of shots and their plugins
        while selection_list:
            selection = selection_list.pop(0)
            if "Shot" in selection:
                shot_plugins[selection] = []
                current_shot = selection
            else:
                shot_plugins[current_shot].append(selection)

        error_log = []
        for shot, plugins in shot_plugins.items():
            # update our vars to get the correct paths
            self.nuke_mngr.ani_vars.update(self.nuke_mngr.ani_vars.seq_name, shot)
            for plugin in plugins:
                error = pyani.core.util.delete_file(os.path.join(self.nuke_mngr.ani_vars.shot_comp_plugin_dir, plugin))
                if error:
                    error_log.append(error)

        # refresh the ui
        self.populate_shot_vers_tree()


        if error_log:
            self.msg_win.show_error_msg("Delete Error", ", ".join(error_log))

    @staticmethod
    def _build_seq_vers_tree_item(item_show_path, item_seq_path, root_name, json_name):
        """
        Makes a row (including and chidlren rows) for the tree
        :param item_show_path: path to the show plugin, script, or other library item
        :param item_seq_path: path to the show plugin, script, or other library item
        :param root_name: name of the library item, such as plugins
        :param json_name: name of the json file for the library items, ex plugins.json
        :return: a dict with the tree root as a pyani.core.ui.CheckboxTreeWidgetItem and
        any children as a list of pyani.core.ui.CheckboxTreeWidgetItems
        """
        tree_child_items = []
        # check if the sequence has items - check if folder exists or its empty
        if not os.path.exists(item_seq_path) or not os.listdir(item_seq_path):
            tree_item = {"root": pyani.core.ui.CheckboxTreeWidgetItem(["No {0} Found".format(root_name)])}
        else:
            tree_item = {"root": pyani.core.ui.CheckboxTreeWidgetItem([root_name, ""])}
            # get list of files in dir, compare their json to show json for version.
            show_versions = pyani.core.util.load_json(os.path.join(item_show_path, json_name))
            seq_versions = pyani.core.util.load_json(os.path.join(item_seq_path, json_name))

            for key, value in show_versions.items():
                show_version = value["version"]
                if key in seq_versions.keys():
                    seq_version = seq_versions[key]["version"]
                else:
                    seq_version = None
                # not installed
                if not key in seq_versions.keys():
                    text = [key, "Not Installed", show_versions[key]["desc"]]
                    color = [pyani.core.ui.RED, pyani.core.ui.RED, QtCore.Qt.gray]
                    tree_child_items.append(pyani.core.ui.CheckboxTreeWidgetItem(text, color))
                # if users version is out of date color orange
                elif not show_version == seq_version:
                    # show version of seq, and version of the show in parenthesis
                    version_text = "{0}     ({1})".format(seq_version, show_versions[key]["version"])
                    text = [key, version_text, show_versions[key]["desc"]]
                    color = [pyani.core.ui.YELLOW, pyani.core.ui.YELLOW, QtCore.Qt.gray]
                    tree_child_items.append(pyani.core.ui.CheckboxTreeWidgetItem(text, color))
                # app up to date
                else:
                    text = [key, seq_version, show_versions[key]["desc"]]
                    color = [None, None, QtCore.Qt.gray]
                    tree_child_items.append(pyani.core.ui.CheckboxTreeWidgetItem(text, color))
            tree_item["children"] = tree_child_items
        return tree_item

    def _grid_auto_layout(self, widget_list, layout):
        """
        lays out a pair (label and widget) in a grid with a blank 3rd column
        :param widget_list: list of the widgets as a tuple (label, widget)
        :param layout: the grid layout
        :return: the grid layout with widgets added
        """
        # layout the widgets
        row = col = 0
        for widget in widget_list:
            label, widget = widget
            layout.addWidget(label, row, col)
            layout.addWidget(widget, row, col + 1)
            # add a third column to push widgets to the left
            layout.addItem(QtWidgets.QSpacerItem(1, 1))
            layout.setColumnMinimumWidth(2, 400)
            row += 1
        return layout