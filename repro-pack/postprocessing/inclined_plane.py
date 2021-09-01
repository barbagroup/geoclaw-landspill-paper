#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Contributors: Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the BSD 3-Clause license.

"""Plot figures for silicone oil on an inclined plane of 2.5 degree.

Requires the environment variable PYTHONPATH and CLAW to point to clawpack.
"""
import os
import pathlib
import numpy
import matplotlib
from matplotlib import pyplot
from clawpack import pyclaw
from helpers import get_max_AMR_level, interpolate

# paths
root_dir = pathlib.Path(__file__).expanduser().resolve().parents[2]
case_dir = root_dir.joinpath("repro-pack", "runs", "silicone-oil-inclined-plane")
output_dir = case_dir.joinpath("_output")
figs_dir = root_dir.joinpath("figs")

# unified style configuration
pyplot.style.use(figs_dir.joinpath("paper.mplstyle"))

# times
T = [32, 59, 122, 271, 486, 727]

# coordinates
x = numpy.linspace(-0.2, 1.0, 601)
y = numpy.linspace(-0.3, 0.3, 301)

# load validation data first
lister = []
for i, t in enumerate(T):
    lister.append(numpy.loadtxt(
        case_dir.joinpath("lister_1992", "T={}.csv".format(t)),
        delimiter=',', skiprows=1
    ))

# plot
lvs1 = numpy.linspace(1e-3, 5e-3, 9)
lvs2 = numpy.linspace(1e-3, 5e-3, 5)
lvs3 = numpy.linspace(1e-3, 5e-3, 9)
lvs4 = numpy.linspace(1e-3, 5e-3, 5)

fig = pyplot.figure(figsize=(13, 10.5))
gs = fig.add_gridspec(3, 3, width_ratios=[4.875, 4.875, 0.25], height_ratios=[1, 1, 1])

zoomed_axs = []
zoomed_axs.append(fig.add_subplot(gs[0, 0])) # T=32
zoomed_axs.append(fig.add_subplot(gs[0, 1], sharey=zoomed_axs[0])) # T=59

axs = []
axs.append(fig.add_subplot(gs[1, 0])) # T=122
axs.append(fig.add_subplot(gs[1, 1], sharey=axs[0])) # T=271
axs.append(fig.add_subplot(gs[2, 0], sharex=axs[0])) # T=486
axs.append(fig.add_subplot(gs[2, 1], sharex=axs[1], sharey=axs[2])) # T=727

cbars_axs = []
cbars_axs.append(fig.add_subplot(gs[0, 2])) # colorbar for T=32 & 59
cbars_axs.append(fig.add_subplot(gs[1:, 2])) # colorbar for remaining plots

# T=32 & 59
# ----------
for i, t in enumerate([32, 59]):
    aux = True if output_dir.joinpath("fort.a{:04d}".format(i+1)).is_file() else False
    soln = pyclaw.Solution(i+1, path=output_dir, file_format="binary", read_aux=aux)
    maxlv = get_max_AMR_level(soln)
    vals = interpolate(soln, 0, x, y, maxlv)
    vals = numpy.ma.array(vals, mask=(vals<1e-3))

    # target axes
    ax = zoomed_axs[i]
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("T = {} sec".format(t))
    ax.set_xlim(-0.1, 0.5)
    ax.set_ylim(-0.15, 0.15)

    # contour
    csf = ax.contourf(x, y, vals, lvs1, extend="max")
    cs = ax.contour(x, y, vals, lvs2, colors='black', linewidths=0.75)
    ax.clabel(cs, lvs2, fmt="%1.0e", inline_spacing=15, fontsize="small")

    # validation data
    scatter = ax.scatter(
        lister[i][:, 0], lister[i][:, 1], s=150, fc="whitesmoke", ec='darkred',
        marker="v", linewidths=2.5, zorder=9
    )

pyplot.setp(zoomed_axs[1].get_yticklabels(), visible=False)
zoomed_axs[0].set_xlabel("x ($m$)")
zoomed_axs[1].set_xlabel("x ($m$)")
zoomed_axs[0].set_ylabel("y ($m$)")

fmt = matplotlib.ticker.ScalarFormatter(useMathText=True)
cbar1 = fig.colorbar(csf, cax=cbars_axs[0], ax=zoomed_axs, format=fmt, shrink=1.0)
cbar1.set_label("Oil depth ($m$)")
cbar1.set_ticks(lvs2)
cbar1.ax.tick_params(labelsize="small")
cbar1.ax.yaxis.set_offset_position('left')
cbar1.formatter.set_powerlimits((0, 0))
cbar1.update_ticks()

# T=122, 271, 486 & 727
# ---------------------
for i, t in enumerate([122, 271, 486, 727]):

    i += 2 # shift 2 because T=32 and T=59
    aux = True if output_dir.joinpath("fort.a{:04d}".format(i+1)).is_file() else False
    soln = pyclaw.Solution(i+1, path=output_dir, file_format="binary", read_aux=aux)
    maxlv = get_max_AMR_level(soln)
    vals = interpolate(soln, 0, x, y, maxlv)
    vals = numpy.ma.array(vals, mask=(vals<1e-3))

    # target axes
    ax = axs[i-2] # remember to shift i back to zero-based
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("T = {} sec".format(t))
    ax.set_xlim(-0.2, 1.0)
    ax.set_ylim(-0.3, 0.3)

    # contour
    csf = ax.contourf(x, y, vals, lvs3, extend="max")
    cs = ax.contour(x, y, vals, lvs4, colors='black', linewidths=0.75)
    ax.clabel(cs, lvs4, fmt="%1.0e", inline_spacing=15, fontsize="small")

    # validation data
    scatter = ax.scatter(
        lister[i][:, 0], lister[i][:, 1], s=150, fc="whitesmoke", ec='darkred',
        marker="v", linewidths=2.5, zorder=9
    )

pyplot.setp(axs[0].get_xticklabels(), visible=False)
pyplot.setp(axs[1].get_xticklabels(), visible=False)
pyplot.setp(axs[1].get_yticklabels(), visible=False)
pyplot.setp(axs[3].get_yticklabels(), visible=False)
axs[2].set_xlabel("x ($m$)")
axs[3].set_xlabel("x ($m$)")
axs[0].set_ylabel("y ($m$)")
axs[2].set_ylabel("y ($m$)")

fmt = matplotlib.ticker.ScalarFormatter(useMathText=True)
cbar2 = fig.colorbar(csf, cax=cbars_axs[1], ax=axs, format=fmt, shrink=1.0)
cbar2.set_label("Oil depth ($m$)")
cbar2.set_ticks(lvs4)
cbar2.ax.tick_params(labelsize="small")
cbar2.ax.yaxis.set_offset_position('left')
cbar2.formatter.set_powerlimits((0, 0))
cbar2.update_ticks()

fig.legend(
    [scatter], ["Experimental data (Lister, 1992)"], loc='upper left',
    bbox_to_anchor=(0.175, 0.93), fontsize="large", framealpha=1.,
    edgecolor="k", facecolor="whitesmoke"
)

fig.suptitle("Silicone oil on an inclined plane, 2.5\u00b0, "+r"$1.48\times 10^3 mm^3/s$")
pyplot.savefig(figs_dir.joinpath("landspill-silicone-inclined-plane"))
