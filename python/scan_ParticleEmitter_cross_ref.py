import os
import Helper.FileUtil
import Helper.UnityScene
import re


def get_config(path):
    config_dict = {}
    lines = Helper.FileUtil.read_lines_from_file(path)
    last_guid = None
    for line in lines:
        if line.startswith('#'):
            continue
        elif line.startswith('{'):
            index = line.find('=>')
            fileId = line[:index-1] + ','
            new_fileId = line[index + len('=>'):].strip()
            new_fileId = new_fileId[:-1] + ','
            config_dict[last_guid].append((fileId, new_fileId))
        else :
            last_guid = line.strip()
            config_dict[last_guid] = []

    return config_dict


def fix_PaticleEmitter_cross_ref(folder):
    ref_config = os.path.join(os.path.dirname(folder), 'ParticleEmitter_guid_ref.txt')
    config_dict = get_config(ref_config)
    if len(config_dict) == 0 :
        print('ParticleEmitter_guid_ref is EMPTY! Skip it!')
        return

    files = Helper.FileUtil.list_files_in_folder_with_exts(folder, None, ['.prefab', '.unity', '.asset'])
    for file in files:
        bChanged = False
        lines = Helper.FileUtil.read_asset_as_YAML_lines(file)
        for i in range(len(lines)):
            line = lines[i]
            index = line.find(', guid:')
            if index != -1 :
                item = line[index + len(', guid:'):].strip()
                item = item[:item.find(',')]
                if item in config_dict:
                    for (_fid, _nfid) in config_dict[item]:
                        if line.find(_fid) != -1:
                            new_line = line.replace(_fid, _nfid)
                            print( (line, new_line) )
                            lines[i] = new_line
                            bChanged = True

        if bChanged:
            Helper.FileUtil.save_lines_to_file(file, lines)

folder = r'<your_unity_project_Assets_folder_path>'
fix_PaticleEmitter_cross_ref(folder)