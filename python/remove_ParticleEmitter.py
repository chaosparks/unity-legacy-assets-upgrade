import os
import Helper.FileUtil
import Helper.UnityScene
import re

def do_remove(lines):
    bChanged = False

    new_lines = []
    fileID_Dict = {}
    bRemove = False
    for line in lines:       
        if line.startswith('--- !u!15 ') or line.startswith('--- !u!12 ') or line.startswith('--- !u!26 '):
            _id = line[line.find('&')+1:].strip()
            _key = '{fileID: ' + _id + '}'
            fileID_Dict[_key] = _id
            bRemove = True
            bChanged = True
        elif line.startswith('--- '):
            bRemove = False

        if not bRemove:
            new_lines.append(line)
        
    lines = new_lines
    new_lines = []
    for line in lines:
        bFound = False
        if line.find('{fileID:') != -1:
            for (_k, _v) in fileID_Dict.items():
                if line.find(_k) != -1:
                    bFound = True
                    bChanged = True
                    break
        if not bFound:
            new_lines.append(line)

    return bChanged, new_lines
    

def do_remove_legacy_ParticleEmitter(folder):
    files = Helper.FileUtil.list_files_in_folder_with_exts(folder, None, ['.prefab', '.unity', '.asset'])
    for file  in files:
        lines = Helper.FileUtil.read_asset_as_YAML_lines(file)
        bChanged, new_lines = do_remove(lines)
        if bChanged:
            Helper.FileUtil.save_lines_to_file(file, new_lines)

folder = r'<your_unity_project_Assets_folder_path>'       
do_remove_legacy_ParticleEmitter(folder) 