import sys, os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_pdf import PdfPages

import marvin
import csv

DEMUD_PATH = '/Users/Jake/Documents/GitHub/DEMUD/demud/results/cnn-k=50-dim=4563-full-init_item=svd-9883-3701/'
IFU = '9883-3701'
N = 20

demud_files = os.listdir(DEMUD_PATH)
recon = []
select = []
resid = []
selections = []
for file in demud_files:
	if 'recon-' in file:
		with open(os.path.join(DEMUD_PATH, file), 'r') as f:
			reader = csv.reader(f)
			for row in reader:
				recon.append(row)
		recon = np.array(recon).astype(np.float32)
	elif 'select-' in file:
		with open(os.path.join(DEMUD_PATH, file), 'r') as f:
			reader = csv.reader(f)
			for row in reader:
				select.append(row)
		select = np.array(select).astype(np.float32)
	elif 'resid-' in file:
		with open(os.path.join(DEMUD_PATH, file), 'r') as f:
			reader = csv.reader(f)
			for row in reader:
				resid.append(row)
		resid = np.array(resid).astype(np.float32)
	elif 'selections-' in file:
		with open(os.path.join(DEMUD_PATH, file), 'r') as f:
			reader = csv.reader(f)
			next(reader)
			for row in reader:
				selections.append(row)
		# no nparray conversion here.

# Pull imagery from marvin
im = marvin.tools.image.Image(IFU)
cube = marvin.tools.Cube(plateifu = IFU)
maps = marvin.tools.Maps(IFU)
xvals = np.array(cube.flux.wavelength.to_value()).astype(np.float32)
yunit = cube.flux.unit.to_string()
xunit = cube.flux.wavelength.unit.to_string()

# Extract nocoverage map
ha = maps.emline_gflux_ha_6564
nocov = ha.masked

side_len = int(cube.header['NAXIS1'])

pp = PdfPages(IFU+".pdf")

for n in range(N):
	name = selections[n][2]
	x = int(name.split('-')[0])
	y = int(name.split('-')[1])

	fig = plt.figure(figsize=(8.5,11))
	fig.suptitle(IFU + " DEMUD selection " + str(n))
	gs = fig.add_gridspec(3,2)
	ax_tl = fig.add_subplot(gs[0,0], projection=im.wcs)
	ax_tr = fig.add_subplot(gs[0,1])
	ax_m = fig.add_subplot(gs[1,:])
	ax_b = fig.add_subplot(gs[2,:])

	# reimplemented from marvin.tools.image.Image.plot()
	ax_tl.set_xlabel('Declination')
	ax_tl.set_ylabel('Right Ascension')
	ax_tl.imshow(im.data, origin='lower', aspect=None)

	# value/mask
	zeros = np.zeros((side_len, side_len))
	ones = np.full((side_len, side_len), 1)
	trans = np.zeros((side_len, side_len, 4))
	value = trans
	mask = nocov
	good = True
	if np.ma.is_masked(mask[y,x]):
		good = False
	if good:
		value[y,x] = [0, 0, 0, 1]
	else:
		value[y,x] = [255, 0, 0, 1]
	

	marvin.utils.plot.map.plot(dapmap=ha, value=ones, fig=fig, ax=ax_tr)
	ax_tr.images[-1].colorbar.remove()
	ax_tr.imshow(value, zorder=10)
	red_patch = mpatches.Patch(color='red', label='Bad spaxel')
	black_patch = mpatches.Patch(color='black', label='Valid spaxel')
	green_patch = mpatches.Patch(color='green', label='Valid region')

	fontP = FontProperties()
	fontP.set_size('small')
	ax_tr.legend(loc='upper left', bbox_to_anchor=(1, 1),
		handles=[green_patch, black_patch, red_patch], prop=fontP)

	ax_m.semilogy(xvals, recon[n], color='b', linewidth=0.5, label='Reconstruction')
	ax_m.semilogy(xvals, select[n], color='g', linewidth=0.5, label='Observed')
	ax_m.legend()
	ax_m.fill_between(xvals, recon[n], select[n], color='mistyrose')

	ax_m.set_xlabel(xunit)
	ax_m.set_ylabel(yunit)

	ax_b.plot(xvals, resid[n], color='r', linewidth=0.5, label='Residual')
	ax_b.legend()

	ax_b.set_xlabel(xunit)
	ax_b.set_ylabel(yunit)

	pp.savefig(fig)
	#if not os.path.isdir(IFU):
	#	os.mkdir(IFU)
	#plt.savefig(os.path.join(IFU, str(n)+'.png'), dpi=144)
	#plt.show()

pp.close()





