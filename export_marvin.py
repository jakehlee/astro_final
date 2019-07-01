import sys, os
import numpy as np
import marvin
import csv

IFU = '9871-12705'

ATTRS = [
	"emline_gflux_oii_3727",
	"emline_gflux_oii_3729",
	"emline_gflux_hthe_3798",
	"emline_gflux_heta_3836",
	"emline_gflux_neiii_3869",
	"emline_gflux_hzet_3890",
	"emline_gflux_neiii_3968",
	"emline_gflux_heps_3971",
	"emline_gflux_hdel_4102",
	"emline_gflux_hgam_4341",
	"emline_gflux_heii_4687",
	"emline_gflux_hb_4862",
	"emline_gflux_oiii_4960",
	"emline_gflux_oiii_5008",
	"emline_gflux_hei_5877",
	"emline_gflux_oi_6302",
	"emline_gflux_oi_6365",
	"emline_gflux_nii_6549",
	"emline_gflux_ha_6564",
	"emline_gflux_nii_6585",
	"emline_gflux_sii_6718",
	"emline_gflux_sii_6732"
]

# Get datacube from Manga
print('Importing', IFU, 'from MaNGA Marvin...')
cube = marvin.tools.Cube(plateifu = IFU)
maps = marvin.tools.Maps(IFU)
ha = maps.emline_gflux_ha_6564

for attr in ATTRS:
	curr_ha = getattr(maps, attr)
	ha = ha + curr_ha

nocov = ha.masked.mask

# Get spectra (flux)
flux = cube.flux

# Confirm quality
if cube.quality_flag.bits != []:
	print("Warning: not good quality")

assert int(cube.header['NAXIS1']) == int(cube.header['NAXIS2']), "DataCube not square!"

side_len = int(cube.header['NAXIS1'])
feat_len = int(cube.header['NAXIS3'])
print(side_len, feat_len)

# xvals
xvals = flux.wavelength.to_value()

print('Exporting to csv...')

# Initialize data
exported = np.zeros((side_len ** 2, feat_len))

for i in range(side_len):
	for j in range(side_len):
		exported[side_len*i+j] = flux[:,i,j].to_value()

# label for export
# we're going to do x-y since comma is used for csv
csv_list = []
for i in range(side_len):
	for j in range(side_len):
		# if masked data, do not export
		if nocov[i,j]:
			continue
		temp = exported[side_len*i+j].tolist()
		label = str(j)+"-"+str(i)
		temp.insert(0, label)
		csv_list.append(temp)

with open(IFU+'.csv', 'w') as f:
	writer = csv.writer(f)
	writer.writerows(csv_list)