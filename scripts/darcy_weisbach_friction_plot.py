#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the BSD 3-Clause license.

"""Compare different models for Darcy-Weisbach friction coefficients.
"""
import numpy
import scipy.special


def thorleifson_et_al_2011_full_circular(vel, depth, vis, roughness):
    """Thorleifson et al., 2011, using 64/Re."""

    def kernel(_vel, _depth, _vis, _roughness):
        """Kernel."""

        reynolds_num = _vel * _depth / _vis
        rel_roughness = _roughness / _depth

        if reynolds_num <= 700.:
            return 16 / reynolds_num
        elif 700. <= reynolds_num <= 25000.:
            return 0.224 / (reynolds_num**0.25)

        coef = numpy.log10(rel_roughness/14.8+5.74/((4.*reynolds_num)**0.9))
        coef *= coef
        coef *= 4.
        coef = 1. / coef
        return coef

    return numpy.vectorize(kernel)(vel, depth, vis, roughness)


def thorleifson_et_al_2011_wide_open(vel, depth, vis, roughness):
    """Thorleifson et al., 2011, using 96/Re."""

    def kernel(_vel, _depth, _vis, _roughness):
        """Kernel."""

        reynolds_num = _vel * _depth / _vis
        rel_roughness = _roughness / _depth

        if reynolds_num <= 700:
            return 24. / reynolds_num
        elif 700. <= reynolds_num <= 25000.:
            return 0.224 / (reynolds_num**0.25)

        coef = numpy.log10(rel_roughness/14.8+5.74/((4.*reynolds_num)**0.9))
        coef *= coef
        coef *= 4.
        coef = 1. / coef
        return coef

    return numpy.vectorize(kernel)(vel, depth, vis, roughness)


def churchill_1977(vel, depth, vis, roughness):
    """Churchill, 1977."""

    def kernel(_vel, _depth, _vis, _roughness):
        """Kernel."""

        reynolds_num = 4. * _vel * _depth / _vis
        rel_roughness = _roughness / _depth

        A = (2.457 * numpy.log(1./((7./reynolds_num)**0.9+0.27*rel_roughness)))**16.
        B = (37530 / reynolds_num)**16.
        coef = ((8. / reynolds_num)**12. + 1. / ((A + B)**1.5))**(1./12.)
        return 8 * coef  # factor of 8 because the Churchill's coefficient is D-W coefficient / 8

    return numpy.vectorize(kernel)(vel, depth, vis, roughness)


def yen_2002(vel, depth, vis, roughness):
    """Yen, 2002."""

    def kernel(_vel, _depth, _vis, _roughness):
        """Kernel."""

        reynolds_num = _vel * _depth / _vis
        rel_roughness = _roughness / _depth

        if reynolds_num <= 700.:
            return 24. / reynolds_num
        elif 700. <= reynolds_num <= 25000.:
            return 0.224 / (reynolds_num**0.25)

        coef = numpy.log10(rel_roughness/12.+1.95/(reynolds_num**0.9))
        coef *= coef
        coef *= 4.
        coef = 1. / coef
        return coef

    return numpy.vectorize(kernel)(vel, depth, vis, roughness)


def cheng_2008(vel, depth, vis, roughness):
    """Cheng, 2008."""

    reynolds_num = vel * depth / vis

    alpha = numpy.reciprocal(numpy.power(reynolds_num/850., 9)+1.)
    beta = numpy.reciprocal(numpy.power(reynolds_num*roughness/(160.*depth), 2) + 1.)

    coef = numpy.power(reynolds_num/24., alpha)
    coef *= numpy.power(1.8*numpy.log10(reynolds_num/2.1), 2.*(1.-alpha)*beta)

    with numpy.errstate(divide="ignore"):
        coef *= numpy.power(2.*numpy.log10(11.8*depth/roughness), 2.*(1.-alpha)*(1.-beta))

    coef = numpy.reciprocal(coef)
    return coef


