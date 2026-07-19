import numpy as np
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
from typing import Optional
import rasterio


def compute_ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    """Compute NDVI from NIR and Red bands (arrays).

    Returns an array of floats in range [-1, 1] where possible. Division by
    zero is ignored and results in nan where both bands are zero.
    """
    np.seterr(divide='ignore', invalid='ignore')
    nir_f = nir.astype(float)
    red_f = red.astype(float)
    denom = (nir_f + red_f)
    ndvi = (nir_f - red_f) / denom
    return ndvi


def compute_nbr(nir: np.ndarray, swir: np.ndarray) -> np.ndarray:
    """Compute NBR from NIR and SWIR bands.

    Returns float array in range [-1, 1] where defined. Values where both
    bands are <= 0 will be left as 0.
    """
    nir_f = nir.astype(np.float32)
    swir_f = swir.astype(np.float32)
    nbr = np.zeros_like(nir_f, dtype=np.float32)
    valid = np.logical_and(nir_f > 0, swir_f > 0)
    nbr[valid] = (nir_f[valid] - swir_f[valid]) / (nir_f[valid] + swir_f[valid])
    return nbr


class Analyzer:
    """Visualization helpers for NDVI, dNBR and image differences.

    The methods separate computation (compute_ndvi/compute_nbr) from plotting
    so they can be unit tested headless.
    """

    def visualize_ndvi_with_threshold(self, src_dataset: rasterio.io.DatasetReader, threshold: Optional[float] = None, verbose: bool = False) -> np.ndarray:
        """Read bands from a rasterio dataset and visualize NDVI.

        Parameters
        - src_dataset: rasterio DatasetReader with at least bands for red and NIR
          (common Sentinel-2 mapping: red=3, nir=8 in 1-based indexing)
        - threshold: if provided, returns a binary mask (0/1) where NDVI >= threshold
        - verbose: if True, shows a matplotlib figure

        Returns the NDVI array (masked if threshold is provided).
        """
        red_band = src_dataset.read(3)
        nir_band = src_dataset.read(8)
        ndvi = compute_ndvi(nir_band, red_band)

        cmap = 'RdYlGn'
        if threshold is not None:
            ndvi_masked = np.zeros_like(ndvi, dtype=np.uint8)
            ndvi_masked[ndvi >= threshold] = 1
            cmap = LinearSegmentedColormap.from_list('custom_cmap', ['black', 'green'], N=2)
            ndvi = ndvi_masked

        if verbose:
            plt.figure(figsize=(8, 8))
            plt.imshow(ndvi, cmap=cmap, interpolation='none')
            plt.colorbar(label='NDVI')
            plt.title('Normalized Difference Vegetation Index (NDVI)')
            plt.axis('off')
            plt.show()

        return ndvi

    def visualize_dnbr(self, dnbr_values: np.ndarray, show: bool = True) -> np.ndarray:
        """Visualize dNBR values using a diverging colormap."""
        plt.figure(figsize=(10, 8))
        plt.imshow(dnbr_values, cmap='RdYlBu_r', vmin=-1, vmax=1)
        plt.colorbar(label='dNBR')
        plt.title('dNBR Visualization')
        if show:
            plt.show()
        return dnbr_values

    def visualize_image_difference(self, image1: np.ndarray, image2: np.ndarray, show: bool = True) -> np.ndarray:
        diff = image1 - image2
        diff_mask = (diff != 0)
        colored_diff = np.zeros_like(image1, dtype=np.uint8)
        colored_diff[diff_mask] = 255

        colored_diff_rgb = np.stack([colored_diff, np.zeros_like(colored_diff), np.zeros_like(colored_diff)], axis=-1)

        plt.figure(figsize=(10, 4))
        plt.subplot(1, 3, 1)
        plt.imshow(image1, cmap='gray')
        plt.title('Image 1')
        plt.axis('off')

        plt.subplot(1, 3, 2)
        plt.imshow(image2, cmap='gray')
        plt.title('Image 2')
        plt.axis('off')

        plt.subplot(1, 3, 3)
        plt.imshow(colored_diff_rgb)
        plt.title('Difference (Red)')
        plt.axis('off')

        plt.tight_layout()
        if show:
            plt.show()
        return colored_diff_rgb
