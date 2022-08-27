import numpy
import numpy as np
import spectral as sp
import hyspec


def delta(cube: hyspec.SpyFileSubclass, new=True) -> hyspec.SpyFileSubclass:
    """
    :param cube: the hyper-spectral image (spectral.SpyFile).
    :param new: whether to create a new file for delta(cube).
    :return: a new hyper-spectral image where every band holds its difference from the previous band.
    """
    if new:
        cube = hyspec.copy(cube, suffix="delta")
    cube_mem = cube.open_memmap(interleave='bsq', writable=True)
    for k in reversed(range(0, cube.nbands - 1)):
        cube_mem[k + 1] = cube_mem[k + 1] - cube_mem[k]
    cube_mem.flush()
    return sp.io.envi.open(*hyspec.hdr_raw(cube))


def rho_original(cube: hyspec.SpyFileSubclass, new=True) -> hyspec.SpyFileSubclass:
    """
    Reverse the effect of delta(cube).
    :param cube: a hyper-spectral cube that went through delta.
    :param new: whether to create a new file for rho(cube)
    :return: the original cube.
    """
    if new:
        cube = hyspec.copy(cube, suffix="rho")
    cube_mem = cube.open_memmap(interleave='bsq', writable=True)
    for k in range(0, cube.nbands):
        cube_mem[k + 1] = cube_mem[k + 1] + cube_mem[k]
    cube_mem.flush()
    return sp.io.envi.open(*hyspec.hdr_raw(cube))
