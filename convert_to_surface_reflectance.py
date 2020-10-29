#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import geopandas as gpd
import folium
import os, shutil
import re
from glob import glob
import requests
from bs4 import BeautifulSoup
import rasterio as rio
from rasterio.plot import show
from rasterio.enums import Resampling
import matplotlib.pyplot as plt


# In[2]:


# given Landsat path and row inputs, creates a dictionary of dictionaries 
# for each bandset stored locally that matches the path/row, where 1) first key is shorthand
# for the bandset (particular date and tile) & value is the file directory; and 2) 
# second key is shorthand for each band in the respective bandsets & value is the image file

def format_pathrow(x):
    if type(x) == int:
        x = str(x)    
    if type(x) == str: 
        if len(x) == 1: 
            new_x = '00' + x
        elif len(x) == 2: 
            new_x = '0' + x
        elif len(x) == 3:
            new_x = x
        else: 
            return 'It looks like your input has too many digits.'
    return new_x

def get_bandsets(sat_path, sat_row):
    sat_path = format_pathrow(sat_path)
    sat_row = format_pathrow(sat_row)
    sat_pathrow = sat_path + sat_row
    bands = {}
    basepath = '.\Landsat8' 
    
    bandsets = []
    
    for dir_name in os.listdir(basepath):
        path = os.path.join(basepath, dir_name)
        if os.path.isdir(path):
            if sat_pathrow in dir_name:
                bandsets.append(dir_name)    
    return bandsets

def get_bands(sat_path, sat_row):
    bandsets = get_bandsets(sat_path, sat_row)
    dictionaries = {}
    for bandset in bandsets: 
        bandset_dict = {}
        entity_dir = os.path.join('.\Landsat8', bandset)
        for i in range(1, 12):
            band_file = os.path.join(entity_dir, (bandset + '_B{}'.format(i)))
            band_dict = {'band{}_file'.format(i): band_file}
            bandset_dict.update(band_dict)
        mini_dict = {bandset: bandset_dict}
        dictionaries.update(mini_dict)
    return dictionaries

# okay! we're now ready to start pre-processing these images


# **Formula for converting raw band images to top of atmosphere (TOA) radiance:** \
# \
# $L_{λ} = (M_{L})(Q_{cal}) + A_{L}$ \
# \
# **where** \
# \
# **$L_{λ}$** = TOA spectral radiance $(Watts/( m^{2} * srad * μm))$ \
# **$M_{L}$** = the band-specific multiplicative rescaling factor from the metadata (RADIANCE_MULT_BAND_x, where x is the band number) \
# **$Q_{cal}$** = the quantized and calibrated standard product pixel values (DN) \
# **$A_{L}$** = the band-specific additive rescaling factor from the metadata (RADIANCE_ADD_BAND_x, where x is the band number)

# In[ ]:


# converts DN raw band images to TOA radiance images

# def toa_radiance(sat_path, sat_row, bandset):
#     bands_of_interest = get_bands(sat_path, sat_row)[bandset]
#     entity_dir = os.path.join('.\Landsat8', bandset)
#     #L = (M * Q) + A 
#     for band in bands_of_interest:
#         band_num = int(re.search(r'\d+', band).group(0))
#         print(band_num)
        
#         # get multiplicative and additive rescaling factors from the metadata file
#         M = ''
#         A = ''
#         with open(entity_dir + '\\' + bandset + '_MTL.txt') as meta_file:
#             meta_lines = meta_file.readlines()
#             for line in meta_lines:
#                 if 'RADIANCE_MULT_BAND_{} '.format(band_num) in line: 
#                     M = line.split('= ', 1)[1]
#                 if 'RADIANCE_ADD_BAND_{} '.format(band_num) in line: 
#                     A = line.split('= ', 1)[1]
#         M = float(M)
#         A = float(A)
#         print(M, A)
        
#         band_file = rio.open(band, 'r')
#         raster = band_file.read(1)
                
# toa_radiance(37, 36, 'LC08_L1TP_037036_20200402_20200410_01_T1')

test = get_bands(37, 36)['LC08_L1TP_037036_20200402_20200410_01_T1']

test_file = test['band1_file']

dude = rio.open(test_file)


# In[ ]:


# for this script, we only care about the majority of coconino national forest

coconino_bandsets = get_bands(37, 36)

for bandset in coconino_bandsets:
    print(bandset)
    
# and we'll just classify the image taken on 2020-04-02

coconino_bandset = coconino_bandsets['LC08_L1TP_037036_20200402_20200410_01_T1']

print(coconino_bandset)

