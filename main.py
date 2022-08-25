import os
import spectral
import pickle
import zlib


def _decompose_path(path: str) -> tuple[str, str]:
    name_ext = path[path.rindex('\\') + 1:]
    file_name = name_ext[:name_ext.rindex('.')]
    folder_path = path[:path.rindex('\\' + file_name)]
    return folder_path, file_name


def compress(obj: object, path: str) -> str:
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
        spectral.settings.envi_support_nonlowercase_params = True
        cube = spectral.io.envi.open(f"{folder_path}\\{file_name}.hdr", f"{folder_path}\\{file_name}.raw")
        cube_mem = cube.open_memmap(interleave='bsq')
        if len(args) < 3:
            dfl_path = compress(cube_mem, path)
            print(f"The compressed file can be found at {dfl_path}")
        else:
            methods = args[2:]
            # TODO: complete all methods
    elif args[0] == 'decompress':
        if len(args) < 3:
            cube, ifl_path = decompress(path)
            print(f"The deompressed file can be found at {ifl_path}")
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
        args = input("Inset a command:\n").split(' ')
        stop = menu(args)


if __name__ == '__main__':
    main()
