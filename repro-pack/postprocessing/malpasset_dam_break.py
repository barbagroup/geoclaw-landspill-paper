#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the BSD 3-Clause license.

"""Post-processing of Malpasset dam break."""
# pylint: disable=protected-access, too-many-statements
import pathlib
import numpy
from gclandspill import pyclaw
from gclandspill._postprocessing.plotdepth import plot_topo_on_ax, plot_soln_frame_on_ax
from gclandspill._postprocessing.calc import get_soln_max
from gclandspill._misc import import_setrun
from matplotlib import pyplot, cm

# absolute paths
repo_dir = pathlib.Path(__file__).expanduser().resolve().parents[2]
fig_dir = repo_dir.joinpath("figs")
case_dir = {
    "geoclaw": repo_dir.joinpath("repro-pack", "runs", "malpasset-dam-break-geoclaw"),
    "landspill": repo_dir.joinpath("repro-pack", "runs", "malpasset-dam-break-landspill")
}

# try to use a specific style
try:
    pyplot.style.use(fig_dir.joinpath("paper.mplstyle"))
except FileNotFoundError:
    pass

# electrical transformers
elec_trans = {"A": (5500, 4400), "B": (11900, 3250), "C": (13000, 2700)}

# police field survey points
field_pts = {
    1: (4913.1, 4244.0), 2: (5159.7, 4369.6), 3: (5790.6, 4177.7), 4: (5886.5, 4503.9), 5: (6763.0, 3429.6),
    6: (6929.9, 3591.8), 7: (7326.0, 2948.7), 8: (7451, 3232.1), 9: (8735.9, 3264.6), 10: (8628.6, 3604.6),
    11: (9761.1, 3480.3), 12: (9832.9, 2414.7), 13: (10957.2, 2651.9), 14: (11115.7, 3800.7), 15: (11689, 2592.3),
    16: (11626, 3406.8), 17: (12333.7, 2269.7)
}

# lab scaled model gauge points
model_pts = {
    6: (4947.4, 4289.7), 7: (5717.3, 4407.6), 8: (6775.1, 3869.2), 9: (7128.2, 3162), 10: (8585.3, 3443.1),
    11: (9675, 3085.9), 12: (10939.1, 3044.8), 13: (11724.4, 2810.4), 14: (12723.7, 2485.1)
}


def add_gauge_points(axes):
    """Add gauges and annotation to an axes object."""

    for key, val in field_pts.items():
        axes.scatter(*val, 30, "k", ".", label="P{}".format(key))

    for key, val in model_pts.items():
        axes.scatter(*val, 15, "k", "x", label="S{}".format(key))

    # annotation properties
    text_props = {"textcoords": "offset pixels", "fontsize": 8, "rasterized": True, "snap": True, "in_layout": True}

    # manually annotate each point ...
    axes.annotate("P1", field_pts[1], (-2, -2), va="top", ha="right", **text_props)
    axes.annotate("P2", field_pts[2], (2, -2), va="top", ha="left", **text_props)
    axes.annotate("P3", field_pts[3], (2, -2), va="top", ha="left", **text_props)
    axes.annotate("P4", field_pts[4], (2, 2), va="bottom", ha="left", **text_props)
    axes.annotate("P5", field_pts[5], (-2, -2), va="top", ha="right", **text_props)
    axes.annotate("P6", field_pts[6], (2, 0), va="center", ha="left", **text_props)
    axes.annotate("P7", field_pts[7], (2, -2), va="top", ha="left", **text_props)
    axes.annotate("P8", field_pts[8], (2, 2), va="bottom", ha="left", **text_props)
    axes.annotate("P9", field_pts[9], (2, -2), va="top", ha="left", **text_props)
    axes.annotate("P10", field_pts[10], (0, 2), va="bottom", ha="center", **text_props)
    axes.annotate("P11", field_pts[11], (0, 2), va="bottom", ha="center", **text_props)
    axes.annotate("P12", field_pts[12], (0, -4), va="top", ha="center", **text_props)
    axes.annotate("P13", field_pts[13], (0, -4), va="top", ha="center", **text_props)
    axes.annotate("P14", field_pts[14], (0, 2), va="bottom", ha="center", **text_props)
    axes.annotate("P15", field_pts[15], (0, -4), va="top", ha="center", **text_props)
    axes.annotate("P16", field_pts[16], (2, 2), va="bottom", ha="left", **text_props)
    axes.annotate("P17", field_pts[17], (0, -4), va="top", ha="center", **text_props)

    axes.annotate("S6", model_pts[6], (-2, 2), va="bottom", ha="right", **text_props)
    axes.annotate("S7", model_pts[7], (-2, 2), va="bottom", ha="right", **text_props)
    axes.annotate("S8", model_pts[8], (2, 2), va="bottom", ha="left", **text_props)
    axes.annotate("S9", model_pts[9], (-2, -2), va="top", ha="right", **text_props)
    axes.annotate("S10", model_pts[10], (-2, -2), va="top", ha="right", **text_props)
    axes.annotate("S11", model_pts[11], (4, 0), va="center", ha="left", **text_props)
    axes.annotate("S12", model_pts[12], (4, 0), va="center", ha="left", **text_props)
    axes.annotate("S13", model_pts[13], (4, 0), va="center", ha="left", **text_props)
    axes.annotate("S14", model_pts[14], (4, 0), va="center", ha="left", **text_props)

    return axes


