#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2020 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the BSD 3-Clause license.

"""Helper functions.
"""
import os
import requests
import numpy
import scipy.interpolate

def get_max_AMR_level(solution):
    """Get the max AMR level in a solution object.

    Args:
    -----
        soultions: a pyclaw.Solution object.

    Returns:
    --------
        max_level: the max AMR level.
    """

    max_level = 1

    for state in solution.states:
        p = state.patch
        max_level = p.level if p.level > max_level else max_level

    return max_level

def get_level_ncells_volumes(solution):
    """Get level-wise numbers of cells and fluid volumes.

    Args:
    -----
        soultions: a pyclaw.Solution object.

    Returns:
    --------
        ncells: a list of the number of cells at each AMR level.
        volumrs: a list of the total fuild volumes at each AMR level.
    """

    max_level = get_max_AMR_level(solution)
    ncells = [0 for _ in range(max_level)]
    volumes = [0.0 for _ in range(max_level)]

    for state in solution.states:
        p = state.patch
        level = p.level
        ncells[level-1] += (p.num_cells_global[0] * p.num_cells_global[1])
        volumes[level-1] += (numpy.sum(state.q[0, :, :]) * p.delta[0] * p.delta[1])

    return ncells, volumes

def get_min_max_values(solution, field=0):
    """Get the minimum and the maximum values of a field in a solution.

    Args:
    -----
        soultions: a pyclaw.Solution object.
        field: the index of the target field in the solution.

    Returns:
    --------
        min_val: the minimum value.
        max_val: the maximum value.
    """

    min_val, max_val = 1e38, 0.

    for state in solution.states:
        min_temp = state.q[field, :, :].min()
        max_temp = state.q[field, :, :].max()
        min_val = min_temp if min_temp < min_val else min_val
        max_val = max_temp if max_temp > max_val else max_val

    return min_val, max_val

def get_state_interpolator(state, field=0, **kwargs):
    """Get a Scipy interpolation object for a field on a AMR grid.

    Args:
    -----
        soultions: a pyclaw.Solution object.
        field: the index of the target field in the solution.
        kwargs: keyword arguments to scipy.interpolate.RectBivariateSpline.

    Returns:
    --------
        interp: a scipy.interpolate.RectBivariateSpline.
    """

    # the underlying patch in this state object
    p = state.patch

    # x, y arrays and also dx, dy for checking
    x, dx = numpy.linspace(
        p.lower_global[0]+p.delta[0]/2., p.upper_global[0]-p.delta[0]/2.,
        p.num_cells_global[0], retstep=True
    )
    y, dy = numpy.linspace(
        p.lower_global[1]+p.delta[1]/2., p.upper_global[1]-p.delta[1]/2.,
        p.num_cells_global[1], retstep=True
    )
    # sanity check
    assert numpy.abs(dx-p.delta[0]) < 1e-6, "{} {}".format(dx, p.delta[0])
    assert numpy.abs(dy-p.delta[1]) < 1e-6, "{} {}".format(dy, p.delta[1])

    interp = scipy.interpolate.RectBivariateSpline(
        x=x, y=y, z=state.q[field, :, :],
        bbox=[
            p.lower_global[0], p.upper_global[0],
            p.lower_global[1], p.upper_global[1]
        ],
    )

    return interp

def interpolate(solution, field, x, y, level=1):
    """Do the interpolation.

    Args:
    -----
        solution: a pyclaw.Solution instance.
        field: int; the target field in the solution.
        x: 1D numpy.ndarray; x coordinates to be interpolated on.
        y: 1D numpy.ndarray; y coordinates to be interpolated on.
        level: int; the target AMR level.

    Returns:
    --------
        values: a 2D numpy.ndarray of shape (y.size, x.size).
    """

    # allocate space for interpolated results
    values = numpy.zeros((y.size, x.size), dtype=numpy.float64)

    # loop through all AMR grids
    for state in solution.states:
        p = state.patch

        # only do subsequent jobs if this is at the target level
        if p.level != level:
            continue

        # get the indices of the target coordinates that are inside this patch
        xid = numpy.where(numpy.logical_and(x>=p.lower_global[0], x<=p.upper_global[0]))[0]
        yid = numpy.where(numpy.logical_and(y>=p.lower_global[1], y<=p.upper_global[1]))[0]

        # if any target coordinate located in thie patch, do interpolation
        if xid.size and yid.size:
            # get interpolation object and interpolate
            interp = get_state_interpolator(state, field)
            values[yid[:, None], xid[None, :]] = interp(x[xid], y[yid]).T

    return values

def download_sat_image(extent, filepath, force=False):
    """Download a setellite image of the given extent.

    Args:
    -----
        extent: a list of [xmin, ymin, xmax, ymax]
        filepath: where to save the image.
        force: force to download.

    Returns:
        The extent of the saved image. The server does not always return the
        image within exactly the extent. Sometimes the extent of the image is
        larger, so we need to know.
    """
    api_url = "http://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/export"
    extent_file = filepath.with_suffix(filepath.suffix+".extent")

    # always with extra 5 pixels outside each boundary
    extent[0] = int(extent[0]) - 5
    extent[1] = int(extent[1]) - 5
    extent[2] = int(extent[2]) + 5
    extent[3] = int(extent[3]) + 5
    width = extent[2]-extent[0]
    height = extent[3]-extent[1]

    # if image and extent info already exists, we may stop downloading and leave
    if os.path.isfile(extent_file) and os.path.isfile(filepath) and not force:
        with open(extent_file, "r") as f:
            img_extent = f.readline()

        img_extent = img_extent.strip().split()
        img_extent = [float(i) for i in img_extent]
        return img_extent

    # REST API parameters
    params = {
        "bbox": "{},{},{},{}".format(*extent),
        "bbSR": "3857",
        "size": "{},{}".format(width, height),
        "imageSR": "3857",
        "format": "png",
        "f": "json"
    }

    # create a HTTP session that can retry 5 times if 500, 502, 503, 504 happens
    session = requests.Session()
    session.mount("https://", requests.adapters.HTTPAdapter(
        max_retries=requests.packages.urllib3.util.retry.Retry(
            total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504]
        )
    ))

    # use GET to get response
    respns = session.get(api_url, params=params)
    respns.raise_for_status() # raise an error if not success
    respns = respns.json() # convert to a dictionary
    assert "href" in respns # make sure the image's url is in the response

    # download the file, retry unitl success or timeout
    respns2 = session.get(respns["href"], stream=True, allow_redirects=True)
    respns2.raise_for_status()

    with open(filepath, "wb") as f:
        f.write(respns2.content)

    # close the session
    session.close()

    # write image extent to a text file
    with open(extent_file, "w") as f:
        f.write("{} {} {} {}".format(
            respns["extent"]["xmin"], respns["extent"]["ymin"],
            respns["extent"]["xmax"], respns["extent"]["ymax"]
        ))

    return [respns["extent"]["xmin"], respns["extent"]["ymin"],
            respns["extent"]["xmax"], respns["extent"]["ymax"]]

def get_AMR_borders(solution, lv):
    """Get the xlims and ylims of each AMR patch.

    Args:
    -----
        soultions: a pyclaw.Solution object.
        lv: the target lv in AMR.

    Returns:
    --------
        limits: a list of elements in the format: (xmin, xmax, ymin, ymax)
    """

    limits = []
    for state in solution.states:

        p = state.patch

        if p.level != lv:
            continue

        limits.append(
            [p.lower_global[0], p.upper_global[0],
             p.lower_global[1], p.upper_global[1]]
        )

    return limits
