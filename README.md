# Repository refactor: package structure

This branch moves reusable code into src/remote_sensing and adds minimal packaging and tests.

Files added/changed:
- src/remote_sensing/{__init__,analyzer,rasterhandler}.py
- requirements.txt
- .gitignore (updated to ignore outputs/ and *.tif)
- CONTRIBUTING.md (quickstart)
- tests/test_imports.py (smoke test)

I did not modify notebooks/ or move large binary files in this commit to avoid copying heavy files in the PR. If you'd like I can also:
- move notebooks to notebooks/
- move presentation assets to docs/
- convert large datasets to Git LFS or remove them from history (requires force-push)
