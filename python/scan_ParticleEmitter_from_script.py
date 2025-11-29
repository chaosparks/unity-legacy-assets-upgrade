import os
import Helper.FileUtil
import Helper.UnityScene
import re

'''
# step 1
# find all C# code that use ParticleEmitter component, and those C# script will be bind to some game object.
# This means those script file are used in project. We MUST fix it while upgrading project!
'''

def find_constant_strings_in_csharp(filepath):
    pattern = r'\bParticleEmitter\b'
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            matches = re.findall(pattern, content)
            return matches
    except UnicodeDecodeError:
        print('Load Error: ' + filepath)
    return None

def get_class_name(path):
    basename = os.path.basename(path)
    file_name, file_extension = os.path.splitext(basename)
    return file_name

def get_baseclass(filepath):
    class_name = get_class_name(filepath)
    pattern = r'\b'+ class_name + '\s:\s[A-Za-z0-9_]+'
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()            
            matches = re.findall(pattern, content)            
            return matches
    except UnicodeDecodeError:
        print('Load Error: ' + filepath)
    return None

def get_class_info(path, class_name):
    content = Helper.FileUtil.read_text_from_file(path)
    if not content:
        return None

    pattern = r'\bParticleEmitter\b'
    matches = re.findall(pattern, content)
    bParticleEmitter = False
    if matches and len(matches) > 0:
        bParticleEmitter = True

    pattern = r'\b'+ class_name + '\s:\s[A-Za-z0-9_]+'
    matches = re.findall(pattern, content)
    base_name = None
    if matches and len(matches) > 0:
        base_name = matches[0]
        base_name = base_name[base_name.find(':')+1:].strip()

    guid = Helper.FileUtil.read_meta_guid(path + '.meta')
    result = (bParticleEmitter, class_name, base_name, guid, path)
    return result

def get_base_class(_dict, _basename):
    for (_key, _value) in _dict.items():
        (bUsingGUITexture, class_name, base_name, guid, path) = _value
        if _basename == class_name :
            if bUsingGUITexture :
                return True
            elif base_name:
                return get_base_class(_dict, base_name)
            else :
                return False

def scan_ParticleEmitter_from_script(folder):
    # 第一步，先找出所有使用或者包含 ParticleEmitter 组件的类
    files = Helper.FileUtil.list_files_in_folder(folder, None, '.cs')
    scripts_dict = {}
    for file in files:
        class_name = get_class_name(file)
        class_info = get_class_info(file, class_name)
        if class_info:
            scripts_dict[file] = class_info
        else :
            print('Error in: ' + file)

    for (_key, _value) in scripts_dict.items():
        (bParticleEmitter, class_name, base_name, guid, path) = _value
        if not bParticleEmitter and base_name:
            bUsing = get_base_class(scripts_dict, base_name)
            if bUsing:
                scripts_dict[_key] = (bUsing, class_name, base_name, guid, path) 

    guids = {}
    for (_key, _value) in scripts_dict.items():
        (bParticleEmitter, class_name, base_name, guid, path) = _value
        if bParticleEmitter:
            guids[guid] = path


    files = Helper.FileUtil.list_files_in_folder_with_exts(folder, None, ['.prefab', '.unity', '.asset'])
    guid_usage = {}
    for file in files:
        lines = Helper.FileUtil.read_asset_as_YAML_lines(file)
        for line in lines:
            index = line.find('{fileID: 11500000, guid: ')
            if index != -1:
                new_line = line[index + len('{fileID: 11500000, guid: '):].strip()
                guid = new_line[:new_line.find(',')]
                if guid in guids:
                    if not guid in guid_usage:
                        guid_usage[guid] = []
                    
                    if not file in guid_usage[guid]:
                        guid_usage[guid].append(file)

    lines = []

    for (_, file) in guids.items():
        lines.append(file + '\n')

    lines.append('\n')

    # 资源中直接引用的脚本
    lines.append('used script files: \n')
    for (_guid, _files) in guid_usage.items():
        script_file = guids[_guid]
        lines.append('=> ' + script_file + '\n')
        print('=> ' + script_file)
        for file in _files:
            print('    ' + file)
            lines.append('    ' + file + '\n')

    config = os.path.join(os.path.dirname(folder), 'ParticleEmitter_ref.txt')
    Helper.FileUtil.save_lines_to_file(config, lines)

folder = r'<your_unity_project_Assets_folder_path>'
scan_ParticleEmitter_from_script(folder)

