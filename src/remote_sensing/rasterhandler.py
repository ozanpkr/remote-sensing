import rasterio
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional
import os

from enum import Enum


class AreaType(Enum):
    BURNED = 1
    UNBURNED = 2


class RasterHandler:
    """Utility class to open raster datasets and save bands or RGB images.

    This class intentionally keeps a simple API: pass file paths for burned
    and unburned images (commonly Sentinel-2 products) and call helpers.
    """

    def __init__(self, burned_tiff_path: str, unburned_tiff_path: str, output_dir: Optional[str] = "outputs"):
        self._src = {
            AreaType.BURNED: rasterio.open(burned_tiff_path),
            AreaType.UNBURNED: rasterio.open(unburned_tiff_path)
        }
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def src(self, area_type: AreaType) -> rasterio.io.DatasetReader:
        return self._src[area_type]

    def close(self):
        for ds in self._src.values():
            try:
                ds.close()
            except Exception:
                pass

    def get_metadata(self, area_type: AreaType) -> dict:
        src = self._src[area_type]
        return src.meta

    def _save_band(self, area_type: AreaType, band_idx: int, output_path: str, band: np.ndarray):
        src = self._src[area_type]
        with rasterio.open(output_path, 'w', driver='GTiff', width=src.width, height=src.height, count=1, dtype=band.dtype, crs=src.crs, transform=src.transform) as dst:
            dst.write(band, 1)

    def save_bands(self, area_type: AreaType):
        src = self._src[area_type]
        for band_idx in range(1, src.count + 1):
            band = src.read(band_idx)
            output_path = os.path.join(self.output_dir, f"band{band_idx}.tif")
            self._save_band(area_type, band_idx, output_path, band)

    def visualize_rgb(self, area_type: AreaType, show: bool = True) -> str:
        src = self._src[area_type]
        # Sentinel-2 common band mapping (1-based): red=4, green=3, blue=2
        red = src.read(4)
        green = src.read(3)
        blue = src.read(2)

        rgb_image = np.stack([red, green, blue], axis=-1).astype(np.float32)
        rgb_image = rgb_image / np.max(rgb_image)

        plt.figure(figsize=(8, 6))
        plt.imshow(rgb_image)
        plt.axis('off')
        plt.title('Sentinel-2 RGB Image')
        if show:
            plt.show()

        output_path = os.path.join(self.output_dir, "sentinel2_rgb.png")
        plt.imsave(output_path, rgb_image)
        return output_path

    def _save_band_with_colormap(self, area_type: AreaType, band_idx: int, band: np.ndarray):
        cmap = plt.cm.get_cmap('viridis')
        normed_band = (band - band.min()) / (band.max() - band.min())
        band_colored = (cmap(normed_band) * 255).astype(np.uint8)

        output_path = os.path.join(self.output_dir, f"band{band_idx}_colored.tif")
        src = self._src[area_type]
        with rasterio.open(output_path, 'w', driver='GTiff', width=src.width, height=src.height, count=4, dtype=band_colored.dtype, crs=src.crs, transform=src.transform) as dst:
            dst.write(band_colored.transpose(2, 0, 1), indexes=[1, 2, 3, 4])

    def save_bands_with_colormap(self, area_type: AreaType):
        src = self._src[area_type]
        for band_idx in range(1, src.count + 1):
            band = src.read(band_idx)
            self._save_band_with_colormap(area_type, band_idx, band)
