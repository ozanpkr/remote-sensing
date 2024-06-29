import rasterio
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class RasterHandler:
    def __init__(self, tiff_path):
        self.__src = rasterio.open(tiff_path)
        self.__metadata = self.src.meta
    @property
    def src(self):
        return self.__src
    def get_metadata(self):
        df_metadata = pd.DataFrame(self.__metadata.items(), columns=['Meta Veri', 'Değer'])
        meta_aciklamalari = {
            'driver': 'Kullanılan sürücü veya veri formatı',
            'dtype': 'Veri tipi (örneğin, uint16)',
            'nodata': 'Geçersiz (boş) değerlerin tanımlanması',
            'width': 'Görüntünün genişliği piksel cinsinden',
            'height': 'Görüntünün yüksekliği piksel cinsinden',
            'count': 'Bant sayısı',
            'crs': 'Koordinat referans sistemi (EPSG kodu ile belirtilen)',
            'transform': 'Piksel koordinatlarının dünya koordinatlarına dönüşüm matrisi'
        }
        df_metadata['Açıklama'] = df_metadata['Meta Veri'].map(meta_aciklamalari)
        print(df_metadata.head(5))
    
    def save_bands(self):
        for band_idx in range(1, self.__src.count + 1):
            band = self.__src.read(band_idx)
            output_path = f"outputs/band{band_idx}.tif"
            with rasterio.open(output_path, 'w', driver='GTiff', width=self.__src.width, height=self.__src.height, count=1, dtype=band.dtype) as dst:
                dst.write(band, 1)
                print(f"Band {band_idx} kaydedildi: {output_path}")
    
    def visualize_rgb(self):
        red = self.__src.read(4)   # Bant 4
        green = self.__src.read(3) # Bant 3
        blue = self.__src.read(2)  # Bant 2

        rgb_image = np.stack([red, green, blue], axis=-1)
        rgb_image = rgb_image / np.max(rgb_image)

        plt.figure(figsize=(8, 6))
        plt.imshow(rgb_image)
        plt.axis('off')
        plt.title('Sentinel-2 RGB Görüntü')
        plt.show()

        output_path = "./outputs/sentinel2_rgb.png"
        plt.imsave(output_path, rgb_image)
        print(f"RGB görüntü başarıyla kaydedildi: {output_path}")

    def save_bands_with_colormap(self):
        for band_idx in range(1, self.__src.count + 1):
            band = self.__src.read(band_idx)
            cmap = plt.cm.get_cmap('viridis')  # Renk skalası (viridis örneği)
            normed_band = (band - band.min()) / (band.max() - band.min())  # Normalizasyon
            band_colored = (cmap(normed_band) * 255).astype(np.uint8)  # 0-255 arasına dönüştürme ve uint8 türüne dönüştürme

            output_path = f"outputs/band{band_idx}_colored.tif"
            with rasterio.open(output_path, 'w', driver='GTiff', width=self.__src.width, height=self.__src.height, count=4, dtype=band_colored.dtype) as dst:
                dst.write(band_colored.transpose(2, 0, 1), indexes=[1, 2, 3, 4])
                print(f"Band {band_idx} renk skalası ile kaydedildi: {output_path}")