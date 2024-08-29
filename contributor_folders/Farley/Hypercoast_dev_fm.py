# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 09:03:29 2024

@author: fmiller
"""
#Here we will experiment with hypercoast

import os

from holoviews.streams import Tap
from matplotlib import animation
from matplotlib.colors import ListedColormap
from PIL import Image, ImageEnhance
from scipy.ndimage import gaussian_filter1d
#from xarray.backends.api import open_datatree
import cartopy.crs as ccrs
import cmocean
import earthaccess
import holoviews as hv
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
import numpy as np
import panel.widgets as pnw
import xarray as xr
hv.extension("bokeh")
import hypercoast
import colour
import colormath
from colormath.color_objects import SpectralColor
from colormath.color_conversions import convert_color

#Load in example data
#TODO make it work with our data!
#Import dataset from EarthAcess

def wavelength_to_rgb(wavelength, gamma=0.8):

    '''This converts a given wavelength of light to an 
    approximate RGB color value. The wavelength must be given
    in nanometers in the range from 380 nm through 750 nm
    (789 THz through 400 THz).
    Based on code by Dan Bruton
    http://www.physics.sfasu.edu/astro/color/spectra.html
    '''

    wavelength = float(wavelength)
    if wavelength >= 380 and wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
        R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
        G = 0.0
        B = (1.0 * attenuation) ** gamma
    elif wavelength >= 440 and wavelength <= 490:
        R = 0.0
        G = ((wavelength - 440) / (490 - 440)) ** gamma
        B = 1.0
    elif wavelength >= 490 and wavelength <= 510:
        R = 0.0
        G = 1.0
        B = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif wavelength >= 510 and wavelength <= 580:
        R = ((wavelength - 510) / (580 - 510)) ** gamma
        G = 1.0
        B = 0.0
    elif wavelength >= 580 and wavelength <= 645:
        R = 1.0
        G = (-(wavelength - 645) / (645 - 580)) ** gamma
        B = 0.0
    elif wavelength >= 645 and wavelength <= 750:
        attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
        R = (1.0 * attenuation) ** gamma
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0
    R *= 255
    G *= 255
    B *= 255
    return (int(R), int(G), int(B))

import hypercoast
import pyvista

auth = earthaccess.login(persist=True)

results = earthaccess.search_datasets(instrument="oci")

tspan = ("2024-07-01", "2024-08-25")
bbox = (-170, 23, -140, 33)

results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_CHL_NRT",
    temporal=tspan,
    bounding_box=bbox,
    granule_name="*.DAY.*.4km.*",
)

paths = earthaccess.open(results)[35:38]

# Use dask for lazy loading
combined_datasets = []

# Iterate over all the datasets
for i in range(1, len(paths)):
    # Open dataset without specifying chunks
    dataset = xr.open_dataset(paths[i])  # Load the dataset first

    # Rechunk the dataset after loading
    dataset = dataset.chunk({'lon': 'auto', 'lat': 'auto'})  # Use 'auto' or set specific sizes
    
    # Subset the dataset within the specified region and append to list
    subset = dataset.sel(lon=slice(-159.5, -157.5), lat=slice(27.5, 26))
    combined_datasets.append(subset)

# Concatenate all subsets along the 'dataset' dimension
combined_dataset = xr.concat(combined_datasets, dim='dataset')

# Calculate the mean Rrs value across lon and lat for each dataset
average_per_dataset = combined_dataset.mean(dim=['lon', 'lat'])

#Check dimentions
combined_dataset.dims
combined_dataset['chlor_a'].values

p = hypercoast.image_cube(
    combined_dataset,
    variable="chlor_a",
    cmap="jet",
    clim=(0, 0.5),
    rgb_wavelengths=[1000, 700, 500],
    rgb_gamma=2,
    widget="slice",
)
#p.add_text("Band slicing ", position="upper_right", font_size=14)
p.show()



######## Below we try for the single spectrum plot!

# # #We use L2 AOP data
results = earthaccess.search_datasets(instrument="oci")


results = earthaccess.search_data(
    short_name="PACE_OCI_L2_AOP_NRT",
    count = 1,
)

paths = earthaccess.open(results)

# Open the dataset

dataset = hypercoast.read_pace(paths[0])

dataset.dims

hypercoast.viz_pace(dataset, wavelengths=[500, 510, 520, 530], ncols=2)


latitude = 25.493961
longitude = -91.25617
hypercoast.filter_pace(dataset, latitude, longitude, return_plot=True)
