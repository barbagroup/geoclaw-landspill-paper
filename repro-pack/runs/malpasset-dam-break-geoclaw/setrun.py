"""Set up run time parameters for Clawpack.

The values set in the function setrun are then written out to data files
that will be read in by the Fortran code.
"""
import os
from clawpack.clawutil import data


def setrun(claw_pkg='geoclaw'):
    """
    Define the parameters used for running Clawpack.

    INPUT:
        claw_pkg expected to be "geoclaw" for this setrun.

    OUTPUT:
        rundata - object of class ClawRunData

    """

    assert claw_pkg.lower() == 'geoclaw',  "Expected claw_pkg = 'geoclaw'"

    num_dim = 2
    rundata = data.ClawRunData(claw_pkg, num_dim)

    # core classical clawpack configuration
    rundata.clawdata.num_eqn = 3
    rundata.clawdata.num_waves = 3
    rundata.clawdata.num_aux = 1
    rundata.clawdata.output_format = 3  # binary
    rundata.clawdata.output_aux_components = "all"
    rundata.clawdata.output_aux_onlyonce = False
    rundata.clawdata.dt_initial = 1e-5
    rundata.clawdata.dt_max = 5.0
    rundata.clawdata.cfl_max = 0.95
    rundata.clawdata.steps_max = 100000
    rundata.clawdata.verbosity = 5
    rundata.clawdata.verbosity_regrid = 5
    rundata.clawdata.source_split = 1  # godunov
    rundata.clawdata.limiter = [4, 4, 4]  # use "mc" limiter for all equations
    rundata.clawdata.use_fwaves = True
    rundata.clawdata.bc_lower = [1, 1]
    rundata.clawdata.bc_upper = [1, 1]

    # AMRClaw configuration
    rundata.amrdata.amr_levels_max = 2
    rundata.amrdata.refinement_ratios_x = [4]
    rundata.amrdata.refinement_ratios_y = [4]
    rundata.amrdata.refinement_ratios_t = [4]
    rundata.amrdata.aux_type = ["center", "center"]  # aux variables are defined at cell centers
    rundata.amrdata.regrid_interval = 1
    rundata.amrdata.verbosity_regrid = 5

    # GeoClaw basic configuration
    rundata.geo_data.gravity = 9.81
    rundata.geo_data.coriolis_forcing = False
    rundata.geo_data.sea_level = -1000.
    rundata.geo_data.dry_tolerance = 1e-4
    rundata.geo_data.friction_forcing = False  # turned off in favor of Darcy-Weisbach friction

    # GeoClaw refinement mechanism
    rundata.refinement_data.wave_tolerance = 1.0e-5
    rundata.refinement_data.speed_tolerance = [1e-5] * 6
    rundata.refinement_data.variable_dt_refinement_ratios = True

    # lower and upper edges of computational domain
    rundata.clawdata.lower[0] = 542.0
    rundata.clawdata.upper[0] = 17762.0
    rundata.clawdata.lower[1] = -2338.0
    rundata.clawdata.upper[1] = 6830.0

    # number of grid cells: coarsest grid
    rundata.clawdata.num_cells[0] = 1435
    rundata.clawdata.num_cells[1] = 764

    rundata.amrdata.amr_levels_max = 1
    rundata.amrdata.refinement_ratios_x = [2]
    rundata.amrdata.refinement_ratios_y = [2]
    rundata.amrdata.refinement_ratios_t = [2]

    # temporal data output
    rundata.clawdata.output_style = 1
    rundata.clawdata.num_output_times = 180
    rundata.clawdata.tfinal = 3600
    rundata.clawdata.output_t0 = True  # output at initial (or restart) time?

    # disable initializing water surface level with sea-level
    rundata.geo_data.sea_level = -1e8

    # manning's friction
    rundata.geo_data.friction_forcing = True
    rundata.geo_data.manning_coefficient = 0.033

    # initial water serface level (i.e., depth + topo elevation)
    rundata.qinit_data.qinit_type = 4
    rundata.qinit_data.qinitfiles = [["malpasset-eta.xyz"]]

    # topography
    rundata.topo_data.topofiles.append([3, "malpasset-topo.asc"])

    # electrric transform gauge A, B, C
    rundata.gaugedata.gauges.append([101, 5500, 4400, 0., 1e9])
    rundata.gaugedata.gauges.append([102, 11900, 3250, 0., 1e9])
    rundata.gaugedata.gauges.append([103, 13000, 2700, 0., 1e9])

    # police survey points P1 ~ P17
    rundata.gaugedata.gauges.append([201, 4913.1, 4244.0, 0., 1e9])
    rundata.gaugedata.gauges.append([202, 5159.7, 4369.6, 0., 1e9])
    rundata.gaugedata.gauges.append([203, 5790.6, 4177.7, 0., 1e9])
    rundata.gaugedata.gauges.append([204, 5886.5, 4503.9, 0., 1e9])
    rundata.gaugedata.gauges.append([205, 6763.0, 3429.6, 0., 1e9])
    rundata.gaugedata.gauges.append([206, 6929.9, 3591.8, 0., 1e9])
    rundata.gaugedata.gauges.append([207, 7326.0, 2948.7, 0., 1e9])
    rundata.gaugedata.gauges.append([208, 7451, 3232.1, 0., 1e9])
    rundata.gaugedata.gauges.append([209, 8735.9, 3264.6, 0., 1e9])
    rundata.gaugedata.gauges.append([210, 8628.6, 3604.6, 0., 1e9])
    rundata.gaugedata.gauges.append([211, 9761.1, 3480.3, 0., 1e9])
    rundata.gaugedata.gauges.append([212, 9832.9, 2414.7, 0., 1e9])
    rundata.gaugedata.gauges.append([213, 10957.2, 2651.9, 0., 1e9])
    rundata.gaugedata.gauges.append([214, 11115.7, 3800.7, 0., 1e9])
    rundata.gaugedata.gauges.append([215, 11689, 2592.3, 0., 1e9])
    rundata.gaugedata.gauges.append([216, 11626, 3406.8, 0., 1e9])
    rundata.gaugedata.gauges.append([217, 12333.7, 2269.7, 0., 1e9])

    # model gauge points G6 ~ G14
    rundata.gaugedata.gauges.append([306, 4947.4, 4289.7, 0., 1e9])
    rundata.gaugedata.gauges.append([307, 5717.3, 4407.6, 0., 1e9])
    rundata.gaugedata.gauges.append([308, 6775.1, 3869.2, 0., 1e9])
    rundata.gaugedata.gauges.append([309, 7128.2, 3162, 0., 1e9])
    rundata.gaugedata.gauges.append([310, 8585.3, 3443.1, 0., 1e9])
    rundata.gaugedata.gauges.append([311, 9675, 3085.9, 0., 1e9])
    rundata.gaugedata.gauges.append([312, 10939.1, 3044.8, 0., 1e9])
    rundata.gaugedata.gauges.append([313, 11724.4, 2810.4, 0., 1e9])
    rundata.gaugedata.gauges.append([314, 12723.7, 2485.1, 0., 1e9])

    return rundata
    # end of function setgeo
    # ----------------------


if __name__ == '__main__':
    # Set up run-time parameters and write all data files.
    import sys

    rundata = setrun(*sys.argv[1:])
    rundata.write()
