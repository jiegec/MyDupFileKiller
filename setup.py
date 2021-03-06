from mydupfilekiller import __version__
try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    
from setuptools import setup, find_packages
    


setup(
    name="mydupfilekiller",
    packages=find_packages(),
    description="A Duplicate File Killer",
    version=__version__,
    entry_points={'console_scripts': ['mydupfilekiller = mydupfilekiller.console:main',
                                      'mydupfilekiller-gui = mydupfilekiller.gui:main']},
    author="Wiadufa Chen",
    author_email="wiadufachen@gmail.com",
    url="https://github.com/wiadufachen/mydupfilekiller",
    classifiers=["Programming Language :: Python",
                 "Programming Language :: Python :: 3",
                 "License :: OSI Approved :: Apache Software License",
                 "Development Status :: 4 - Beta",
                 "Operating System :: OS Independent",
                 ],
    long_description=open('README.txt').read(),
    include_package_data=True,
    package_data={
        'mydupfilekiller': ['*.xrc']
    },
    install_requires=['argparse', 'cython']
)
