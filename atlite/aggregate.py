## Copyright 2016-2017 Gorm Andresen (Aarhus University), Jonas Hoersch (FIAS), Tom Brown (FIAS)

## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License, or (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Renewable Energy Atlas Lite (Atlite)

Light-weight version of Aarhus RE Atlas for converting weather data to power systems data
"""

import xarray as xr
import dask

def aggregate_sum(da):
    return da.sum('time')

def aggregate_matrix(da, matrix, index):
    # We could maybe get rid of this distinction?
    # However the performance of the 'else' branch is significantly (2x-4x) lower than the upper one
    # Could probably be substituted by a variation of the upper variant (w/o the whole casting)
    # TODO: Need to compare results -> Debug mode
    # TODO: Why is this here? Relict from when this was not equivalent yet (@xarray)?
    
    if isinstance(da.data, dask.array.core.Array):
        da = da.stack(spatial=('y', 'x'))
        return xr.apply_ufunc(
            lambda da: da * matrix.T,
            da,
            input_core_dims=[['spatial']],
            output_core_dims=[[index.name]],
            dask='parallelized',
            output_dtypes=[da.dtype],
            output_sizes={index.name: index.size}
        ).assign_coords(**{index.name: index})
    else:
        da = da.stack(spatial=('y', 'x')).transpose('spatial', 'time')
        return xr.DataArray(matrix * da,
                            [index, da.coords['time']])
