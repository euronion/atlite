# -*- coding: utf-8 -*-

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


"""Methods for validation of generated time-series against reference time-series."""

import xarray as xr
import numpy as np


def _calculate_rms(da, ref):
    rms = ((ref - da)**2).sum(dim='time')/da.coords['time'].count()
    rms.name = 'RMS'
    return rms

def _calculate_total_difference(da, ref):
    total_diff = da.sum(dim='time') - ref.sum(dim='time')
    total_diff.name = "TOTAL difference"
    return total_diff

def _calculate_chi_square(da, ref):
    chi_square = ((ref - da)**2/ref).sum(dim='time')
    chi_square.name = "Chi square"
    return chi_square

def _calculate_mape(da, ref):
    mape = np.abs((ref-da)/ref).mean(dim='time')
    mape.name = "MAPE"
    return mape

from .utils import product_dict
def _calculate_dkl(da, ref):

    no_of_bins = 100

    # +++ Calculating the probability distribution (mass) functions +++
    # There is no multidimensional groupby yet in xarray
    # -> workaround by selecting each dimension seperately
    pmfs = None
    
    # Then calculate the probability mass function PMF for #nbins in the capacity factor range (0,1)
    for d_coords in product_dict(**{c:da.coords[c].values for c in da.coords if c != 'time'}):

        d = da.sel(d_coords)

        # Calculate the PMF for each entry
        hist, bins = np.histogram(d, bins=no_of_bins, range=(0,1))
        hist = hist/np.sum(hist) # can't use /= here because of integers

        # Reconvert to xarray for calculations later
        hist = xr.DataArray(hist, coords={'CF bin':(bins[:-1]+bins[1:])/2}, dims=('CF bin'), name='PMF')
        hist = hist.assign_coords(**d_coords).expand_dims(d_coords)

        # Combine into a single DataSet again
        if pmfs is None:
            pmfs = hist.to_dataset()
        else:
            pmfs = xr.merge([pmfs, hist.to_dataset()])


    # Calculate PMF for reference Capacity Factors for each bus (one entry per bus)
    # NaN values are removed, causing a (small) skew in the probabilities
    for bus in ref.coords['bus']:
        d = ref.sel(bus=bus).dropna(dim='time')

        # Calculate the PMF
        hist, bins = np.histogram(d, bins=no_of_bins, range=(0,1))
        hist = hist/np.sum(hist) # can't use /= here because of integers

        # Generate appropriate DataArray and merge into results
        hist = xr.DataArray(hist, coords={'CF bin':(bins[:-1]+bins[1:])/2}, dims=('CF bin'), name='PMF reference')
        hist = hist.assign_coords(bus=bus).expand_dims('bus')
        pmfs = xr.merge([pmfs, hist])
        
    # --- Calculating the probability distribution (mass) functions ---

    # Where data PMFs are 0 the DKL formula would divide by 0
    # To resolve this we introduce a penalty if the data PMF 
    # is 0 and the reference PMF != [0,1]; from this assignment,
    # there follows no penalty for the other two cases
    pmfs['PMF'] = pmfs.PMF.where(pmfs.PMF != 0., 1)

    t = pmfs['PMF reference']/pmfs.PMF
    t = t.where(t != 0, 1) # Set "0" entries to "1" to supress errors, because log(1) = 0: no influence on result
    dkl = (np.log(t)*pmfs['PMF reference']).sum(dim='CF bin')
    dkl.name = 'DKL'
    
    return dkl



def calculate_agreement(da, ref, measure='RMS'):
    """Calculate an agreement metric between a given and a reference generation time-series.
    
    
    For DKL, the CF of the reference data set is calculated for each 'bus' along the 'time' dimension.
    All remaining dimensions are used for calculation of their respective coordinates DKLs.
    
    Note:
    * NaN entries are simply discarded, which can cause a small skew in probabilities.)
    * Recommmended measures for comparing Capacity Factors: MAPE, CHI_SQUARE, DKL
    
    Parameters
    ----------
    da : xarray.DataArray
        Data to evaluate along the necessary dimension 'time'.
        Except for measure='DKL', this can be the generation time series or the capacity factor time series.
        For DKL this must be the capacity factor time series.
    ref : xarray.DataArray
        Reference data with the same dimensions and coordinates as 'da'.
    measure : ['RMS', 'DKL', 'TOTAL', 'MAPE', 'CHI_SQUARE']
        The measure to use for calculating the agreement.
        (Default: Root-Mean-Square RMS)
    """
    funcs = {
        "RMS"  : _calculate_rms,  # Root Mean Square error
        "TOTAL": _calculate_total_difference,
        "DKL"  : _calculate_dkl,  # Kullback-Leibler Divergence
        "MAPE" : _calculate_mape, # Mean Absolute Percentage Error
        "CHI_SQUARE" : _calculate_chi_square
    } 

    # Select function or return error
    func = funcs.get(measure.upper())
    if func is None:
        raise ValueError("Unknown measure {m}".format(m=measure))

    # Calculate and return
    return func(da, ref)