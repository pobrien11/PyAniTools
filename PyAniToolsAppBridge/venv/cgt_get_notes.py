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
    connection, database, error = cgt_core.login_cgt(
        ip_addr=ip_addr, username=username, password=password, database=database
    )
    if error:
        return error, None
    
    # get asset task id
    task_id_list = connection.task.get_id(
        database,
        'asset',
        [
            ['task.pipeline','=',pipeline_component],
            'and',
            ['asset.asset_name','=',asset_name]
        ]
    )

    # get note id
    note_id_list =  connection.note.get_id(
        database,
        [
            ['module','=','asset'],
            'and',
            ['module_type','=','task'],
            'and',
            ['#task_id','=',task_id_list[0]]
        ]
    )

    fields = connection.note.fields()
    # gets all notes
    notes = connection.note.get(database, note_id_list, fields)
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
        return None, note_unformatted[note_link_index:]
    else:
        return None, note_unformatted
    
def main():


    pipeline_component = sys.argv[1]
    asset_name = sys.argv[2]
    ip_addr = sys.argv[3]
    username = sys.argv[4]
    password = sys.argv[5]
    
    """
    # Testing:
    pipeline_component = "Rig"
    asset_name = "charMei"
    ip_addr = "172.18.100.246"
    username = "Patrick"
    password = "longgong19"
    """

    error, note = get_note(pipeline_component, asset_name, ip_addr=ip_addr, username=username, password=password)

    if error:
        print error
    else:
        print note

if __name__ == '__main__':
    main()