from typing import Union, List, Dict
import shutil
import scipy
import numpy as np
import spectral as sp
from spectral.io.bilfile import BilFile
from spectral.io.bipfile import BipFile
from spectral.io.bsqfile import BsqFile

SpyFileSubclass = Union[BilFile, BipFile, BsqFile]


def hdr_raw(cube: SpyFileSubclass) -> tuple[str, str]:
    return str(cube.filename).replace(".raw", ".hdr"), cube.filename


def str_interleave(i: int) -> str:
    if i == sp.BIL:
        return 'bil'
    elif i == sp.BIP:
        return 'bip'
    elif i == sp.BSQ:
        return 'bsq'


def copy(original: SpyFileSubclass, suffix="copy") -> SpyFileSubclass:
    """
    Creates a copy of the original SpyFile in its folder.
    :param original: the SpyFile to be copied
    :param suffix: an addition to the name of the original file.
    :return: The copy
    """
    original_hdr, original_raw = hdr_raw(original)
    new_hdr = original_hdr.replace(".hdr", f"_{suffix}.hdr")
    new_raw = original_raw.replace(".raw", f"_{suffix}.raw")
    shutil.copy2(original_hdr, new_hdr)
    shutil.copy2(original_raw, new_raw)
    return sp.io.envi.open(new_hdr, new_raw)


def zeros_like(cube: SpyFileSubclass, dtype=None) -> SpyFileSubclass:
    """
    Creates a zero-filled copy of `cube` of type `dtype`.
    :param cube: the spectral.SpyFile object.
    :param dtype: the new data type (must be a legal numpy dtype).
    :return: the new cube as a spectral.SpyFile object.
    """
    dtype_ = cube.dtype if dtype is None else dtype
    hdr_path, _ = hdr_raw(cube)
    new_hdr_path = hdr_path.replace(".hdr", "_.hdr")
    new_hdr_path = new_hdr_path.replace("__.hdr", ".hdr")
    shutil.copy2(hdr_path, new_hdr_path)
    return sp.io.envi.create_image(new_hdr_path,
                                   cube.metadata,
                                   dtype=dtype_,
                                   force=True,
                                   ext='.raw',
                                   interleave=str_interleave(cube.interleave))


def to_sparse(cube: SpyFileSubclass) -> List:
    """
    Converts a hyper-spectral cube into a sparse matrix.
    :param cube: the hyper-spectral image to be converted.
    :return: a sparse matrix in CSR format.
    """
    mem_cube = cube.open_memmap(interleave='bsq')
    sparse = []
    for k in range(cube.nbands):
        sparse.append(scipy.sparse.csr_array(mem_cube[k]))
    return sparse


def from_sparse(hdr_path: str, sparse: List, metadata: Dict) -> SpyFileSubclass:
    """
    Generates a hyper-spectral cube from a sparse matrix.
    :param hdr_path: a path to the cube's .hdr file.
    :param sparse: the sparse matrix.
    :param metadata: the cube's metadata.
    :return: a new SpyFile object of the cube.
    """
    cube = sp.io.envi.create_image(hdr_path,
                                   metadata,
                                   force=True,
                                   ext='.raw')
    cube_mem: np.memmap = cube.open_memmap(interleave='bsq', writable=True)
    for l in range(cube.nbands):
        coordinates = scipy.sparse.find(sparse[l])
        for k in range(len(coordinates[0])):
            i, j, v = coordinates[0][k], coordinates[1][k], coordinates[2][k]
            cube_mem[l][i][j] = v
    cube_mem.flush()
    return cube
