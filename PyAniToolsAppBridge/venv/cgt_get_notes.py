import sys
import ast

sys.path.append(r"c:\cgteamwork\bin\base")
sys.path.append('C:/cgteamwork/bin/cgtw')
import cgtw2
import ct

import cgt_core


def get_note(pipeline_component, asset_name, database=None, ip_addr=None, username=None, password=None):
    """
    Gets the note from CGT's note section
    :param pipeline_component: the asset component, such as Rig
    :param asset_name: name of the asset
    :param database: the CGT database to connect to
    :param ip_addr: optional ip address (no http://)
    :param username: optional username
    :param password:  optional password
    :return: error if occurred and the note as a html string (cgt stores with html)
    """
    if username == "":
        username = None
    if password == "":
        password = None

    cgt_core_obj = cgt_core.CGTCore(database=database, ip_addr=ip_addr, username=username, password=password)
    # make sure we connected
    if not cgt_core_obj.valid_connection():
        return cgt_dl.cgt_core.connection_error_msg, ""
    
    # get asset task id
    task_id_list = cgt_core_obj.connection.task.get_id(
        cgt_core_obj.database,
        'asset',
        [
            ['task.pipeline','=',pipeline_component],
            'and',
            ['asset.asset_name','=',asset_name]
        ]
    )

    # get note id
    note_id_list = cgt_core_obj.connection.note.get_id(
        cgt_core_obj.database,
        [
            ['module','=','asset'],
            'and',
            ['module_type','=','task'],
            'and',
            ['#task_id','=',task_id_list[0]]
        ]
    )

    fields = cgt_core_obj.connection.note.fields()
    # gets all notes
    notes = cgt_core_obj.connection.note.get(cgt_core_obj.database, note_id_list, fields)
    # get the latest version which is the last element in list of notes
    note_as_str = notes[-1]['text']
    # notes field returns a string, but really it should be a dict because its formatted as {"data": ..., "image": ...}
    # so convert to a dict
    note_converted_to_dict = ast.literal_eval(note_as_str)
    note_unformatted = note_converted_to_dict['data']
    # remove file link, references file on disk but we aren't opening anything.
    note_link_index = note_unformatted.find("</a>")
    if not note_link_index == -1:
        note_link_index = note_link_index + len("</a>")
        return "", note_unformatted[note_link_index:]
    else:
        return "", note_unformatted


def main():
    debug = False

    if debug:
        ip_addr = "172.18.100.246"
        username = "publish"
        password = "publish"
        pipeline_component = "Rig"
        asset_name = "charMei"
    else:
        pipeline_component = sys.argv[1]
        asset_name = sys.argv[2]
        ip_addr = sys.argv[3]
        username = sys.argv[4]
        password = sys.argv[5]

    error, note = get_note(pipeline_component, asset_name, ip_addr=ip_addr, username=username, password=password)

    if error:
        print error
    else:
        print note


if __name__ == '__main__':
    main()
