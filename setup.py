# !/usr/bin/env python3
from distutils.core import setup

try:
    import py2exe
except ImportError:
    py2exe = None
    pass

setup(
    name='mydupfilekiller',
    description="A Duplicate File Killer",
    version='1.3',
    console=[{'script': 'mydupfilekiller.py'}],
    options={"py2exe": dict(compressed=True,
                            optimize=2,
                            bundle_files=1,
                            includes="ctypes")},
    zipfile=None
)
