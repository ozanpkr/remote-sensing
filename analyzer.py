import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import enum
from rasterio import plot

class AreaType(enum.Enum):
    BURNED = 1
    UNBURNED = 2

class Analyzer:
    def __init__(self):
        self.__src = None

    def visualize_ndvi_with_threshold(self, src_dataset, threshold=None, verbose=False):
        """
        Rasterio veri kümesinden NDVI haritasını belirli bir eşik değeri üstünde
        yeşil, diğer alanları kırmızı olarak görselleştirir.
    
        Parameters:
        - src_dataset (rasterio.io.DatasetReader): Rasterio veri kümesi, TIFF dosyasının açılmış hali.
        - threshold (float): NDVI eşik değeri. Bu değeri geçen alanlar yeşil olacak.
        - verbose (bool): Görüntüyü görselleştirme modunu etkinleştirir veya devre dışı bırakır.
    
        Returns:
        - ndvi_masked (numpy.ndarray): NDVI haritası (eğer verbose=True ise).
        """
        red_band = src_dataset.read(3)
        nir_band = src_dataset.read(8)
    
        np.seterr(divide='ignore', invalid='ignore')
    
        ndvi = (nir_band.astype(float) - red_band.astype(float)) / (nir_band + red_band)
    
        cmap = 'RdYlGn'
        if threshold is not None:
            ndvi_masked = np.zeros_like(ndvi, dtype=np.uint8)
            ndvi_masked[ndvi >= threshold] = 1
            ndvi_masked[ndvi < threshold] = 0
            cmap = LinearSegmentedColormap.from_list('custom_cmap', ['black', 'green'], N=2)
            ndvi = ndvi_masked
            
        if verbose:
            plt.figure(figsize=(10, 10))
            plt.imshow(ndvi, cmap=cmap, interpolation='none')
            plt.colorbar(label='NDVI')
            plt.title('Normalized Difference Vegetation Index (NDVI)')
            plt.axis('off')
            plt.show()
        
        return ndvi

    def visualize_dnbr(self, dnbr_values):
        """
        Visualizes dNBR values using a color map.
        
        Parameters:
        - dnbr_values (numpy.ndarray): dNBR values to visualize.
        """
        plt.figure(figsize=(10, 8))
        plt.imshow(dnbr_values, cmap='RdYlBu_r', vmin=-1, vmax=1)
        plt.colorbar(label='dNBR')
        plt.title('dNBR Visualization')
        plt.xlabel('Distance (Pixels)')
        plt.ylabel('Distance (Pixels)')
        #plot.show(nbr, cmap='RdYlGn', vmin=-1, vmax=1)
        plt.show()
        return dnbr_values


    def visualize_image_difference(self, image1, image2):
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
        plt.show()

    def calculate_and_plot_nbr(self,src_dataset, threshold=None):
        """
        Sentinel-2 görüntüsünden Normalized Burn Ratio (NBR) hesaplar ve görselleştirir.
        
        Args:
        src_dataset (object): Sentinel-2 TIFF dosyası veri kümesi.
        threshold (float or None): NDVI için eşik değeri. None ise eşik uygulanmaz.
        """
        # NIR ve SWIR bantlarını yükleyin
        nir_band = src_dataset.read(8).astype(np.float32)
        swir_band = src_dataset.read(11).astype(np.float32)
    
        # NIR ve SWIR bantlarının değerleri sıfırdan büyük olan yerlerde NBR hesaplayın
        nbr = np.zeros_like(nir_band, dtype=np.float32)
        valid_mask = np.logical_and(nir_band > 0, swir_band > 0)
        nbr[valid_mask] = (nir_band[valid_mask] - swir_band[valid_mask]) / (nir_band[valid_mask] + swir_band[valid_mask])
    
        # Eğer threshold belirtilmişse, NBR'yi bu eşik değerine göre maskeleyin
        if threshold is not None:
            nbr_masked = np.zeros_like(nbr, dtype=np.uint8)
            nbr_masked[nbr >= threshold] = 1
            nbr_masked[nbr < threshold] = 0
            nbr = nbr_masked.astype(np.float32)  # Maskelenmiş NBR'yi kullan
    
            # Özel renk skalası için lineer segmentli bir renk haritası oluşturun
            cmap = LinearSegmentedColormap.from_list('custom_cmap', ['red', 'green'], N=2)
    
        else:
            cmap = 'RdYlGn'  # Eğer eşik belirtilmemişse varsayılan renk haritası kullan
    
        # Renkli görselleştirme ve renk skalası eklemek için matplotlib kullanın
        plt.figure(figsize=(10, 8))
        plt.imshow(nbr, cmap=cmap)
        plt.colorbar(label='NBR Masked' if threshold is not None else 'NBR')
        plt.title('Normalized Burn Ratio (NBR)')
        plt.show()
        return nbr