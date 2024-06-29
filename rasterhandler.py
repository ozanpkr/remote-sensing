import rasterio
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import enum

class AreaType(enum.Enum):
    BURNED = 1
    UNBURNED = 2

class RasterHandler:
    def __init__(self, burned_tiff_path, unburned_tiff_path):
        self._src = {
            AreaType.BURNED: rasterio.open(burned_tiff_path),
            AreaType.UNBURNED: rasterio.open(unburned_tiff_path)
        }
    def src(self,area_type):
            return self._src[area_type]
    def _validate_area_type(self, area_type):
        if area_type not in AreaType:
            raise ValueError("Invalid area type specified.")

    def get_metadata(self, area_type):
        self._validate_area_type(area_type)
        
        src = self._src[area_type]
        meta_data = src.meta
        meta_descriptions = {
            'driver': 'Driver used or data format',
            'dtype': 'Data type (e.g., uint16)',
            'nodata': 'Definition of invalid (empty) values',
            'width': 'Image width in pixels',
            'height': 'Image height in pixels',
            'count': 'Number of bands',
            'crs': 'Coordinate reference system (specified with EPSG code)',
            'transform': 'Transformation matrix from pixel coordinates to world coordinates'
        }
        df_metadata = pd.DataFrame(meta_data.items(), columns=['Metadata', 'Value'])
        df_metadata['Description'] = df_metadata['Metadata'].map(meta_descriptions)
        print(df_metadata.head(5))

    def _save_band(self, area_type, band_idx, output_path, band):
        with rasterio.open(output_path, 'w', driver='GTiff', width=self._src[area_type].width, height=self._src[area_type].height, count=1, dtype=band.dtype) as dst:
            dst.write(band, 1)
            print(f"Band {band_idx} saved: {output_path}")

    def save_bands(self, area_type):
        self._validate_area_type(area_type)

        for band_idx in range(1, self._src[area_type].count + 1):
            band = self._src[area_type].read(band_idx)
            output_path = f"outputs/band{band_idx}.tif"
            self._save_band(area_type, band_idx, output_path, band)

    def visualize_rgb(self, area_type):
        self._validate_area_type(area_type)

        red = self._src[area_type].read(4)   # Band 4
        green = self._src[area_type].read(3) # Band 3
        blue = self._src[area_type].read(2)  # Band 2

        rgb_image = np.stack([red, green, blue], axis=-1)
        rgb_image = rgb_image / np.max(rgb_image)

        plt.figure(figsize=(8, 6))
        plt.imshow(rgb_image)
        plt.axis('off')
        plt.title('Sentinel-2 RGB Image')
        plt.show()

        output_path = "./outputs/sentinel2_rgb.png"
        plt.imsave(output_path, rgb_image)
        print(f"RGB image saved successfully: {output_path}")

    def _save_band_with_colormap(self, area_type, band_idx, band):
        cmap = plt.cm.get_cmap('viridis')  # Color map (example: viridis)
        normed_band = (band - band.min()) / (band.max() - band.min())  # Normalization
        band_colored = (cmap(normed_band) * 255).astype(np.uint8)  # Convert to 0-255 and to uint8 type

        output_path = f"outputs/band{band_idx}_colored.tif"
        with rasterio.open(output_path, 'w', driver='GTiff', width=self._src[area_type].width, height=self._src[area_type].height, count=4, dtype=band_colored.dtype) as dst:
            dst.write(band_colored.transpose(2, 0, 1), indexes=[1, 2, 3, 4])
            print(f"Band {band_idx} saved with colormap: {output_path}")

    def save_bands_with_colormap(self, area_type):
        self._validate_area_type(area_type)

        for band_idx in range(1, self._src[area_type].count + 1):
            band = self._src[area_type].read(band_idx)
            self._save_band_with_colormap(area_type, band_idx, band)
