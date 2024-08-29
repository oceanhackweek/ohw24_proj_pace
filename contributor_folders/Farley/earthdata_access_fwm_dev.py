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

start_date = "2024-08-02"
end_date = "2024-08-12"

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


paths = earthaccess.open(results)[1:7]

#Get average values
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



wavelengths = average_per_dataset['wavelength'].data  # Use .data instead of .values
#dataset_indices = average_per_dataset['dataset_index'].data
rrs_values = average_per_dataset['Rrs'].values.T


rgb_dict = {}

for i in range(len(wavelengths)):
    wavelength = wavelengths[i]
    rrs = rrs_values[i, 0]
    rgb = wavelength_to_rgb(wavelength, gamma=rrs)
    rgb_dict[wavelength] = rgb