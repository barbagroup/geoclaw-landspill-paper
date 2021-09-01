#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Pi-Yueh Chuang <pychuang@gwu.edu>
#
# Distributed under terms of the BSD 3-Clause license.

"""Generate ASCII format topography from Telemac's Malpasset mesh."""
# pylint: disable=invalid-name
import pathlib
import numpy
import scipy.interpolate
import fiona
import geopandas
import rasterio
import rasterio.mask
import rasterio.io
import rasterio.transform
import rasterio.features


# enable Selafin driver
fiona.supported_drivers["Selafin"] = "rw"

# case folder and final output raster
case_dir = pathlib.Path(__file__).parent.expanduser().resolve()
topo_output = case_dir.joinpath("malpasset-topo.asc")
eta_output = case_dir.joinpath("malpasset-eta.xyz")

# sources
s_source_file = case_dir.joinpath("geo_malpasset-small.slf")
s_polygon_layer = "geo_malpasset-small_e0"
s_point_layer = "geo_malpasset-small_p0"

# output raster dimension
extent = [530., -2350., 17774., 6842.]
res = [12., 12.]
size = [766, 1437]

# output raster profile
profile = {
    "width": size[1],
    "height": size[0],
    "count": 1,
    "transform": rasterio.transform.from_bounds(*extent, size[1], size[0]),
    "nodata": -9999,
    "dtype": "float64"
}

# french to english translation for the column names
translation = {
    "VITESSE U       M/S             ": "velocity-u",
    "VITESSE V       M/S             ": "velocity-v",
    "HAUTEUR D EAU   M               ": "depth",
    "SURFACE LIBRE   M               ": "eta",
    "FOND            M               ": "elevation",
    "FOND                            ": "elevation"
}

# read in the polygon mesh and points
s_polygons = geopandas.read_file(s_source_file, mode="r", driver="Selafin", layer=s_polygon_layer)
s_polygons = s_polygons.rename(columns=translation)
s_points = geopandas.read_file(s_source_file, mode="r", driver="Selafin", layer=s_point_layer)
s_points = s_points.rename(columns=translation)

# create a mask (a big polygon) for valid topography
s_polygons["temp"] = 0
topo_mask = s_polygons.dissolve(by="temp").geometry.to_list()

# create masks for reservoir and gulf
reservoir_mask = s_polygons.loc[s_polygons.depth != 0].loc[s_polygons.eta > 50]
reservoir_mask["temp"] = 0
reservoir_mask = reservoir_mask.dissolve(by="temp").geometry
gulf_mask = s_polygons.loc[s_polygons.depth != 0].loc[s_polygons.eta < 50]
gulf_mask["temp"] = 0
gulf_mask = gulf_mask.dissolve(by="temp").geometry

# prepare for rasterize
data = []
for row in s_polygons.iterrows():
    data.append((row[1].geometry, row[1].elevation))

raster_z = rasterio.features.rasterize(
    data, size, fill=101, transform=profile["transform"], all_touched=True, dtype="float64")

# # extract x and y coordinates from topography points
# topo_xy = numpy.concatenate([s_points.geometry.x.to_numpy()[:, None], s_points.geometry.y.to_numpy()[:, None]], 1)
# topo_z = s_points.elevation.to_numpy()

# # initialize coordinates of the pixels in the output raster
# raster_x, raster_y = numpy.meshgrid(
#     numpy.linspace(extent[0]+res[0]/2., extent[2]-res[0]/2., size[1]),
#     numpy.linspace(extent[1]+res[1]/2., extent[3]-res[1]/2., size[0])
# )

# # revert row order (rasters usually put origins at upper-left corner)
# raster_x = raster_x[::-1, :]
# raster_y = raster_y[::-1, :]

# # interpolate elevation to the raster grid points
# raster_z = scipy.interpolate.griddata(
#     topo_xy, topo_z, numpy.concatenate([raster_x.reshape((-1, 1)), raster_y.reshape((-1, 1))], 1),
#     "linear", -9999
# ).reshape((1,)+raster_x.shape)  # add an extra dimension for band index

# # apply mask (write to an temporary & in-memory raster dataset first)
# with rasterio.io.MemoryFile() as memfile:
#     with memfile.open(driver="GTiff", **profile) as dataset:
#         dataset.write(raster_z)
#         raster_z, _ = rasterio.mask.mask(dataset, topo_mask, False, False, 100, True)  # GeoClaw doesn't like nodata

# output topo
with rasterio.open(topo_output, "w", driver="AAIGrid", **profile) as dataset:
    dataset.write(raster_z, 1)

# eta
eta_z = raster_z - 1e-3  # make init eta below topo so it's dry every where in GeoClaw

if len(eta_z.shape) == 2:
    eta_z = eta_z[None, :, :]

# apply reservoir mask
with rasterio.io.MemoryFile() as memfile:
    with memfile.open(driver="GTiff", **profile) as dataset:
        dataset.write(eta_z)
        eta_z, _ = rasterio.mask.mask(dataset, reservoir_mask, False, True, 100, True)  # the eta at reservoir is 100

# apply gulf mask
with rasterio.io.MemoryFile() as memfile:
    with memfile.open(driver="GTiff", **profile) as dataset:
        dataset.write(eta_z)
        eta_z, _ = rasterio.mask.mask(dataset, gulf_mask, False, True, -0.5, True)  # the initial eta at gulf is -0.5

# output eta
with rasterio.open(eta_output, "w", driver="XYZ", **profile) as dataset:
    dataset.write(eta_z)
