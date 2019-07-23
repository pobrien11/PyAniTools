import sys

sys.path.append('C:\\PyAniTools\\lib')


sys.path.append(r"c:\cgteamwork\bin\base")
sys.path.append('C:/cgteamwork/bin/cgtw')
import cgtw2
import ct

import cgt_core


def update_sequence_shot_list(json_path, database=None, ip_addr=None, username=None, password=None):
    """
    Updates sequences.json in app_data/Shared. Format is:
        sequence name: [
            {
                shot,
                first frame,
                last frame
            },
            ....
        ]
        ....

        example:
       "Seq170": [
          {
             "Shot": "Shot010",
             "first_frame": 1001,
             "last_frame": 1114
          },
          more shots...
        ]
    :return: error if encountered, otherwise None
    """
    t_tw, t_db, error = cgt_core.login_cgt(ip_addr=ip_addr, username=username, password=password, database=database)
    if error:
        return error
    
    seq_shot_frames = {}
    # get sequences, shots, and frame ranges
    try:
        sequences = get_seq_list(t_tw, t_db)
        for sequence in sequences:
            seq_shot_frames[sequence] = []
    except Exception as e:
        error = "Error getting sequence list from CG Teamworks. Error is {0}".format(e)
        return error
    try:
        for sequence in sequences:
            shots = get_shot_list(sequence, t_tw, t_db)
            shot_frames = get_shot_frames(sequence, t_tw, t_db)
            for shot in shots:
                first_frame = shot_frames[shot]["first_frame"]
                last_frame = shot_frames[shot]["last_frame"]
                seq_shot_frames[sequence].append(
                    {
                        "shot": shot,
                        "first_frame": first_frame,
                        "last_frame": last_frame
                    }
                )
    except Exception as e:
        error = "Error getting shot and frame list from CG Teamworks. Error is {0}".format(e)
        return error
    # write to json and return response
    return cgt_core.write_json(json_path, seq_shot_frames, indent=4)


def get_seq_list(t_tw, t_db):
    """
    Access CG teamworks program to get a list of sequences, filters out non production sequences. Only sequences
    that have seq#### are added
    :param t_tw: the connection to cgt
    :param t_db: the database name
    :return: a list of the sequences
    """
    temp = []
    t_id_list = t_tw.info.get_id(t_db, 'eps', [["eps.eps_name", "has", "%"]])
    t_data = t_tw.info.get(t_db, "eps", t_id_list, ['eps.eps_name'])
    for i in t_data:
        if "seq" in i["eps.eps_name"].lower():
            temp.append(i["eps.eps_name"])
    return temp


def get_shot_list(sequence, t_tw, t_db):
    """
    Access CG teamworks program to get a list of shots for a given sequence
    :param sequence: sequence name
        ex: "seq001"
    :param t_tw: the connection to cgt
    :param t_db: the database name
    :return: a list of shots
    """
    temp = []
    t_id_list = t_tw.info.get_id(t_db, 'shot', [["eps.eps_name", "=", sequence]])
    t_data = t_tw.info.get(t_db, 'shot', t_id_list, ['shot.shot'])
    for i in t_data:
        temp.append(i["shot.shot"])
    return temp


def get_shot_frames(sequence, t_tw, t_db):
    """
    Access CG teamworks program to get a dict of first and last frames for every shot in a given sequence
    :param sequence: sequence name
        ex: "seq001"
    :param t_tw: the connection to cgt
    :param t_db: the database name
    :return: a dict of shots and their frames

    ep: {
         u'shot001': {'last_frame': u'1020', 'frame': u'5', 'first_frame': u'1001'},
         u's002': {'last_frame': u'1056', 'frame': u'2', 'first_frame': u'1001'}
         }
    """
    temp = {}
    t_id_list = t_tw.info.get_id(t_db, 'shot', [["eps.eps_name", "=", sequence]])
    t_data = t_tw.info.get(t_db, 'shot', t_id_list,
                                ['shot.shot', 'shot.frame', 'shot.first_frame', 'shot.last_frame'])
    for i in t_data:
        te = {}
        te['frame'] = i["shot.frame"]
        te['first_frame'] = i["shot.first_frame"]
        te['last_frame'] = i["shot.last_frame"]
        temp[i['shot.shot']] = te

    return temp

def main():
    json_path = sys.argv[1]
    ip_addr = sys.argv[2]
    username = sys.argv[3]
    password = sys.argv[4]
    error = update_sequence_shot_list(json_path, ip_addr=ip_addr, username=username, password=password)
    print error
    if error:
        print error
    else:
        print ""

if __name__ == '__main__':
    main()
