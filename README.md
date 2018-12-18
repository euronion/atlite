Atlite
======

Atlite is a [free
software](http://www.gnu.org/philosophy/free-sw.en.html),
[xarray](http://xarray.pydata.org/en/stable/)-based Python library for
converting weather data (such as wind speeds, solar radiation,
temperature and runoff) into power systems data (such as wind power,
solar power, hydro power and heating demand time series). It is designed
to work with big datasets, such as hourly global weather data over
several years at spatial resolutions down to e.g. 0.1 x 0.1 degree
resolution.

Atlite was originally conceived as a light-weight version of the Aarhus
University RE Atlas, which produces wind and solar generation time
series from historical reanalysis data. It has since been extended to
use weather datasets simulated with projected climate change and to
compute other time series, such as hydro power, solar thermal collectors
and heating demand. Atlite is designed to be modular, so that it can
work with any weather datasets. It currently has modules for the
following datasets:

-   [NCEP Climate Forecast
    System](http://rda.ucar.edu/datasets/ds094.1/) hourly historical
    reanalysis weather data available on a 0.2 x 0.2 degree global grid
-   [EURO-CORDEX Climate Change Projection](http://www.euro-cordex.net/)
    three-hourly up until 2100, available on a 0.11 x 0.11 degree grid
    for Europe
-   [ECMWF
    ERA5](https://software.ecmwf.int/wiki/display/CKB/ERA5+data+documentation)
    hourly historical reanalysis weather data on an approximately 0.3 x
    0.3 deg global grid
-   [CMSAF
    SARAH-2](https://wui.cmsaf.eu/safira/action/viewDoiDetails?acronym=SARAH_V002)
    half-hourly historical surface radiation on a 0.05 x 0.05 deg grid
    available for Europe and Africa (automatically interpolated to a 0.2
    deg grid and combined with ERA5 temperature).

It can process the following weather data fields:

-   Temperature
-   Downward short-wave radiation
-   Upward short-wave radiation
-   Wind speeds
-   Runoff
-   Surface roughness
-   Height maps
-   Soil temperature

The following power-system relevant time series can be produced for all
possible spatial distributions of assets:

-   Wind power generation for a given turbine type
-   Solar PV power generation for a given panel type
-   Solar thermal collector heat output
-   Hydroelectric inflow (simplified)
-   Heating demand (based on the degree-day approximation)

As of 2018 Atlite is under heavy development and therefore it is
recommended to use caution when using it in a production environment.

Citation for Aarhus University RE Atlas:
> G. B. Andresen, A. A. Søndergaard, M. Greiner, "Validation of danish wind time series from a
new global renewable energy atlas for energy system analysis," Energy
93, Part 1 (2015) 1074 – 1088.
<doi:http://dx.doi.org/10.1016/j.energy.2015.09.071>.

Atlite was initially developed by the [Renewable Energy
Group](https://fias.uni-frankfurt.de/physics/schramm/renewable-energy-system-and-network-analysis/)
at [FIAS](https://fias.uni-frankfurt.de/) to carry out simulations for
the [CoNDyNet project](http://condynet.de/), financed by the [German
Federal Ministry for Education and Research
(BMBF)](https://www.bmbf.de/en/index.html) as part of the [Stromnetze
Research
Initiative](http://forschung-stromnetze.info/projekte/grundlagen-und-konzepte-fuer-effiziente-dezentrale-stromnetze/).

Getting started
---------------

-   Install atlite from this repository with all its library
    dependencies\
    ```pip install git+https://github.com/FRESNA/atlite.git```
-   Download one of the weather datasets, see notes below.
-   Adjust the [atlite/config.py](atlite/config.py) directory paths to
    point to the directory where you downloaded the dataset
-   Create a cutout, i.e. a geographical rectangle and a selection of
    times, e.g. all hours in 2011 and 2012, to narrow down the scope
    -see [examples/create\_cutout.py](examples/create_cutout.py)
-   Select a sparse matrix of the geographical points inside the cutout
    you want to aggregate for your time series, and pass it to the
    appropriate converter function - see [examples/](examples/)


### Notes on accessing the different data sets

| Data set | Note | Link |
|----------|------|------|
| ERA-5    | Data for this data set is downloaded automatically when creating a cutout. For this to function, the `ecmwfapirc` client has to be installed and a API key set up. See the link for detailed information. |  [ECMWF website](https://confluence.ecmwf.int/display/WEBAPI/Access+ECMWF+Public+Datasets)    |


Licence
-------

Copyright 2016-2017 Gorm Andresen (Aarhus University), Jonas Hörsch
(FIAS), Tom Brown (FIAS), Markus Schlott (FIAS), David Schlachtberger
(FIAS)

This program (atlite) is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation; either [version 3 of the
License](LICENSE.txt), or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the [GNU
General Public License](LICENSE.txt) for more details.
