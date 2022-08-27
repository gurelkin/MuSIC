from typing import Union
import shutil

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
    shutil.copy(original_hdr, new_hdr)
    shutil.copy(original_raw, new_raw)
    return sp.io.envi.open(new_hdr, new_raw)


def change_dtype(cube: SpyFileSubclass, dtype: np.dtype) -> SpyFileSubclass:
    hdr_path, _ = hdr_raw(cube)
    return sp.io.envi.create_image(hdr_path,
                                   cube.metadata,
                                   dtype=dtype,
                                   force=True,
                                   ext='.raw',
                                   interleave=str_interleave(cube.interleave))
