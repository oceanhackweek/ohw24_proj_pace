# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 13:31:20 2024

@author: fmiller
"""
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
from scipy.ndimage import convolve

def enhancel3(rgb, scale = .01, vmin = 0.01, vmax = 1.02, gamma=.95, contrast=1.5, brightness=1.02, sharpness=2, saturation=1.1):
   
    rgb = rgb.where(rgb > 0)
    rgb = np.log(rgb / scale) / np.log(1 / scale)
    rgb = (rgb -  rgb.min()) / (rgb.max() - rgb.min())
    rgb = rgb * gamma
    img = rgb * 255
    img = img.where(img.notnull(), 0).astype("uint8")
    img = Image.fromarray(img.data)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast)
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(brightness)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(sharpness)
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(saturation)
    rgb[:] = np.array(img) / 255    
    return rgb


results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_RRS_NRT",
    granule_name="*.MO.*.0p1deg.*",
)
paths = earthaccess.open(results)

dataset = xr.open_dataset(paths[-1])

rrs_rgb = dataset["Rrs"].sel({"wavelength": [645, 555, 368]})
rrs_rgb

rrs_rgb["channel"] = ("wavelength", ["Reds", "Greens", "Blues"])
rrs_rgb = rrs_rgb.swap_dims({"wavelength": "channel"})
rrs_rgb

rrs_rgb_enhanced = enhancel3(rrs_rgb)

artist = rrs_rgb.plot.imshow(x="lon", y="lat")
plt.gca().set_aspect("equal")