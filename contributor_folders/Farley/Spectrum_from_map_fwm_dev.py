# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 14:04:51 2024

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
from bokeh.plotting import show
hv.extension("bokeh")

results = earthaccess.search_data(
    short_name="PACE_OCI_L3M_RRS_NRT",
    granule_name="*.MO.*.1deg.*",
)
paths = earthaccess.open(results)

dataset = xr.open_dataset(paths[-1])


def single_band(w):
    array = dataset.sel({"wavelength": w})
    return hv.Image(array, kdims=["lon", "lat"], vdims=["Rrs"]).opts(aspect="equal", frame_width=450, frame_height=250, tools=['hover'])

image = single_band(368)

def spectrum(x, y):
    array = dataset.sel({"lon": x, "lat": y}, method="nearest")
    return hv.Curve(array, kdims=["wavelength"]).redim.range(Rrs=(-0.01, 0.04))

spectrum(0, 0)
