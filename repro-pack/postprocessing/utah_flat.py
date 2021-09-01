#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Contributors: Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the BSD 3-Clause license.

"""Postprocessing of Maya crude and gasoline above flat terrain in Utah.

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
from helpers import download_sat_image, interpolate, get_max_AMR_level

# paths
root_dir = pathlib.Path(__file__).expanduser().resolve().parents[2]
maya_dir = root_dir.joinpath("landspill-runs", "utah_maya")
gasoline_dir = root_dir.joinpath("landspill-runs", "utah_gasoline")
topo_path = root_dir.joinpath("landspill-runs", "common-files", "salt_lake_1.asc")
figs_dir = root_dir.joinpath("figs")
img_path = figs_dir.joinpath("utah-flat-sat.png")

# unified style configuration
pyplot.style.use(figs_dir.joinpath("paper.mplstyle"))

# times (in min)
T = [10, 30, 60, 120]
idx = [5, 15, 30, 60] # corresponding frame indices

# rupture point coords
center = [-12459650.,  4986000.]

# coordinates
x = numpy.linspace(center[0]-250, center[0]+250, 501)
y = numpy.linspace(center[1]-130, center[1]+80, 211)

# get image
extent = download_sat_image([x.min(), y.min(), x.max(), y.max()], img_path)
img = image.imread(img_path)

# read topo file
raster = rasterio.open(topo_path)
window = raster.window(*extent) # crop to the region in interest
topo = raster.read(1, window=window, boundless=True)
raster.close()

# mix image with topo and light source
ls = colors.LightSource(45, 25)
# shade = ls.shade_rgb(
#     img.astype(float), topo.astype(float), fraction=1.0, blend_mode='overlay',
#     vert_exag=1, dx=1, dy=1
# )
shade = ls.hillshade(topo.astype(float), vert_exag=5, dx=1, dy=1, fraction=1.0)

# plot
lvs1 = numpy.linspace(0., 0.27, 28)

fig, axs = pyplot.subplots(4, 2, figsize=(13, 11), sharex=True, sharey=True)

fig.suptitle("Maya crude oil and gasoline overland flow, flat terrain")

for i, (fno, t) in enumerate(zip(idx, T)):

    def reused_func(ax, title, output_dir):
        """To reduce duplicated code."""
        aux = True if output_dir.joinpath("fort.a{:04d}".format(fno+1)).is_file() else False
        soln = pyclaw.Solution(fno+1, path=output_dir, file_format="binary", read_aux=aux)
        maxlv = get_max_AMR_level(soln)
        vals = interpolate(soln, 0, x, y, maxlv)
        vals = numpy.ma.array(vals, mask=(vals<1e-3))

        # add the background setellite
        ax.imshow(shade, extent=[extent[0], extent[2], extent[1], extent[3]], cmap="gray", alpha=0.7)

        # target axes
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(title)
        ax.set_xlim(x.min(), x.max())
        ax.set_ylim(y.min(), y.max())
        ax.xaxis.get_major_formatter().set_useOffset(center[0])
        ax.xaxis.get_major_formatter().set_powerlimits((0, 3))
        ax.xaxis.get_offset_text().set_x(1.0)
        ax.yaxis.get_major_formatter().set_useOffset(center[1])
        ax.yaxis.get_major_formatter().set_powerlimits((0, 3))
        ax.yaxis.get_offset_text().set_x(-0.1)

        # contour
        csf = ax.contourf(x, y, vals, lvs1, extend="max")
        scatter = ax.scatter(center[0], center[1], s=100, c="w", ec="r", marker="o", lw=2)


        return csf, scatter

    # maya crude
    csf, scatter = reused_func(
        axs[i, 0], "Maya crude, T = {} min".format(t), maya_dir.joinpath("_output"))

    # gasoline
    csf, scatter = reused_func(
        axs[i, 1], "Gasoline, T = {} min".format(t), gasoline_dir.joinpath("_output"))

for i in range(3):
    pyplot.setp(axs[i, 0].get_xticklabels(), visible=False)
    pyplot.setp(axs[i, 1].get_xticklabels(), visible=False)

for i in range(2):
    axs[3, i].set_xlabel("x ($m$)")

for i in range(4):
    axs[i, 0].set_ylabel("y ($m$)")
    pyplot.setp(axs[i, 1].get_yticklabels(), visible=False)

fmt = matplotlib.ticker.ScalarFormatter(useMathText=True)
cbar = fig.colorbar(csf, ax=axs, format=fmt, shrink=0.85)
cbar.set_label("Depth ($m$)")
cbar.ax.yaxis.set_offset_position('left')
cbar.formatter.set_powerlimits((0, 0))
cbar.update_ticks()

fig.legend(
    [scatter], ["Pipeline rupture point"], loc='lower center',
    bbox_to_anchor=(0.48, 0.775), fontsize="large", framealpha=1.,
    edgecolor="k", facecolor="whitesmoke"
)

pyplot.savefig(figs_dir.joinpath("landspill-maya-gasoline-flat-terrain"))
