"""Remote sensing utilities package

This package exposes RasterHandler and Analyzer utilities originally
from top-level scripts. It provides functions to compute NDVI and NBR
from numpy arrays and small wrapper classes that use rasterio datasets.
"""

from .analyzer import Analyzer, compute_ndvi, compute_nbr
from .rasterhandler import RasterHandler, AreaType

__all__ = ["Analyzer", "compute_ndvi", "compute_nbr", "RasterHandler", "AreaType"]
