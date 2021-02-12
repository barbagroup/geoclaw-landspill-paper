"""Malpasset dam break simulation using geoclaw-landspill."""
# pylint: disable=no-member, too-many-statements
import gclandspill.data


def setrun():
    """Define the parameters used for running Clawpack.

    Returns
    -------
    rundata : gclandspill.data.ClawRunData
    """

    rundata = gclandspill.data.ClawRunData()

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
