'''
# some common function for file operations
'''
import os
import sys
from pathlib import Path
import re
import binascii
import ctypes


def get_file_extension(file_path):
    path = Path(file_path)
    return path.suffix

def read_lines_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        return lines
    except FileNotFoundError:
        print("Error: File not found.")
    except PermissionError:
        print("Error: Permission denied.")
    except Exception as e:
        print("An error occurred:", str(e))

def read_asset_as_YAML_lines(path):
    bYAML = False
    with open(path, 'rb') as filehandle:
        bytes_read = filehandle.read(6)
        bYAML = bytes_read == b'%YAML '
    
    if bYAML:
        lines = read_lines_from_file(path)
        return lines
    else:
        return []

def read_text_from_file_default_encode(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        print("Error: File not found.")
    except PermissionError:
        print("Error: Permission denied.")
    except Exception as e:
        print("An error occurred:", str(e))

    return None

def read_text_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except UnicodeDecodeError:
        return read_text_from_file_default_encode(file_path)
    except FileNotFoundError:
        print("Error: File not found.")
    except PermissionError:
        print("Error: Permission denied.")
    except Exception as e:
        print("An error occurred:", str(e))
    return None

def save_lines_to_file(file_path, lines):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for line in lines:
                file.write(line)
        print("Lines saved to file successfully.")
    except Exception as e:
        print("An error occurred:", str(e))

def save_text_to_file(file_path, content):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print("Lines saved to file successfully.")
    except Exception as e:
        print("An error occurred:", str(e))

def list_files_in_folder(folder, sub_foler = "", ext = ".txt"):
    file_list = []

    if  sub_foler != None and len(sub_foler) > 0:
        folder = os.path.join(folder, sub_foler)

    for root, dirs, files in os.walk(folder):
        for file in files:
            fullPath = os.path.join(root, file)
            if fullPath.endswith(ext):
                file_list.append(fullPath)
    
    return file_list

def list_files_in_folder_with_exts(folder, sub_foler = "", exts = [".txt"]):
    file_list = []

    if  sub_foler != None and len(sub_foler) > 0:
        folder = os.path.join(folder, sub_foler)

    for root, dirs, files in os.walk(folder):
        for file in files:
            basename = os.path.basename(file)
            file_name, file_extension = os.path.splitext(basename)
            if file_extension != None and file_extension in exts:
                fullPath = os.path.join(root, file)
                file_list.append(fullPath)
    
    return file_list    

def read_meta_guid(file_path):
    if not file_path.endswith('.meta'):
        file_path = file_path + '.meta'

    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        if len(lines) > 2:
            line = lines[1]
            guid =  line[len('guid:')+1:].strip()
            return guid
        else:
            return None

def get_clean_name(path):
    basename = os.path.basename(path)
    file_name, file_extension = os.path.splitext(basename)
    pattern=r"_d\d+$"
    res = re.findall(pattern, file_name)
    bMain = True
    if len(res) > 0:
        file_name = file_name.replace(res[0], '')
        bMain = False
    return (file_name, bMain)

def group_files(files):
    group_dict = {}
    for file in files:
        name = get_clean_name(file)
        if not name in group_dict:
            group_dict[name] = []
        group_dict[name].append(file)
    return group_dict

def calculate_crc(data):
    return binascii.crc32(data.encode()) & 0xffffffff    

def calculate_crc_binary(path):
    with open(path, 'rb') as file:
        data = file.read()
        crc_value = binascii.crc32(data)
        return crc_value & 0xffffffff  

def calculate_crc_text(path, skip_index = -1):

    # read all lines
    lines = read_lines_from_file(path)

    # skip `  m_Name:` line
    if 0 <= skip_index and skip_index < len(lines):
        lines[skip_index] = ''

    crc_value = calculate_crc(''.join(lines))

    return crc_value & 0xffffffff

def custom_comparator(element):
    return element.span()[0]
    
def fix_whole_words(content, words_dict):
    bChanged = False

    for _p, word in words_dict.items():
        pattern = re.compile(_p)
        match_iter = re.finditer(pattern, content)
        if match_iter :
            match_iter = sorted(match_iter, key = custom_comparator, reverse=True)
        # print(match_iter)
        for match in match_iter:
            old_block = match.group()
            new_block = word
            (start, end) = match.span()
            content = content[:start] + new_block  + content[end: ]
            bChanged = True

    return (content, bChanged)

def set_hidden(filepath):
    FILE_ATTRIBUTE_HIDDEN = 0x02
    attrs = ctypes.windll.kernel32.GetFileAttributesW(filepath)
    if not attrs & FILE_ATTRIBUTE_HIDDEN:
        ctypes.windll.kernel32.SetFileAttributesW(filepath, attrs | FILE_ATTRIBUTE_HIDDEN)

def unset_hidden(filepath):
    FILE_ATTRIBUTE_HIDDEN = 0x02
    attrs = ctypes.windll.kernel32.GetFileAttributesW(filepath)
    if attrs & FILE_ATTRIBUTE_HIDDEN:
        ctypes.windll.kernel32.SetFileAttributesW(filepath, attrs & ~FILE_ATTRIBUTE_HIDDEN)      