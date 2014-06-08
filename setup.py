# !/usr/bin/env python3
from distutils.core import setup
import py2exe

setup(
    name='MyDupFileKiller',
    description="A Duplicate File Killer",
    version='1.1',
    console=[{'script': 'mydupfilekiller.py'}],
    options={"py2exe": dict(compressed=True,
                            optimize=2,
                            bundle_files=1,
                            includes="ctypes")},
    zipfile=None
)
