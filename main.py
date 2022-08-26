import os
import numpy as np
import spectral as sp
import pickle
import zlib
import matplotlib.pyplot as plt
import wx
import OpenGL

import diff
import fourier


def _decompose_path(path: str) -> tuple[str, str]:
    """
    Splits a path to a path to the lowest folder and the name of the file at the end.
    """
    name_ext = path[path.rindex('\\') + 1:]
    file_name = name_ext[:name_ext.rindex('.')]
    folder_path = path[:path.rindex('\\' + file_name)]
    return folder_path, file_name


def compress(obj: object, path: str) -> str:
    """
    Deflates an python object.
    :param obj: the object to be deflated.
    :param path: a path to a file in the folder that will contain the deflated object, with its designated name.
    :return: a path to the '.dfl' file containing the deflated object.
    """
    folder_path, file_name = _decompose_path(path)
    file_path = f"{folder_path}\\{file_name}.dfl"
    with open(file_path, mode='w+b') as dfl_file:
        pickle.dump(obj, dfl_file, protocol=5)
    with open(file_path, mode='r+b') as dfl_file:
        buffer = dfl_file.read()
    comp_buffer = zlib.compress(buffer)
    with open(file_path, mode='w+b') as dfl_file:
        dfl_file.seek(0)
        dfl_file.truncate()
        dfl_file.write(comp_buffer)
    print(
        f"\"{file_name}\" file was successfully compressed to ~{str(len(comp_buffer) / len(buffer) * 100)[:5]}% its original size")
    return file_path


def decompress(dfl_path: str) -> object:
    """
    Inflates a deflated object
    :param dfl_path: The path to the '.dfl' file containing the deflated object.
    :return: an identical copy of the deflated object and a path to its '.ifl' file.
    """
    with open(dfl_path, mode='r+b') as dfl_file:
        comp_buffer = dfl_file.read()
    buffer = zlib.decompress(comp_buffer)
    folder_path, file_name = _decompose_path(dfl_path)
    ifl_path = f"{folder_path}\\{file_name}.ifl"
    with open(ifl_path, mode='w+b') as ifl_file:
        ifl_file.write(buffer)
    with open(ifl_path, mode='r+b') as ifl_file:
        obj = pickle.load(ifl_file)
    print(f"\"{file_name}\" file was successfully decompressed")
    return obj, ifl_path


HELP_STR = """
MuSIC - Multi-Spectral Image Compressor (c) Gur Elkin
-----------------------------------------------------

Command Options:

>>> compress <path> <method>*
    To compress the file at the specified path.

>>> decompress <path> <method>*
    To decompress the file at the specified path.

>>> delete <path>
    To delete the file at the specified path.

>>> help
    To display this menu.

>>> exit
    To exit the program.

<method> = dfft | TODO: add more methods
"""


def menu(args):
    if len(args) < 2:
        if args[0] == 'help':
            print(HELP_STR)
            return False
        elif args[0] == 'exit':
            return True
    path = args[1]
    folder_path, file_name = _decompose_path(path)
    if args[0] == 'compress':
        sp.settings.envi_support_nonlowercase_params = True
        cube = sp.io.envi.open(f"{folder_path}\\{file_name}.hdr", f"{folder_path}\\{file_name}.raw")
        cube_mem = cube.open_memmap(interleave='bsq').astype(np.int16)
        if len(args) < 3:
            dfl_path = compress(cube_mem, path)
            print(f"The compressed file can be found at {dfl_path}")
        else:
            methods = args[2:]
            # TODO: complete all methods
    elif args[0] == 'decompress':
        if len(args) < 3:
            cube, ifl_path = decompress(path)
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



def count_zroes(arr):
    zero_counter = 0
    for index, value in np.ndenumerate(arr):
        if value == 0:
            zero_counter += 1
    return zero_counter

def main_1():
    c = 0
    def pc(counter):
        print(f"({counter})")
        counter += 1

    sp.settings.envi_support_nonlowercase_params = True
    pc(c)
    cube = sp.io.envi.open("C:\\Users\\gursh\\hs\\image.hdr", "C:\\Users\\gursh\\hs\\image.raw")
    pc(c)
    cube_d = diff.delta(cube)
    pc(c)
    cube_mem = cube_d.open_memmap(interleave='bsq').astype(np.int16)
    pc(c)
    compress(cube_mem, cube_d.filename)

    # print("(1)")
    # diluted_cube = fourier.dilute_bands(cube, 10)
    # print("(2)")
    # dcm = diluted_cube.open_memmap(interleave='bsq').astype(np.int16)
    # print("(3)")
    # print("~~~", count_zroes(dcm[50]))
    # compress(dcm, r"C:\Users\gursh\hs\image_copy.raw")
    # print("(4)")
    # # plt.imshow(dcm[50])
    # # plt.show()



    # image = plt.imread("C:\\Users\\gursh\\hs\\river.jpg", format='jpeg')
    # m, n = image.shape
    # f_image = np.zeros_like(image, dtype='complex')
    # for i in range(m):
    #     f_image[i] = fourier.dilute(image[i], 10)
    # # f_image = fourier.dilute(image, 10)
    # print(count_zroes(f_image))
    # f_image_inv = np.zeros_like(image)
    # for i in range(m):
    #     f_image_inv[i] = fourier.inverse(f_image[i])
    # plt.imshow(fourier.inverse(f_image_inv), cmap='gray', vmin=0, vmax=255)
    # plt.show()


if __name__ == '__main__':
    main_1()
