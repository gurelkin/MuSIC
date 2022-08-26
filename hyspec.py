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
    return 'bsq'


def copy(original: SpyFileSubclass) -> SpyFileSubclass:
    """
    Creates a copy of the original SpyFile in its folder.
    :param original: the SpyFile to be copied
    :return: The copy
    """
    original_hdr = hdr(original)
    new_hdr = original_hdr.replace(".hdr", "_copy.hdr")
    shutil.copyfile(original_hdr, new_hdr)
    return sp.io.envi.create_image(new_hdr,
                                   metadata=original.metadata,
                                   dtype='unit16',
                                   ext='.raw',
                                   interleave=str_interleave(original.interleave))

