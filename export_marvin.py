import sys, os
import numpy as np
import marvin
import csv

IFU = '9883-3701'

# Get datacube from Manga
print('Importing', IFU, 'from MaNGA Marvin...')
cube = marvin.tools.Cube(plateifu = IFU)
#cube = marvin.tools.Cube(plateifu = '8257-6103')

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
		temp = exported[side_len*i+j].tolist()
		label = str(j)+"-"+str(i)
		temp.insert(0, label)
		csv_list.append(temp)

with open(IFU+'.csv', 'w') as f:
	writer = csv.writer(f)
	writer.writerows(csv_list)