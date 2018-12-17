from setuptools import setup, find_packages
from codecs import open
import six

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='atlite',
    version='0.0.1',
    author='Gorm Andresen (Aarhus University), Jonas Hoersch (FIAS), Tom Brown (FIAS)',
    author_email='hoersch@fias.uni-frankfurt.de',
    description='Light-weight version of Aarhus RE Atlas for converting weather data to power systems data',
    long_description=long_description,
    url='https://github.com/FRESNA/atlite',
    license='GPLv3',
    packages=find_packages(exclude=['doc', 'test']),
    include_package_data=True,
    python_requires='>3.0',
    install_requires=['numpy', 'scipy', 'pandas', 'xarray>=0.10.0', 'dask',
                      'rasterio', 'shapely', 'bottleneck',
                      'toolz',
                      'cyordereddict ; python_version<'3.5'"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ])