def plot_topo():
    """Plot topo and survey points."""

    dem_file = case_dir["landspill"].joinpath("malpasset-topo.asc")
    rundata = import_setrun(case_dir["landspill"]).setrun()

    # plot
    fig, axes = pyplot.subplots(2, 1, gridspec_kw={"height_ratios": [20, 1]})
    fig.suptitle("Malpasset dam break: topography and gauge points")

    # topo
    axes[0], _, cmap, cmscale = plot_topo_on_ax(axes[0], [dem_file], True, alpha=1, nodata=101)
    axes[0].set_xlim(rundata.clawdata.lower[0], rundata.clawdata.upper[0])
    axes[0].set_ylim(rundata.clawdata.lower[1], rundata.clawdata.upper[1])
    axes[0].set_xlabel("x (meter)")
    axes[0].set_ylabel("y (meter)")

    # gauge points
    add_gauge_points(axes[0])

    # colorbar
    fig.colorbar(cm.ScalarMappable(cmscale, cmap), cax=axes[1], orientation="horizontal")
    axes[1].set_xlabel("Elevation (meter)")

    # save (file format determined by plot style)
    fig.savefig(fig_dir.joinpath("malpasset-topo-gauges"))


def plot_soln(solver="landspill", frame=90):
    """Plot solution at one specific time frame from a chosen solver (geoclaw or landspill)."""

    dem_file = case_dir[solver].joinpath("malpasset-topo.asc")

    # read soln
    soln_dir = case_dir[solver].joinpath("_output")
    soln = pyclaw.Solution()
    soln.read(frame, str(soln_dir), file_format="binary", read_aux=False)

    # determine max level and dry_tol
    rundata = import_setrun(case_dir[solver]).setrun()
    level = rundata.amrdata.amr_levels_max

    # determine cmax
    cmax = get_soln_max(soln_dir, frame, frame+1, level)

    # plot
    fig, axes = pyplot.subplots(2, 1, gridspec_kw={"height_ratios": [20, 1]})
    fig.suptitle("Malpasset dam break: water depth at T=1800 sec")

    # topo
    axes[0], _, _, _ = plot_topo_on_ax(axes[0], [dem_file], True, alpha=0.7, nodata=101)

    # soln
    axes[0], _, cmap_s, cmscale_s = plot_soln_frame_on_ax(axes[0], soln, level, [0., cmax], dry_tol=1e-3)

    # other props
    axes[0].set_xlim(rundata.clawdata.lower[0], rundata.clawdata.upper[0])
    axes[0].set_ylim(rundata.clawdata.lower[1], rundata.clawdata.upper[1])
    axes[0].set_xlabel("x (meter)")
    axes[0].set_ylabel("y (meter)")

    # solution depth colorbar
    fig.colorbar(cm.ScalarMappable(cmscale_s, cmap_s), cax=axes[1], orientation="horizontal")
    axes[1].set_xlabel("Water depth (meter)")

    # save (file format determined by plot style)
    fig.savefig(fig_dir.joinpath("malpasset-soln-{}-frame{:05d}".format(solver, frame)))


