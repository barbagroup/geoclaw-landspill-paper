#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Contributors: Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the BSD 3-Clause license.

"""Postprocessing of Maya crude at hill terrain in Utah.

Requires the environment variable PYTHONPATH and CLAW to point to clawpack.
"""
import os
import pathlib
import numpy
import rasterio
import matplotlib
from matplotlib import image
from matplotlib import pyplot
from matplotlib import colors
from clawpack import pyclaw
from helpers import download_sat_image, interpolate, get_max_AMR_level, get_AMR_borders

# paths
root_dir = pathlib.Path(__file__).expanduser().resolve().parents[2]
maya_dir = root_dir.joinpath("landspill-runs", "utah_hill_maya")
topo_path = root_dir.joinpath("landspill-runs", "common-files", "utah_hill.asc")
figs_dir = root_dir.joinpath("figs")
img_path = figs_dir.joinpath("utah-hill-sat.png")

# unified style configuration
pyplot.style.use(figs_dir.joinpath("paper.mplstyle"))

# times (in min)
T = [2, 10, 60, 120]
idx = [1, 5, 30, 60] # corresponding frame indices

# rupture point coords
center = [-12443619., 4977641.]

# coordinates
x = numpy.linspace(center[0]-50, center[0]+350, 401)
y = numpy.linspace(center[1]-650, center[1]+150, 801)

# get image (not used here, but just in case ...)
extent = download_sat_image([x.min(), y.min(), x.max(), y.max()], img_path)
img = image.imread(img_path)

# read topo file
raster = rasterio.open(topo_path)
window = raster.window(*extent) # crop to the region in interest
topo = raster.read(1, window=window, boundless=True)
raster.close()

# mix image with topo and light source
ls = colors.LightSource(345, 35)
shade = ls.hillshade(topo.astype(float), vert_exag=5, dx=1, dy=1, fraction=1.0)

# plot
lvs1 = numpy.linspace(0., 0.75, 13)

fig, axs = pyplot.subplots(1, 4, figsize=(13, 6.3), sharey=True)

fig.suptitle("Maya crude oil overland flow, hill area")

for i, (fno, t) in enumerate(zip(idx, T)):

    def reused_func(ax, title, output_dir):
        """To reduce duplicated code."""
        aux = True if output_dir.joinpath("fort.a{:04d}".format(fno+1)).is_file() else False
        soln = pyclaw.Solution(fno+1, path=output_dir, file_format="binary", read_aux=aux)
        maxlv = get_max_AMR_level(soln)
        limits = get_AMR_borders(soln, maxlv)
        vals = interpolate(soln, 0, x, y, maxlv)
        vals = numpy.ma.array(vals, mask=(vals<1e-3))

        # add the background setellite
        ax.imshow(shade, extent=[extent[0], extent[2], extent[1], extent[3]], cmap="gray", alpha=0.7)

        # target axes
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(title)
        ax.set_xlim(x.min(), x.max())
        ax.set_ylim(y.min(), y.max())
        ax.set_xticks(numpy.arange(center[0], x.max(), 100))
        ax.set_yticks(numpy.arange(center[1]-600, y.max(), 100))
        ax.xaxis.get_major_formatter().set_useOffset(center[0])
        ax.xaxis.get_major_formatter().set_powerlimits((0, 3))
        ax.xaxis.get_offset_text().set_x(1.0)
        ax.yaxis.get_major_formatter().set_useOffset(center[1])
        ax.yaxis.get_major_formatter().set_powerlimits((0, 3))
        ax.yaxis.get_offset_text().set_x(-0.5)

        # contour
        csf = ax.contourf(x, y, vals, lvs1, extend="max")
        scatter = ax.scatter(center[0], center[1], s=100, c="w", ec="r", marker="o", lw=2)

        # AMR patchs' borders
        for p in limits:
            ax.plot(
                [p[0], p[1], p[1], p[0], p[0]],
                [p[2], p[2], p[3], p[3], p[2]],
                lw = 1, color="k", ls="-", alpha=0.6
            )

        return csf, scatter

    # maya crude
    csf, scatter = reused_func(axs[i], "T = {} min".format(t), maya_dir.joinpath("_output"))

axs[0].set_ylabel("y ($m$)")
for i in range(1, 4):
    pyplot.setp(axs[i].get_yticklabels(), visible=False)

for i in range(4):
    axs[i].set_xlabel("x ($m$)")
    axs[i].xaxis.labelpad = 20 # move the x-axis label down

fmt = matplotlib.ticker.ScalarFormatter(useMathText=True)
cbar = fig.colorbar(csf, ax=axs, format=fmt, shrink=0.85)
cbar.set_label("Depth ($m$)")
cbar.ax.yaxis.set_offset_position('left')
cbar.formatter.set_powerlimits((0, 0))
cbar.update_ticks()

fig.legend(
    [scatter], ["Pipeline rupture point"], loc='lower center',
    bbox_to_anchor=(0.48, 0.2), fontsize="large", framealpha=1.,
    edgecolor="k", facecolor="whitesmoke"
)

pyplot.savefig(figs_dir.joinpath("landspill-maya-hill"))
