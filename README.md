# MuSIC: Multi-Spectral Images Compressor

### Background
This is the Python source code of a project regarding the compression of [hyperpectral images](https://en.wikipedia.org/wiki/Hyperspectral_imaging).
In ordinary color images, every pixel usually holds three values, corresponding to the colors red, green and blue. 
Au contraire, hyperspectral images sample a scene in an extensive number of wavelengths. 
That is, every pixel in the image holds a k-dimensional vector, where each entry reflects the intensity of a certain wavelength, measured at that point. 
Therefore, the size of a hyperspectral image will be several times greater than the size of a greyscale or color image with the same spatial resolution.

### Method
The Compressor can utilize both lossy and lossless compression methods:

For the lossless method, I chose to adapt the main principle of [delta encoding](https://en.wikipedia.org/wiki/Delta_encoding) to fit our case. 
In the code, I transformed the cube by replacing each slice with its difference from the previous slice. 
In other words, I treated each pixel in the hyperspectral cube as a sequence of its own and replaced it with its delta encoding. 

For the lossy method, I chose to employ  the [Fourier transform](https://en.wikipedia.org/wiki/Fourier_transform). 
Compression algorithms like JPEG’s use image transforms to store only a subset of the image’s coefficients in the frequency domain. 
By that, they reduce the number of effective components in the image, increasing its compressibility. 
In my implementation, I applied the FFT over each slice of the cube separately, and then equated to zero its smallest coefficients.

After applying a method, the program uses zlib's implementation of the DEFLATE algorithm to enhance the compression. 
As can be seen in `results.png`, by preprocessing our images using the above methods, we get higher compression ratio.

### Usage
This program works with hyperspectral images in ENVI header format. 
By calling the `help` command, a menu will be printed, displaying the various compression options.
Important note: the image's `.raw` and `.hdr` files must have the same name and be located in the same directory.
