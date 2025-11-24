import os
import sys

class UnitySceneParser:
    Gameobjects = {}
    Transforms = {}
    MeshRenderers = {}
    SkinnedMeshRenderers = {}
    MonoBehaviours = {}

    def __init__(self):
        pass 

    def parse_fileID(self, line):
        s = line[ line.find('fileID:') + len('fileID:') :]
        s = s.replace('}','').strip()
        return int(s)

    def parse_id(self, line):
        s = line[line.find('&')+1:].strip()
        id = int(s)
        return id

    def parse_Gameobject(self, lines, k):
        line = lines[k]
        id = self.parse_id(line)

        block_lines = []
        block_lines.append(line)
        for i in range(k+1, len(lines)):
            line = lines[i]
            if line.startswith('--- '):
                break
            else:
                block_lines.append(line)

        component = []

        for j in range(1, len(block_lines)):
            line = block_lines[j]
            if line.startswith('  - component:'):
                fileID = self.parse_fileID(line)
                component.append(fileID)
            elif line.startswith('  m_Name:'):
                name = line[len('  m_Name: '):].strip()

        # print('id = ' + str(id) + ', name = ' + name + ', transform = ' + str(component[0]))

        self.Gameobjects[id] = {
            'id': id,
            'component': component,
            'name': name,
            'lines': block_lines
        }

        return i

    def parse_Transform(self, lines, k):
        line = lines[k]
        id = self.parse_id(line)

        block_lines = []
        block_lines.append(line)
        for i in range(k+1, len(lines)):
            line = lines[i]
            if line.startswith('--- '):
                break
            else:
                block_lines.append(line)

        Children = []
        Father = 0
        GameObject = 0
        for j in range(1, len(block_lines)):
            line = block_lines[j]
            if line.startswith('  - {fileID:'):
                fileID = self.parse_fileID(line)
                Children.append(fileID)
            elif line.startswith('  m_Father:'):
                Father = self.parse_fileID(line)
            elif line.startswith('  m_GameObject:'):
                GameObject = self.parse_fileID(line)

        # print('id = ' + str(id) + ', Father = ' + str(Father) )

        self.Transforms[id] = {
            'id': id,
            'Children': Children,
            'Father': Father,
            'GameObject': GameObject,
            'lines': block_lines
        }

        return i

    def parse_MeshRenderer(self, lines, k):
        line = lines[k]
        id = self.parse_id(line)

        block_lines = []
        block_lines.append(line)
        for i in range(k+1, len(lines)):
            line = lines[i]
            if line.startswith('--- '):
                break
            else:
                block_lines.append(line)

        GameObject = 0
        Materials = []
        for j in range(1, len(block_lines)):
            line = block_lines[j]
            if line.startswith('  m_GameObject:'):
                GameObject = self.parse_fileID(line)
            elif line.startswith('  - {fileID: 18500000,'):
                s = line[line.find('{'):].strip()
                Materials.append(s)

        # print('id = ' + str(id) + ', GameObject = ' + str(GameObject) )

        self.MeshRenderers[id] = {
            'id': id,
            'GameObject': GameObject,
            'lines': block_lines,
            'Materials': Materials
        }

        return i

    def parse_MonoBehaviour(self, lines, k):
        line = lines[k]
        id = self.parse_id(line)

        block_lines = []
        block_lines.append(line)
        for i in range(k+1, len(lines)):
            line = lines[i]
            if line.startswith('--- '):
                break
            else:
                block_lines.append(line)

        GameObject = 0
        Script = None
        for j in range(1, len(block_lines)):
            line = block_lines[j]
            if line.startswith('  m_GameObject:'):
                GameObject = self.parse_fileID(line)
            elif line.startswith('  m_Script:'):
                s = line[line.find('{'):].strip()
                Script = s

        # print('id = ' + str(id) + ', GameObject = ' + str(GameObject) )

        self.MonoBehaviours[id] = {
            'id': id,
            'GameObject': GameObject,
            'lines': block_lines,
            'Script': Script
        }

        return i

    def get_gameobject_name(self, id):
        name = self.Gameobjects[id]['name']
        if name.startswith('"'):
            name = name[1:]
        if name.endswith('"'):
            name = name[:-1]
        return name

    def get_parent_gameobject_name(self, gid):
        go = self.Gameobjects[gid]
        tid = go['component'][0]
        pid = self.Transforms[tid]['Father']
        pgid = self.Transforms[pid]['GameObject']
        return self.get_gameobject_name(pgid)

    def parse_unity_scene(self, lines):
        self.Gameobjects.clear()
        self.Transforms.clear()
        self.MeshRenderers.clear()
        self.SkinnedMeshRenderers.clear()

        next_i = 0
        for i in range(len(lines)):

            if i < next_i:
                continue

            line = lines[i]

            if line.startswith('--- !u!1 '):
                next_i = self.parse_Gameobject(lines, i)
            elif line.startswith('--- !u!4 '):
                next_i = self.parse_Transform(lines, i)
            elif line.startswith('--- !u!23 '):
                next_i = self.parse_MeshRenderer(lines, i)
            elif line.startswith('--- !u!137 '):
                next_i = self.parse_MeshRenderer(lines, i)
            elif line.startswith('--- !u!114 '):
                next_i = self.parse_MonoBehaviour(lines, i)

    def print_info(self):
        print('GameObject count = ' + str(len(self.Gameobjects)))
        print('Transforms count = ' + str(len(self.Transforms)))
        print('MonoBehaviours count = ' + str(len(self.MonoBehaviours)))

    def get_MonoBehaviour_Info(self):

        gameobjects = {}

        for (_id, _param) in self.MonoBehaviours.items():
            gid = _param['GameObject']

            if not gid in gameobjects:
                gameobjects[gid] = []

            gameobjects[gid].append(_id)
            # print((_id, gid, _param['Script']))

        print( len(gameobjects) )

        mappings = []

        for i in range(3):
            remove_mids = []
            print('====> ' + str(i))
            for (_gid, _mids) in gameobjects.items():
                if len(_mids) == 1:
                    mid = _mids[0]
                    gname = self.Gameobjects[_gid]['name']
                    script = self.MonoBehaviours[mid]['Script']
                    print( (gname, script) )
                    mappings.append((gname, script))

                    if not mid in remove_mids:
                        remove_mids.append(mid)

            for mid in remove_mids:
                for gid in gameobjects.keys():
                    
                    # 
                    if mid in gameobjects[gid]:
                        gameobjects[gid].remove(mid)
                        continue
                    
                    new_mids = []
                    for g_mid in gameobjects[gid]:
                        if self.MonoBehaviours[mid]['Script'] == self.MonoBehaviours[g_mid]['Script']:
                            pass
                        else :
                            new_mids.append(g_mid)

                    gameobjects[gid] = new_mids

        
        print(len(mappings))
        if len(gameobjects) == len(mappings):
            print('All found!')

        for (_k, _v) in mappings:
            print( _k + '=>' + _v )

        return mappings
