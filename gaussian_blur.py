import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter # imported for faster speed 
import math

# def gaussian_kernel(radius, sigma=None):
#     if sigma is None:
#         sigma = radius / 2.0
#     kernel_size = 2 * radius + 1
#     ax = np.arange(-radius, radius + 1)
#     xx, yy = np.meshgrid(ax, ax)
#     kernel = np.exp(-(xx**2 + yy**2) / (2. * sigma**2))
#     kernel = kernel / np.sum(kernel)
#     return kernel

def apply_gaussian_blur(image, radius):
    img_array = np.array(image)
    blurred = np.zeros_like(img_array)
    for c in range(3):  
        blurred[..., c] = gaussian_filter(img_array[..., c], sigma=radius)
    return Image.fromarray(blurred.astype(np.uint8))
