# -*- coding: utf-8 -*-

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

from __future__ import absolute_import

import os
import yaml
from six import string_types
from operator import itemgetter
import numpy as np
from scipy.signal import fftconvolve
from pkg_resources import resource_stream

def get_windturbineconfig(turbine):
    res_name = "resources/windturbine/" + turbine + ".yaml"
    turbineconf = yaml.load(resource_stream(__name__, res_name))
    V, POW, hub_height = itemgetter('V', 'POW', 'HUB_HEIGHT')(turbineconf)
    return dict(V=V, POW=POW, hub_height=hub_height, P=max(POW))

def get_solarpanelconfig(panel):
    res_name = "resources/solarpanel/" + panel + ".yaml"
    return yaml.load(resource_stream(__name__, res_name))

def solarpanel_rated_capacity_per_unit(panel):
    # unit is m^2 here

    if isinstance(panel, string_types):
        panel = get_solarpanelconfig(panel)

    model = panel.get('model', 'huld')
    if model == 'huld':
        return panel['efficiency']
    elif model == 'bofinger':
        # one unit in the capacity layout is interpreted as one panel of a
        # capacity (A + 1000 * B + log(1000) * C) * 1000W/m^2 * (k / 1000)
        A, B, C = itemgetter('A', 'B', 'C')(panel)
        return (A + B * 1000. + C * np.log(1000.))*1e3

def windturbine_rated_capacity_per_unit(turbine):
    if isinstance(turbine, string_types):
        turbine = get_windturbineconfig(turbine)

    return turbine['P']

def windturbine_smooth(turbine, params={}, rescale=True):
    '''Smooth the power curve in `turbine` via convolution with a gaussian kernel.

    The convolution reduces the maximum power of the power curve.
    Following [2], the power curve is rescaled to match the turbines
    maximum rated power. Rescaling can be prevented via 'rescale' = False .

    Parameters
    ----------
    turbine : dict
        Turbine config with at least V and POW
    params : dict
        Allows adjusting fleet availability eta, mean Delta_v and
        stdev sigma. Defaults to values used for Denmark in [1]:
        0.95, 1.27 and 2.29, respectively.
    rescale : boolean
        Whether to rescale the smoothed power curve to its original
        rated power (defaults to True).

    Returns
    -------
    turbine : dict
        Turbine config with a smoothed power curve

    References
    ----------
    [1] G. B. Andresen, A. A. Søndergaard, M. Greiner, Validation of
    Danish wind time series from a new global renewable energy atlas
    for energy system analysis, Energy 93, Part 1 (2015) 1074–1088.
    [2] P. Nørgaard, H. Holttinen, A Multi-Turbine Power Curve Approach,
    Proceedings of Nordic Wind Power Conference NWPC 2004. PDF available at
    https://pdfs.semanticscholar.org/bbe0/1a9987893a53bd3c443b7e9b2773046f725c.pdf
    (last accessed 2019-02-27).
    '''

    if not isinstance(params, dict):
        params = {}

    eta = params.get('eta', 0.95)
    Delta_v = params.get('Delta_v', 1.27)
    sigma = params.get('sigma', 2.29)

    def kernel(v_0):
        # all velocities in m/s
        return (1./np.sqrt(2*np.pi*sigma*sigma) *
                np.exp(-(v_0 - Delta_v)*(v_0 - Delta_v)/(2*sigma*sigma) ))

    def smooth(velocities, power):
        # interpolate kernel and power curve to the same, regular velocity grid
        velocities_reg = np.linspace(-50., 50., 1001)
        power_reg = np.interp(velocities_reg, velocities, power)
        kernel_reg = kernel(velocities_reg)

        # convolve power and kernel
        # the downscaling is necessary because scipy expects the velocity
        # increments to be 1., but here, they are 0.1
        convolution = 0.1*fftconvolve(power_reg, kernel_reg, mode='same')

        # sample down so power curve doesn't get too long
        velocities_new = np.linspace(0., 35., 72)
        power_new = eta * np.interp(velocities_new, velocities_reg, convolution)

        return velocities_new, power_new

    turbine_new = turbine.copy()
    turbine_new['V'], turbine_new['POW'] = smooth(turbine['V'], turbine['POW'])

    if rescale is True:
        turbine_new['POW'] = (turbine_new['POW'] / np.max(turbine_new['POW'])
                             * np.max(turbine['POW']))

    return turbine_new
