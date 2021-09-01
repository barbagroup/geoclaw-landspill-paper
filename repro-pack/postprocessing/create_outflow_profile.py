#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the BSD 3-Clause license.

"""Create a figure that shows the outflow profile."""
import pathlib
import matplotlib
import matplotlib.pyplot as pyplot

# paths
root_dir = pathlib.Path(__file__).expanduser().resolve().parents[2]
figs_dir = root_dir.joinpath("figs")

# unified style configuration
pyplot.style.use(figs_dir.joinpath("paper.mplstyle"))

# figure
fig: matplotlib.figure.Figure; ax: matplotlib.axes.Axes
fig, ax = pyplot.subplots(figsize=(6.5, 3))

ax.plot([0.5, 0.], [0.5, 0.5], "k-", lw=3)
ax.plot([0.5, 0.5], [0.5, 0.1], "k-", lw=3)
ax.plot([0.5, 3.5], [0.1, 0.1], "k-", lw=3)
ax.plot([3.5, 3.5], [0.1, 0.0], "k-", lw=3)
ax.plot([3.5, 8.0], [0.0, 0.0], "k-", lw=3)

ax.set_xticks([0., 0.5, 3.5, 8.0])
ax.set_xlabel("Time from rupture (hours)")

ax.set_ylim(-0.05, 0.6)
ax.set_yticks([0., 0.1, 0.5])
ax.set_ylabel("Flow rate (" + r"$m^3 / second$" + ")")

fig.suptitle("Outflow profile at the pipeline rupture point")
pyplot.savefig(figs_dir.joinpath("landspill-outflow-profile"))
