# !/usr/bin/env python3
from distutils.core import setup

setup(
    name='MyDupFileKiller',
    description="A Duplicate File Killer",
    version='1.0',
    console=[{'script': 'mydupfilekiller.py'}],
    options={"py2exe":
                 {"compressed": True,
                  "optimize": 2,
                   "bundle_files": 1,
                   "includes": "ctypes"
                 }
    },
    zipfile=None
)

