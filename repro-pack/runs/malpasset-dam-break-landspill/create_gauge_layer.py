#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2021 Pi-Yueh Chuang <pychuang@pm.me>
#
# Distributed under terms of the BSD 3-Clause license.

"""Create vector files/layers for visualization in GIS software."""
import shapely
import geopandas
from matplotlib import pyplot

# electrric transform gauge A, B, C
elec_trans = {"x": [], "y": []}
elec_trans["x"].append(5500)
elec_trans["y"].append(4400)
elec_trans["x"].append(11900)
elec_trans["y"].append(3250)
elec_trans["x"].append(13000)
elec_trans["y"].append(2700)
elec_trans = geopandas.GeoDataFrame(geometry=geopandas.points_from_xy(elec_trans["x"], elec_trans["y"]))

with open("elec_trans.geojson", "w") as fileobj:
    fileobj.write(elec_trans.to_json())

# police survey points P1 ~ P17
field_points = {"x": [], "y": []}
field_points["x"].append(4913.1)
field_points["y"].append(4244.0)
field_points["x"].append(5159.7)
field_points["y"].append(4369.6)
field_points["x"].append(5790.6)
field_points["y"].append(4177.7)
field_points["x"].append(5886.5)
field_points["y"].append(4503.9)
field_points["x"].append(6763.0)
field_points["y"].append(3429.6)
field_points["x"].append(6929.9)
field_points["y"].append(3591.8)
field_points["x"].append(7326.0)
field_points["y"].append(2948.7)
field_points["x"].append(7451)
field_points["y"].append(3232.1)
field_points["x"].append(8735.9)
field_points["y"].append(3264.6)
field_points["x"].append(8628.6)
field_points["y"].append(3604.6)
field_points["x"].append(9761.1)
field_points["y"].append(3480.3)
field_points["x"].append(9832.9)
field_points["y"].append(2414.7)
field_points["x"].append(10957.2)
field_points["y"].append(2651.9)
field_points["x"].append(11115.7)
field_points["y"].append(3800.7)
field_points["x"].append(11689)
field_points["y"].append(2592.3)
field_points["x"].append(11626)
field_points["y"].append(3406.8)
field_points["x"].append(12333.7)
field_points["y"].append(2269.7)
field_points = geopandas.GeoDataFrame(geometry=geopandas.points_from_xy(field_points["x"], field_points["y"]))

with open("field_points.geojson", "w") as fileobj:
    fileobj.write(field_points.to_json())

# model gauge points G6 ~ G14
model_points = {"x": [], "y": []}
model_points["x"].append(4947.4)
model_points["y"].append(4289.7)
model_points["x"].append(5717.3)
model_points["y"].append(4407.6)
model_points["x"].append(6775.1)
model_points["y"].append(3869.2)
model_points["x"].append(7128.2)
model_points["y"].append(3162)
model_points["x"].append(8585.3)
model_points["y"].append(3443.1)
model_points["x"].append(9675)
model_points["y"].append(3085.9)
model_points["x"].append(10939.1)
model_points["y"].append(3044.8)
model_points["x"].append(11724.4)
model_points["y"].append(2810.4)
model_points["x"].append(12723.7)
model_points["y"].append(2485.1)
model_points = geopandas.GeoDataFrame(geometry=geopandas.points_from_xy(model_points["x"], model_points["y"]))

with open("model_points.geojson", "w") as fileobj:
    fileobj.write(model_points.to_json())

# dam location
dam = geopandas.GeoDataFrame(geometry=[shapely.geometry.LineString([[4701, 4143], [4655, 4392]])])

with open("dam.geojson", "w") as fileobj:
    fileobj.write(dam.to_json())
