import os
import ast
import contextlib


init_file_path = os.path.abspath(
    os.path.join(os.getcwd(), '..', '__init__.py'))

copyright_id = '# Copyright (C)'


def get_bl_info():

    bl_info_string = ""
    start_found = False
    with open(init_file_path, 'r') as f:
        with contextlib.suppress(StopIteration):
            for line in f:
                if 'bl_info' in line and not start_found:
                    start_found = True
                    bl_info_string += line.split('=')[1]
                elif start_found:
                    bl_info_string += line
                    if '}' in line:
                        raise StopIteration
    return ast.literal_eval(bl_info_string)


def get_bl_info_version():
    version = list(map(str, get_bl_info()['version']))
    version = '.'.join(version)
    return version


def get_bl_info_author():
    return str(get_bl_info()['author'])


def get_bl_info_name():
    return str(get_bl_info()['name'])


def get_copyright():
    copyright = ''
    with open(init_file_path, 'r') as f:
        with contextlib.suppress(StopIteration):
            for line in f:
                if copyright_id in line:
                    copyright = line.replace(
                        copyright_id, '').lstrip(' ').rstrip('\n')
                    raise StopIteration
    return f'{copyright}'
