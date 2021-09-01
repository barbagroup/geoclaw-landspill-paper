#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Contributors: Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the BSD 3-Clause license.

"""Postprocessing.
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
maya_dir = root_dir.joinpath("landspill-runs", "utah_hydrofeatures_maya")
topo_path = root_dir.joinpath("landspill-runs", "common-files", "salt_lake_2.asc")
figs_dir = root_dir.joinpath("figs")
img_path = figs_dir.joinpath("utal-hydro.png")

# unified style configuration
pyplot.style.use(figs_dir.joinpath("paper.mplstyle"))

# read in removed fluid data at land-water intersection
rmvd = numpy.loadtxt(maya_dir.joinpath("_output", "removed_fluid.csv"), delimiter=",")

# times (in min)
T = [90]
idx = [45] # corresponding frame indices

# rupture point coords
center = [-12460209.5, 4985137.4]

# coordinates
x = numpy.linspace(center[0]-150, center[0]+150, 301)
y = numpy.linspace(center[1]-150, center[1]+150, 301)

# get image
extent = download_sat_image([x.min(), y.min(), x.max(), y.max()], img_path)
img = image.imread(img_path)

# read topo file
raster = rasterio.open(topo_path)
window = raster.window(*extent) # crop to the region in interest
topo = raster.read(1, window=window, boundless=True)
raster.close()

# mix image with topo and light source
ls = colors.LightSource(300, 45)
shade = ls.shade_rgb(
    img.astype(float), topo.astype(float), fraction=1.0, blend_mode='overlay',
    vert_exag=5, dx=1, dy=1
)

# plot
lvs1 = 16


fig = pyplot.figure(figsize=(13, 6.5))
gs = fig.add_gridspec(1, 3, width_ratios=[4.875, 0.25, 4.875])

axs = []
axs.append(fig.add_subplot(gs[0]))
axs.append(fig.add_subplot(gs[2], projection="3d"))
cbarax = fig.add_subplot(gs[1])

# no need to do a loop, but just to match the pattern of other scripts...
for i, (fno, t) in enumerate(zip(idx, T)):

    def reused_func(ax, title, output_dir):
        """To reduce duplicated code."""
        aux = True if output_dir.joinpath("fort.a{:04d}".format(fno+1)).is_file() else False
        soln = pyclaw.Solution(fno+1, path=output_dir, file_format="binary", read_aux=aux)
        maxlv = get_max_AMR_level(soln)
        vals = interpolate(soln, 0, x, y, maxlv)
        vals = numpy.ma.array(vals, mask=(vals<1e-3))

        # add the background setellite
        ax.imshow(shade, extent=[extent[0], extent[2], extent[1], extent[3]], alpha=0.7)

        # target axes
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(title)
        ax.set_xticks(numpy.arange(x.min(), x.max()+1, 50.))
        ax.set_yticks(numpy.arange(y.min(), y.max()+1, 50.))
        ax.set_xlim(x.min(), x.max())
        ax.set_ylim(y.min(), y.max())
        ax.xaxis.get_major_formatter().set_useOffset(center[0])
        ax.xaxis.get_major_formatter().set_powerlimits((0, 5))
        ax.yaxis.get_major_formatter().set_useOffset(center[1])
        ax.yaxis.get_major_formatter().set_powerlimits((0, 5))
        ax.yaxis.get_offset_text().set_x(-0.2)

        # contour
        csf = ax.contourf(x, y, vals, lvs1, extend="max")
        scatter = ax.scatter(center[0], center[1], s=100, c="w", ec="r", marker="o", lw=2)

        return csf, scatter

    # maya crude
    csf, scatter1 = reused_func(
        axs[0], "T = {} min".format(t), maya_dir.joinpath("_output"))

    # oil-water intersections
    scatter2 = axs[0].scatter(rmvd[:, 0], rmvd[:, 1], s=50, c='w', ec="k", marker="o", lw=0.5, alpha=0.6)

axs[0].set_ylabel("y ($m$)")
axs[0].set_xlabel("x ($m$)")

fmt = matplotlib.ticker.ScalarFormatter(useMathText=True)
cbar = fig.colorbar(csf, cax=cbarax, ax=axs[0], format=fmt)
cbar.set_label("Depth ($m$)")
cbar.ax.yaxis.set_offset_position('left')
cbar.formatter.set_powerlimits((0, 0))
cbar.update_ticks()

axs[0].legend(
    [scatter1, scatter2], ["Pipeline rupture point", "Oil-water contact points"],
    loc='upper right', bbox_to_anchor=(1.0, 1.0), fontsize="large", framealpha=1.,
    edgecolor="k", facecolor="whitesmoke"
)



# 3D bar plots on the right
# --------------------------
axs[1].set_title("Removed oil volume at contact points") #, fontsize=10, pad=10)
axs[1].view_init(40, 290)
axs[1].dist = 11

X, Y = numpy.meshgrid(
    numpy.linspace(extent[0], extent[2], img.shape[1]),
    numpy.linspace(extent[3], extent[1], img.shape[0])
)

axs[1].plot_surface(X, Y, numpy.zeros_like(X), facecolors=shade, rcount=200, ccount=200)

axs[1].bar3d(
    rmvd[:, 0], rmvd[:, 1], numpy.zeros_like(rmvd[:, 0]),
    6, 6, rmvd[:, 3], shade=True, lightsource=colors.LightSource(180, 35),
    alpha=0.5, color="tab:cyan"
)


pyplot.setp(axs[1].get_xticklabels(), visible=False)
axs[1].xaxis.get_major_formatter().set_useOffset(False)
axs[1].xaxis.get_major_formatter().set_powerlimits((0, 10))
axs[1].set_xlim(x.min(), x.max())

pyplot.setp(axs[1].get_yticklabels(), visible=False)
axs[1].yaxis.get_major_formatter().set_useOffset(False)
axs[1].yaxis.get_major_formatter().set_powerlimits((0, 10))
axs[1].set_ylim(y.min(), y.max())

axs[1].set_zlabel(r"Oil volume ($\times 10\ m^3$)")#, fontsize=8)
axs[1].grid(False)

fig.suptitle("Maya crude oil overland flow, oil-water contact points")
pyplot.savefig(figs_dir.joinpath("landspill-maya-hydro.pdf"))
