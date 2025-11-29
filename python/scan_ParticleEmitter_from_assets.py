import os
import Helper.FileUtil
import Helper.UnityScene
import re

'''
# After you do ParticleEmitter -> ParticleSystem, and code fix for replacement.
# You need to replace the component reference. Switch the pointer to the new one.
# Notice, some other prefabs or level will point ones that not in the same physical file.
'''

def has_ParticleEmitter(lines):
    for line in lines:
        if line.startswith('EllipsoidParticleEmitter:'):
            return True
        elif line.strip().endswith('ParticleEmitter:'):
            return True
    return False

def parse_fileID(line):
    item = line[line.find('&')+1:].strip()
    return item

def parse_GameObjectID(line):
    item = line[line.find(':')+1:].strip()
    return item    

def scan_ParticleEmitter(lines):

    gameobject_pe = {}
    gameobject_ps = {}

    for i in range(len(lines)):
        curr_line = lines[i]
        if curr_line.startswith('EllipsoidParticleEmitter:') :
            _id = parse_fileID(lines[i-1])
            _obj = parse_GameObjectID(lines[i+4])
            gameobject_pe[_obj] = _id
        elif curr_line.startswith('ParticleSystem:'):
            _id = parse_fileID(lines[i-1])
            _obj = parse_GameObjectID(lines[i+4])
            gameobject_ps[_obj] = _id

    bChanged = False
    pe_2_ps = {}
    for (_obj, _id) in gameobject_pe.items():
        pe_2_ps['{fileID: '+ _id + '}'] = '{fileID: '+ gameobject_ps[_obj ] + '}'

    bGameObject = False
    for i in range(len(lines)):
        line = lines[i]
        
        if line.startswith('--- !u!1 '):
            bGameObject = True
            continue
        elif line.startswith('--- '):
            bGameObject = False
            continue

        if bGameObject:
            continue

        index = line.find('{fileID:')
        if index != -1:
            old_id = line[index:line.rfind('}')+1]
            if old_id in pe_2_ps:
               new_id = pe_2_ps[old_id]
               new_line = line.replace(old_id, new_id)
               print( (line, new_line) )
               lines[i] = new_line
               bChanged = True

    return pe_2_ps, bChanged

def scan_ParticleEmitter_only(folder):
    files = Helper.FileUtil.list_files_in_folder_with_exts(folder, None, ['.prefab', '.unity', '.asset'])
    for file in files:
        lines = Helper.FileUtil.read_asset_as_YAML_lines(file)
        bParticleEmitter = has_ParticleEmitter(lines)
        if bParticleEmitter:
            print('scan file: ' + file)



def scan_ParticleEmitter_try_fix(folder):
    files = Helper.FileUtil.list_files_in_folder_with_exts(folder, None, ['.prefab', '.unity', '.asset'])
    pt_usage = {}
    unique_particles = {}
    log_lines = []
    cross_ref = {}
    for file in files:
        lines = Helper.FileUtil.read_asset_as_YAML_lines(file)
        bParticleEmitter = has_ParticleEmitter(lines)
        if bParticleEmitter:
            # do inner file component reference fix, and log the old => new mapping
            pe_2_ps, bChanged = scan_ParticleEmitter(lines)
            if bChanged:
                Helper.FileUtil.save_lines_to_file(file, lines)

            guid = Helper.FileUtil.read_meta_guid(file + '.meta')
            
            cross_ref[guid] = []

            log_lines.append('# ' + file + '\n')
            log_lines.append('' + guid + '\n')
            for (_k, _v) in pe_2_ps.items():
                log_lines.append(_k + '=>' + _v + '\n')
                cross_ref[guid].append((_k, _v))

    # save the old=>new mapping log, we will use it to fix reference among files
    config = os.path.join(os.path.dirname(folder), 'ParticleEmitter_guid_ref.txt')
    Helper.FileUtil.save_lines_to_file(config, log_lines)

    # handle cross reference
    for file in files:
        bChanged = False
        lines = Helper.FileUtil.read_asset_as_YAML_lines(file)
        for i in range(len(lines)):
            line = lines[i]
            index = line.find(', guid:')
            if index != -1 :
                item = line[index + len(', guid:'):].strip()
                item = item[:item.find(',')]
                if item in cross_ref:
                    for (_fid, _nfid) in cross_ref[item]:
                        if line.find(_fid) != -1:
                            new_line = line.replace(_fid, _nfid)
                            print( (line, new_line) )
                            lines[i] = new_line
                            bChanged = True

        if bChanged:
            Helper.FileUtil.save_lines_to_file(file, lines)    

folder = r'<your_unity_project_Assets_folder_path>'
# scan_ParticleEmitter_try_fix(folder)

scan_ParticleEmitter_only(folder)