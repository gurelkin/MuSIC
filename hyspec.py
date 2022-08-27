from typing import Union
import shutil
import spectral as sp
from spectral.io.bilfile import BilFile
from spectral.io.bipfile import BipFile
from spectral.io.bsqfile import BsqFile

SpyFileSubclass = Union[BilFile, BipFile, BsqFile]


def hdr_raw(image: SpyFileSubclass) -> tuple[str, str]:
    return str(image.filename).replace(".raw", ".hdr"), image.filename


def str_interleave(i: int) -> str:
    if i == sp.BIL:
        return 'bil'
    if i == sp.BIP:
        return 'bip'
    if i == sp.BSQ:
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
