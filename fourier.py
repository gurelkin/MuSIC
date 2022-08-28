import numpy as np
import spectral as sp
import hyspec


def dilute(array: np.ndarray, keep: float) -> np.ndarray:
    """
    Performs a lossy compression on a 2-dimensional array using FFT.
    :param array: the n-dimensional array to be diluted.
    :param keep: how many Fourier coefficients to keep (in percents).
    The function :raises: an exception if an illegal value was given.
    :return: The FFTed image, containing only the highest percent of coefficients.
    """
    if not (0 <= keep <= 100):
        raise Exception(f"The parameter 'ratio' must be given in percents.")
    transformed = np.fft.fft2(array)
    keep = keep/100
    sorted_ = np.sort(np.abs(transformed.reshape(-1)))
    threshold = sorted_[int(np.floor((1-keep) * len(sorted_)))]
    indices = np.abs(transformed) > threshold
    return indices * transformed


def inverse(f_array: np.ndarray) -> np.ndarray:
    return np.abs(np.fft.ifft2(f_array))


# TODO: return the transformed cube (where dtype=csingle) and then use sparse matrix ant dtore its serialization (
#  needs to use pickle) in order to change the matrix back to a cube, create an empty one (using envi according to
#  the hdr) and change its memmap.

def dilute_bands(cube: hyspec.SpyFileSubclass, keep: float, new=True) -> hyspec.SpyFileSubclass:
    if new:
        cube = hyspec.copy(cube)
    cube = hyspec.change_dtype(cube, np.csingle)
    cube_mem = cube.open_memmap(interleave='bsq', writable=True)
    for k, band in enumerate(cube_mem):
        cube_mem[k] = dilute(band, keep)
    cube_mem.flush()
    return sp.io.envi.open(*hyspec.hdr_raw(cube))


# def dilute_bands(cube: hyspec.SpyFileSubclass, keep: float, new=True) -> hyspec.SpyFileSubclass:
#     if new:
#         cube = hyspec.copy(cube)
#     mem_map = cube.open_memmap(interleave='bsq', writable=True)
#     for k, band in enumerate(mem_map):
#         mem_map[k] = dilute(band, keep)
#     return sp.io.envi.open(*hyspec.hdr_raw(cube))


# def dilute_image(image: hyspec.SpyFileSubclass, keep: float, new=True) -> None:
#     if new:
#         image = hyspec.copy(image)
#     mem_map = image.open_memmap(interleave='bsq', writable=True)
#     new_mem_map = dilute(mem_map, keep)
#     for k in range(image.nbands):
#         mem_map[k] = new_mem_map[k]


# def dilute_pixels(image: hyspec.SpyFileSubclass, keep: float, new=True) -> None:
#     if new:
#         image = hyspec.copy(image)
#     mem_map = image.open_memmap(interleave='bip', writable=True)
#     for i in range(image.nrows):
#         for j in range(image.ncols):
#             pixel = mem_map[i][j]
#             mem_map[i][j] = dilute(pixel, keep)