def plot_gauges():
    """Plot data of gauges."""
    # pylint: disable=invalid-name

    field_gauges = {
        sol: [pyclaw.GaugeSolution(200+i, str(case_dir[sol].joinpath("_output"))) for i in range(1, 18)]
        for sol in ["geoclaw", "landspill"]
    }

    model_gauges = {
        sol: [pyclaw.GaugeSolution(300+i, str(case_dir[sol].joinpath("_output"))) for i in range(6, 15)]
        for sol in ["geoclaw", "landspill"]
    }

    # simulation max eta (depth + topo)
    field_gauge_sim_mx = {sol: [max(pt.q[3]) for pt in field_gauges[sol]] for sol in ["geoclaw", "landspill"]}
    model_gauge_sim_mx = {sol: [max(pt.q[3]) for pt in model_gauges[sol]] for sol in ["geoclaw", "landspill"]}

    # simulation arrival time (at model gauges)
    model_gauge_arv_sim = {
        sol: [pt.t[numpy.where(pt.q[0] > 0)[0][0]] for pt in model_gauges[sol]]
        for sol in ["geoclaw", "landspill"]
    }

    # field survey observed eta
    field_gauge_obs_mx = [
        79.15, 87.2, 54.9, 64.7, 51.1, 43.75, 44.35, 38.6,
        31.9, 40.75, 24.15, 24.9, 17.25, 20.7, 18.6, 17.25,
        14
    ]

    # field survey max eta from George, 2011
    field_gauge_george_mx = [
        84.56, 87.029, 55.453, 58.175, 48.559, 48.351, 42.064, 36.863,
        34.121, 40.172, 25.962, 27.164, 22.216, 21.827, 19.484, 19.89,
        16.679
    ]

    # lab experiment observed eta
    model_gauge_obs_mx = [84.2, 49.1, 54, 40.2, 34.9, 27.4, 21.5, 16.1, 12.9]

    # lab experiment max eta from George, 2011
    model_gauge_george_mx = [85.653, 56.364, 53.304, 48.762, 38.684, 26.616, 20.445, 18.218, 13.169]

    # lab experiment arrival times
    model_gauge_arv_exp = [10.2, 102, 182, 263, 404, 600, 845, 972, 1139]

    # plot max eta of police servey points
    fig, axes = pyplot.subplots(1, 1)
    fig.suptitle("Malpasset dam break:\nmaximum water levels at field survey points")
    axes.plot(
        range(1, 18), field_gauge_obs_mx, ls="-", lw=2, marker=".", ms=15,
        label="Field survey data (Biscarini et al., 2016)"
    )
    axes.plot(
        range(1, 18), field_gauge_george_mx, ls="none", marker="s", ms=5,
        label="GeoClaw simulation (George, 2011)"
    )
    axes.plot(
        range(1, 18), field_gauge_sim_mx["geoclaw"], ls="none", marker="^", ms=9, mew=2, mfc="none",
        label="GeoClaw simulation (v5.7.1)"
    )
    axes.plot(
        range(1, 18), field_gauge_sim_mx["landspill"], ls="none", marker="x", ms=6, mew=2,
        label="GeoClaw-landspill simulation"
    )
    axes.set_xlim(0, 18)
    axes.set_ylim(0, 100)
    axes.set_xticks(list(range(1, 18, 2)), minor=False)
    axes.set_xticks(list(range(2, 18, 2)), minor=True)
    axes.set_xticklabels(["P{}".format(i) for i in range(1, 18, 2)])
    axes.set_xlabel("Field survey point ID")
    axes.set_ylabel("Water surface level (meter)")
    axes.legend(loc=0, fontsize=12)
    fig.savefig(fig_dir.joinpath("malpasset-gauge-field-survey"))

    # plot max eta of model gauge
    fig, axes = pyplot.subplots(1, 1)
    fig.suptitle("Malpasset dam break:\nmaximum water levels at scaled-model gauges")
    axes.plot(
        range(6, 15), model_gauge_obs_mx, ls="-", lw=2, marker=".", ms=15,
        label="Lab experiments (Biscarini et al., 2016)"
    )
    axes.plot(
        range(6, 15), model_gauge_george_mx, ls="none", marker="s", ms=5,
        label="GeoClaw simulation (George, 2011)"
    )
    axes.plot(
        range(6, 15), model_gauge_sim_mx["geoclaw"], ls="none", marker="^", ms=9, mew=2, mfc="none",
        label="GeoClaw simulation (v5.7.1)"
    )
    axes.plot(
        range(6, 15), model_gauge_sim_mx["landspill"], ls="none", marker="x", ms=6, mew=2,
        label="GeoClaw-landspill simulation"
    )
    axes.set_xlim(5, 15)
    axes.set_ylim(0, 100)
    axes.set_xticks(list(range(6, 15)))
    axes.set_xticklabels(["S{}".format(i) for i in range(6, 15)])
    axes.set_xlabel("Model gauge ID")
    axes.set_ylabel("Water surface level (meter)")
    axes.legend(loc=0, fontsize=12)
    fig.savefig(fig_dir.joinpath("malpasset-gauge-model"))

    # plot arrival times of model gauge
    fig, axes = pyplot.subplots(1, 1)
    fig.suptitle("Malpasset dam break:\narrival times at scaled-model gaugess")
    axes.plot(
        range(6, 15), model_gauge_arv_exp, ls="-", lw=2, marker=".", ms=15,
        label="Lab experiments (Biscarini et al., 2016)"
    )
    axes.plot(
        range(6, 15), model_gauge_arv_sim["geoclaw"], ls="none", marker="^", ms=8, mew=2, mfc="none",
        label="GeoClaw simulation (v5.7.1)"
    )
    axes.plot(
        range(6, 15), model_gauge_arv_sim["landspill"], ls="none", marker="x", ms=6, mew=2,
        label="GeoClaw-landspill simulation"
    )
    axes.set_xlim(5, 15)
    axes.set_ylim(-100, 1400)
    axes.set_xticks(list(range(6, 15)))
    axes.set_xticklabels(["S{}".format(i) for i in range(6, 15)])
    axes.set_xlabel("Model gauge ID")
    axes.set_ylabel("Arrival times (seconds)")
    axes.legend(loc=0, fontsize=12)
    fig.savefig(fig_dir.joinpath("malpasset-arrival-time"))

    # plot histories of P2 and S11
    fig, axes = pyplot.subplots(1, 1)
    fig.suptitle("Malpasset dam break:\nwater surface level history at gauge P2 and S11")
    axes.plot(
        field_gauges["geoclaw"][1].t, field_gauges["geoclaw"][1].q[3], ls="solid", lw=3,
        label="Gauge P2, GeoClaw (v5.7.1)"
    )
    axes.plot(
        field_gauges["landspill"][1].t, field_gauges["landspill"][1].q[3], ls="dashdot", lw=1.5, alpha=0.8,
        label="Gauge P2, GeoClaw-landspill"
    )
    axes.plot(
        model_gauges["geoclaw"][5].t, model_gauges["geoclaw"][5].q[3], ls="dashed", lw=3,
        label="Gauge S11, GeoClaw (v5.7.1)"
    )
    axes.plot(
        model_gauges["landspill"][5].t, model_gauges["landspill"][5].q[3], ls="dotted", lw=1.5, alpha=0.8,
        label="Gauge S11, GeoClaw-landspill"
    )
    axes.set_xlabel("T (seconds)")
    axes.set_ylabel("Water surface level (meter)")
    axes.set_xlim(0, 1800)
    # axes.set_ylim(16, 28)
    axes.legend(loc=0)
    fig.savefig(fig_dir.joinpath("malpasset-p2-s11-hist"))


if __name__ == "__main__":
    plot_topo()
    plot_gauges()
