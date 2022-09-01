import os
from typing import List
import spectral as sp
import pickle
import zlib

import diff
import fourier
import hyspec


def _decompose_path(path: str) -> tuple[str, str, str]:
    """
    Splits a path to a path to the lowest folder and the name of the file at the end.
    """
    name_ext = path[path.rindex('\\') + 1:]
    file_ext = name_ext[name_ext.rindex('.'):]
    file_name = name_ext[:name_ext.rindex('.')]
    folder_path = path[:path.rindex('\\' + file_name)]
    return folder_path, file_name, file_ext


def deflate(path: str) -> str:
    with open(path, mode='rb') as raw_file:
        compressed = zlib.compress(raw_file.read())
    dfl_path = path + ".dfl"
    with open(dfl_path, mode='wb') as dfl_file:
        dfl_file.write(compressed)
    return dfl_path


def inflate(dfl_path: str) -> str:
    with open(dfl_path, mode='rb') as dfl_file:
        decompressed = zlib.decompress(dfl_file.read())
    og_path = dfl_path[:dfl_path.rindex('.')]
    with open(og_path, mode='wb') as og_file:
        og_file.write(decompressed)
    return og_path


def delta_compress(hdr: str, raw: str) -> str:
    cube = sp.io.envi.open(hdr, raw)
    cube_delta = diff.delta(cube)
    return deflate(cube_delta.filename)


def rho_decompress(hdr: str, dfl: str) -> str:
    raw = inflate(dfl)
    cube_delta = sp.io.envi.open(hdr, raw)
    cube = diff.rho(cube_delta)
    return cube.filename


# TODO: remove extra files after decompressing
def fft_compress(hdr: str, raw: str) -> str:
    cube = sp.io.envi.open(hdr, raw)
    cube_fft = fourier.dilute_bands(cube, KEEP)
    sparse = hyspec.to_sparse(cube_fft)
    metadata = cube_fft.metadata
    sps = cube_fft.filename.replace(".raw", ".sps")
    with open(sps, mode='wb') as sps_file:
        pickle.dump((sparse, metadata), sps_file)
    return deflate(sps)


def ifft_decompress(hdr: str, dfl: str) -> str:
    sps = inflate(dfl)
    with open(sps, mode='rb') as sps_file:
        sparse, metadata = pickle.load(sps_file)
    cube_fft = hyspec.from_sparse(hdr, sparse, metadata)
    cube = fourier.reconstruct_bands(cube_fft)
    return cube.filename


KEEP = 10

HELP_STR = """
MuSIC - Multi-Spectral Image Compressor by Gur Elkin (2022)
-----------------------------------------------------------

Command Options:

>>> compress <path> using <method>
    To compress the file at <path> by the specified method.

>>> decompress <path> using <method>
    To decompress the file at <path> that was compressed by the specified method.

>>> delete <path>
    To delete the file at the specified path.

>>> help
    To display this menu.

>>> exit
    To exit the program.

<method> = fft, delta
"""


def invalid(command: List[str]) -> None:
    print(f"Invalid command: \'{' '.join(command)}\'")


def menu(args: List[str]) -> bool:
    if len(args) == 1:
        if args[0] == 'help':
            print(HELP_STR)
        elif args[0] == 'exit':
            return True
        else:
            invalid(args)
    elif len(args) == 2:
        if args[0] == 'delete':
            os.remove(args[1])
        else:
            invalid(args)
    elif len(args) == 4 and args[2] == 'using':
        if (args[0], args[3]) == ('compress', 'delta'):
            raw_path = args[1]
            new_path = delta_compress(raw_path.replace(".raw", ".hdr"), raw_path)
            print(f"The compressed file can be found at {new_path}")
        elif (args[0], args[3]) == ('decompress', 'delta'):
            dfl_path = args[1]
            new_path = rho_decompress(dfl_path.replace(".raw.dfl", ".hdr"), dfl_path)
            print(f"The decompressed file can be found at {new_path}")
        elif (args[0], args[3]) == ('compress', 'fft'):
            raw_path = args[1]
            new_path = fft_compress(raw_path.replace(".raw", ".hdr"), raw_path)
            print(f"The compressed file can be found at {new_path}")
        elif (args[0], args[3]) == ('decompress', 'fft'):
            dfl_path = args[1]
            new_path = ifft_decompress(dfl_path.replace(".sps.dfl", ".hdr"), dfl_path)
            print(f"The decompressed file can be found at {new_path}")
        else:
            invalid(args)
    else:
        invalid(args)
    return False


def main():
    sp.settings.envi_support_nonlowercase_params = True
    stop = False
    while not stop:
        args = input("Insert a command: ").split(' ')
        stop = menu(args)


if __name__ == '__main__':
    main()

