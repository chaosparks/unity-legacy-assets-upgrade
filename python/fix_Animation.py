import os
import Helper.FileUtil
import Helper.UnityScene
import re

# check the animation clip is legacy or not ?
# Animation will using legacy animation clip, but AnimatorController will not!
def is_Legacy(file):
    lines = Helper.FileUtil.read_lines_from_file(file)
    bLegacy = False
    for line in lines:
        if line.startswith('  m_Legacy:'):
            if line.find('1') != -1:
                bLegacy = True
            break
    return bLegacy

# scan and get all animation clip information: file path, guid, is legacy or not?
def scal_all_animation_clip(folder):
    files = Helper.FileUtil.list_files_in_folder(folder, None, '.anim')
    guid_file_dict = {}
    for file in files:
        guid = Helper.FileUtil.read_meta_guid(file + '.meta')
        bLegacy = is_Legacy(file)
        guid_file_dict[guid] = (file, bLegacy)
    return guid_file_dict

# extract guid value from `{fileID: 12121, guid: xxxx, type: 3}`
def pure_guid_from(line):
    index = line.find('guid:')
    if index < 0:
        return None
    item = line[index+len('guid:'):]
    item = item[:item.find(',')].strip()
    return item

# scan all animation clips which used by animator controllers
# Animater Controller will use NOT LEGACY animation clip
def scan_all_controller(folder):
    files = Helper.FileUtil.list_files_in_folder(folder, None, '.controller')
    controller_ref_dict = {}
    for file in files:
        lines = Helper.FileUtil.read_lines_from_file(file)
        bAnimatorState = False
        Name = ''
        controller_ref_dict[file] = []
        for line in lines:
            if line.startswith('--- '):
                bAnimatorState = False
                Name = ''
                continue
            elif line.startswith('AnimatorState:'):
                bAnimatorState = True
                continue
            elif bAnimatorState and line.startswith('  m_Name:'):
                Name = line.strip()[len('m_Name:'):].strip()
            else:
                if line.find('{fileID: 7400000,') != -1:
                    Motion = pure_guid_from(line)
                    controller_ref_dict[file].append((Name, Motion))

    return controller_ref_dict


def scan_legacy_animation_clip(folder):
    files = Helper.FileUtil.list_files_in_folder(folder, None, '.anim')
    for file in files:
        bChanged = False
        lines = Helper.FileUtil.read_lines_from_file(file)
        bFound = False
        for i in range(len(lines)):
            line = lines[i]
            start = line.find('m_Legacy: 1')
            if start != -1:
                bFound = True
                break

        if not bFound:
            print('NOT mark as Legacy: ' + file)

# Scan all Animation Component in unity assets
# Animation component will using LEGACY animation clip
# NOTE: some animation clips will be loaded by code, those may not be included it's Animation
def scan_animation_clips_in_Animation(folder):
    files = Helper.FileUtil.list_files_in_folder_with_exts(folder, None, ['.prefab', '.unity', '.asset'])
    used_animation_clips = {}
    for file in files:
        lines = Helper.FileUtil.read_asset_as_YAML_lines(file)
        bAnimation = False
        for line in lines:
            if line.startswith('--- '):
                bAnimation = False
                continue
            elif line.startswith('Animation:'):
                bAnimation = True
                continue
            elif bAnimation and line.startswith('  - {fileID: 7400000,'):
                item = pure_guid_from(line)
                used_animation_clips[item] = item

    return used_animation_clips


# Combine all the logic into one function
def scan_all_animation_clip(folder):

    # first, scan all animtion clip list
    guid_file_dict = scal_all_animation_clip(folder)

    # filter out that used by AnimaterController!
    controller_ref_dict = scan_all_controller(folder)
    used_in_controller = {}
    subLen = len(folder) - 6
    for (path, items) in controller_ref_dict.items():
        for (name, guid) in items:
            # motion - animation clip exist ?
            if guid:
                if guid in guid_file_dict:
                    used_in_controller[guid] = guid_file_dict[guid]
                    (file, bLegacy) = guid_file_dict[guid]
                    if bLegacy:
                        print('Mark NOT Legacy for: ' + str((bLegacy, file[subLen:], path[subLen:])))
                else:
                    print('can not find: ' + guid)

    # filter out that used by Animation Component
    used_animation_clips = scan_animation_clips_in_Animation(folder)
    for (_guid, _) in used_animation_clips.items():
        # print(_guid)
        if not _guid in guid_file_dict:
            print('can not find: ' + _guid )
            continue
        else :
            (path, bLegacy) = guid_file_dict[_guid]
            used_in_controller[_guid] = path
            if not bLegacy:
                print('Mask Legacy for: ' + path)

    # NOT used in Animater or Animation !
    # Need to take further step to make sure where those animation clips will be used!
    print('Unknown Legacy Mask Animation clips, please check it by hand:')
    for (guid, path) in guid_file_dict.items():
        if not guid in used_in_controller:
            print( (guid, path) )


folder = r'<your_unity_project_Assets_folder_path>'

# scan_legacy_animation_clip(folder)            

scan_all_animation_clip(folder)