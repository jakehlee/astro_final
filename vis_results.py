import sys, os
import numpy as np
import matplotlib.pyplot as plt
import marvin
import csv

DEMUD_PATH = '/Users/Jake/Documents/GitHub/DEMUD/demud/results/cnn-k=50-dim=4563-full-init_item=svd-9883-3701/'
IFU = '9883-3701'
N = 5

demud_files = os.listdir(DEMUD_PATH)
recon = []
select = []
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

# Extract nocoverage map
ha = maps.emline_gflux_ha_6564
nocov = ha.pixmask.get_mask('NOCOV')

side_len = int(cube.header['NAXIS1'])

for n in range(N):
	name = selections[n][2]
	x = int(name.split('-')[0])
	y = int(name.split('-')[1])

	fig = plt.figure(figsize=(6,6))
	gs = fig.add_gridspec(2,2)
	ax_tl = fig.add_subplot(gs[0,0])
	ax_tr = fig.add_subplot(gs[0,1])
	ax_b = fig.add_subplot(gs[1,:])

	ax_marvin = im.plot()
	fig_marvin = ax_marvin.get_figure()
	ax_marvin.remove()

	ax_marvin.figure = fig
	fig.axes.append(ax_marvin)
	fig.add_axes(ax_marvin)
	#ax_marvin.set_position(ax_tl.get_position(original=True), which='both')
	#print(ax_tl.get_position(original=False))
	ax_marvin.set_position([0.12, 0.53, 0.35, 0.35])
	ax_tl.remove()
	plt.close(fig_marvin)

	# value/mask
	#value = np.zeros((side_len, side_len))
	value = np.full((side_len, side_len), ha.pixmask.labels_to_value('DONOTUSE'))
	value[y,x] = 1
	mask = nocov
	print(mask.tolist())

	marvin.utils.plot.map.plot(value=value, mask=mask, fig=fig, ax=ax_tr)

	ax_b.plot(xvals, recon[n], color='b', linewidth=0.5)
	ax_b.plot(xvals, select[n], color='g', linewidth=0.5)
	ax_b.fill_between(xvals, recon[n], select[n], color='r')


	plt.show()






