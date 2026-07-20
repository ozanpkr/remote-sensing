# Quickstart & CONTRIBUTING

This branch refactors the original top-level scripts into a small package at src/remote_sensing.

Quickstart

1. Create a Python environment and install dependencies (system GDAL required for rasterio):

```bash
# On Ubuntu you may need:
sudo apt-get update && sudo apt-get install -y gdal-bin libgdal-dev
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the notebook or import the package in a script:

```python
from remote_sensing import RasterHandler, Analyzer, AreaType
rh = RasterHandler('path/to/burned.tif', 'path/to/unburned.tif')
print(rh.get_metadata(AreaType.BURNED))
rh.close()
```

Notes
- This branch does not remove large binaries from your git history. It will stop tracking new outputs by adding them to .gitignore.
- If you want me to convert large dataset files to Git LFS or rewrite history to remove big files, tell me and I will follow up.
