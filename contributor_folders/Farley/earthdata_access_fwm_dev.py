# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 10:59:54 2024

@author: fmiller
"""

#Acessing Earthdata OCI data

import earthaccess
import xarray as xr
#from xarray.backends.api import open_datatree
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np

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


auth = earthaccess.login(persist=True)

results = earthaccess.search_datasets(instrument="oci")

for item in results:
    summary = item.summary()
    print(summary["short-name"])
    
results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_RRS_NRT",
    count=1,
)

start_date = "2024-07-01"
end_date = "2024-07-10"

lon_east = -160
lat_south = 30
lon_west = -150 
lat_north = 33
cloud_max = 50

tspan = (start_date, end_date)
bbox = (lon_east, lat_south, lon_west, lat_north)
clouds = (0, cloud_max)

results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_RRS_NRT",
    temporal=tspan,
    bounding_box=bbox,
    granule_name="*.DAY.*.0p1deg.*",
)

paths = earthaccess.open(results)[0:10]

#Get average values

# Open all datasets at once and concatenate along a new dimension
datasets = xr.open_mfdataset(paths, concat_dim="dataset_index", combine="nested", parallel=True)

# Subset the datasets within the specified region
subset = datasets.sel(lon=slice(-165, -156), lat=slice(30, 20))

# Calculate the mean Rrs value across the subset for each wavelength
average_subset = subset.mean(dim=['lon', 'lat'])

wavelengths = average_subset['wavelength'].data  # Use .data instead of .values
dataset_indices = average_subset['dataset_index'].data
rrs_values = average_subset['Rrs'].values.T


rgb_dict = {}

for i in range(len(wavelengths)):
    wavelength = wavelengths[i]
    rrs = rrs_values[i, 0]
    rgb = wavelength_to_rgb(wavelength, gamma=rrs)
    rgb_dict[wavelength] = rgb