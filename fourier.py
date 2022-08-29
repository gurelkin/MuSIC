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


def inverse(ffted_array: np.ndarray) -> np.ndarray:
    """
    Performs IFFT on a 2-dimensional array.
    :param ffted_array: am array of complex numbers.
    :return: the IFFT of `ffted_array`.
    """
    return np.abs(np.fft.ifft2(ffted_array))


def dilute_bands(cube: hyspec.SpyFileSubclass, keep: float) -> hyspec.SpyFileSubclass:
    """
    Takes a hyper-spectral cube and perform dilution by FFTon each of its bands.
    :param cube: the hyper-spectral image.
    :param keep: what percent of highest fourier coefficients to preserve.
    :return: a new cube with FFTed images as bands.
    """
    cube_mem = cube.open_memmap(interleave='bsq', writable=True)
    complex_cube = hyspec.zeros_like(cube, dtype=np.csingle)
    complex_cube_mem = complex_cube.open_memmap(interleave='bsq', writable=True)
    for k, band in enumerate(cube_mem):
        complex_cube_mem[k] = dilute(band, keep)
    complex_cube_mem.flush()
    return sp.io.envi.open(*hyspec.hdr_raw(complex_cube))


def reconstruct_bands(cube: hyspec.SpyFileSubclass) -> hyspec.SpyFileSubclass:
    """
    Reconstructs the cube based on the Fourier coefficients left in each band.
    :param cube: the FFTed cube.
    :return: the reconstructed cube.
    """
    cube_mem = cube.open_memmap(interleave='bsq', writable=True)
    uint_cube = hyspec.zeros_like(cube, np.uint16)
    uint_cube_mem = uint_cube.open_memmap(interleave='bsq', writable=True)
    for k, band in enumerate(cube_mem):
        uint_cube_mem[k] = inverse(band)
    uint_cube_mem.flush()
    return sp.io.envi.open(*hyspec.hdr_raw(uint_cube))