def bellos_et_al_2018(vel, depth, vis, roughness):
    """Bellow et al., 2018"""

    Cs = 8.94
    Cr = 33.2
    kappa = 0.4187

    reynolds_num = vel * depth / vis

    alpha = numpy.reciprocal(numpy.power(reynolds_num/678., 8.4)+1.)
    beta = numpy.reciprocal(numpy.power(reynolds_num*roughness/(150.*depth), 1.8) + 1.)

    coef = numpy.power(24./reynolds_num, alpha)

    coef *= numpy.power(
        numpy.sqrt(8.)*numpy.exp(approx_w(kappa*Cs*reynolds_num/numpy.e)+1.)/(reynolds_num*Cs),
        2.*(1.-alpha)*beta)

    with numpy.errstate(divide="ignore"):
        coef *= numpy.power(
            numpy.sqrt(8.)*kappa*numpy.reciprocal(numpy.log(Cr*depth/(numpy.e*roughness))),
            2.*(1.-alpha)*(1.-beta))

    return coef


def approx_w(x):
    """Approximation to the lambert w function."""
    lnx = numpy.log(x)
    lnlnx = numpy.log(lnx)
    return lnx - lnlnx + lnlnx/lnx + (lnlnx * lnlnx - 2. * lnlnx) / (2. * lnx * lnx)



if __name__ == "__main__":
    import pathlib
    from itertools import cycle
    from matplotlib import pyplot, lines

    # paths
    root_dir = pathlib.Path(__file__).expanduser().resolve().parents[1]
    figs_dir = root_dir.joinpath("figs")

    # unified style configuration
    pyplot.style.use(figs_dir.joinpath("paper.mplstyle"))

    u = numpy.ones(1000)
    nu = numpy.ones(1000)
    h = numpy.logspace(2, 6, 1000)
    re_num = u * h / nu


    prop_cycle = pyplot.rcParams['axes.prop_cycle']
    colors = cycle(prop_cycle.by_key()['color'])

    pyplot.figure()

    pyplot.loglog(re_num, cheng_2008(u, h, nu, 0.), lw=2, ls="-", color="#1f77b4")
    pyplot.loglog(re_num, bellos_et_al_2018(u, h, nu, 0.), lw=2, ls="-.", color="#ff7f0e")
    pyplot.annotate(
        r"$k_s/h=0$", (1e6, bellos_et_al_2018(u[-25], h[-25], nu[-25], 0.)),
        backgroundcolor="w", fontsize=8, in_layout=True, ha="left")

    for i, ratio in enumerate([1., 10., 50., 100., 200., 500.]):
        c = next(colors)
        ks = h / ratio
        pyplot.loglog(re_num, cheng_2008(u, h, nu, ks), lw=2, ls="-", color="#1f77b4")
        pyplot.loglog(re_num, bellos_et_al_2018(u, h, nu, ks), lw=2, ls="-.", color="#ff7f0e")
        pyplot.annotate(
            r"$k_s/h={}$".format(1./ratio),
            (1e6, bellos_et_al_2018(u[-25], h[-25], nu[-25], ks[-25])),
            backgroundcolor="w", fontsize=8, in_layout=True, ha="left")

    label_lines = [
        lines.Line2D([0], [0], color="#1f77b4", lw=2, ls="-"),
        lines.Line2D([0], [0], color="#ff7f0e", lw=2, ls="-."),
    ]

    pyplot.legend(label_lines, ["Cheng, 2008", "Bellos et al., 2018"], loc=0)

    pyplot.xscale("log")
    pyplot.xlabel(r"Reynolds number, $Re_h=\frac{\left|\vec{u}\right|h}{\nu}$")

    pyplot.yscale("log")
    pyplot.ylim(1e-2, 1e0)
    pyplot.ylabel(r"Darcy-Weisbach friction coefficient, $f$")

    pyplot.suptitle("Comparison of Darcy-Weisbach friction models")
    pyplot.savefig(figs_dir.joinpath("darcy-weisbach-models"))
