import os
import numpy as np
import spectral as sp
import zlib
import matplotlib.pyplot as plt

import diff
import fourier


def _decompose_path(path: str) -> tuple[str, str, str]:
    """
    Splits a path to a path to the lowest folder and the name of the file at the end.
    """
    name_ext = path[path.rindex('\\') + 1:]
    file_ext = name_ext[name_ext.rindex('.'):]
    file_name = name_ext[:name_ext.rindex('.')]
    folder_path = path[:path.rindex('\\' + file_name)]
    return folder_path, file_name, file_ext


def deflate(path: str, delete=False) -> str:
    with open(path, mode='rb') as raw_file:
        compressed = zlib.compress(raw_file.read())
    dfl_path = path + ".dfl"
    with open(dfl_path, mode='wb') as dfl_file:
        dfl_file.write(compressed)
    if delete:  # TODO: remove this. In the future all files will be deleted
        os.remove(path)
    print(f"\'{path}\' was successfully compressed")
    return dfl_path


def inflate(dfl_path: str) -> str:
    with open(dfl_path, mode='rb') as dfl_file:
        decompressed = zlib.decompress(dfl_file.read())
    og_path = dfl_path[:dfl_path.rindex('.')]
    print("og:", og_path)
    with open(og_path, mode='wb') as og_file:
        og_file.write(decompressed)
    os.remove(dfl_path)
    print(f"\'{dfl_path}\' was successfully decompressed")
    return og_path


HELP_STR = """
MuSIC - Multi-Spectral Image Compressor (c) Gur Elkin
-----------------------------------------------------

Command Options:

>>> compress <path> <method>
    To compress the file at the specified path.

>>> decompress <path> <method>
    To decompress the file at the specified path.

>>> delete <path>
    To delete the file at the specified path.

>>> help
    To display this menu.

>>> exit
    To exit the program.

<method> = fft | delta TODO: add more methods
"""


def menu(args):
    if len(args) < 2:
        if args[0] == 'help':
            print(HELP_STR)
            return False
        elif args[0] == 'exit':
            return True
    path = args[1]
    folder_path, file_name, file_ext = _decompose_path(path)
    sp.settings.envi_support_nonlowercase_params = True
    if args[0] == 'compress':
        cube = sp.io.envi.open(f"{folder_path}\\{file_name}.hdr", f"{folder_path}\\{file_name}.raw")
        cube_mem = cube.open_memmap(interleave='bsq').astype(np.int16)
        if len(args) < 3:
            dfl_path = deflate(cube_mem, path)
            print(f"The compressed file can be found at {dfl_path}")
        else:
            methods = args[2:]
            # TODO: complete all methods
    elif args[0] == 'decompress':
        if len(args) < 3:
            cube, ifl_path = inflate(path)
            print(f"The decompressed file can be found at {ifl_path}")
        else:
            methods = args[2:]
            # TODO: complete all methods
    elif args[0] == 'delete':
        os.remove(path)

    # TODO: anything to add here?
    return False


def main():
    stop = False
    while not stop:
        args = input("Insert a command: ").split(' ')
        stop = menu(args)


def main_1():
    sp.settings.envi_support_nonlowercase_params = True
    cube = sp.io.envi.open(r"C:\Users\gursh\hs\image.hdr", r"C:\Users\gursh\hs\image.raw")

    # fourier.dilute_bands(cube)

if __name__ == '__main__':
    main_1()
