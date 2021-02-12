Malpasset dam break
===================

***Note: the vector files `geo_malpasset-large.slf` and `geo_malpasset-small.slf`
are obtained from [Open Telemac-Mascaret](http://www.opentelemac.org/) and
covered by the GPL3 license.***

Before running the simulation, use the script `vector_to_raster.py` to create
topography data and initial value data required. The script creates two files:
`malpasset-topo.asc` and `malpasset-eta.xyz`.

The directory `data` contains maximum water levels at field survey and scaled-model
gauges extracted from George, 2011.

------------
## Reference

George, D. L. (2011). Adaptive finite volume methods with well-balanced Riemann
solvers for modeling floods in rugged terrain: Application to the Malpasset
dam-break flood (France, 1959). International Journal for Numerical Methods in
Fluids, 66(8), 1000–1018. https://doi.org/10.1002/fld.2298
