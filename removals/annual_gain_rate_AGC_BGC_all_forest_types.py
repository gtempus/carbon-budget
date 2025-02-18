import datetime
import numpy as np
import os
import rasterio
import logging
import sys
sys.path.append('../')
import constants_and_names as cn
import universal_util as uu

def annual_gain_rate_AGC_BGC_all_forest_types(tile_id, output_pattern_list, sensit_type, no_upload):

    uu.print_log("Mapping removal rate source and AGB and BGB removal rates:", tile_id)

    # Start time
    start = datetime.datetime.now()

    # Names of the input tiles
    # Removal factors
    model_extent = uu.sensit_tile_rename(sensit_type, tile_id, cn.pattern_model_extent)
    mangrove_AGB = '{0}_{1}.tif'.format(tile_id, cn.pattern_annual_gain_AGB_mangrove)
    mangrove_BGB = '{0}_{1}.tif'.format(tile_id, cn.pattern_annual_gain_BGB_mangrove)
    europe_AGC_BGC = uu.sensit_tile_rename(sensit_type, tile_id, cn.pattern_annual_gain_AGC_BGC_natrl_forest_Europe)
    plantations_AGC_BGC = uu.sensit_tile_rename(sensit_type, tile_id, cn.pattern_annual_gain_AGC_BGC_planted_forest_unmasked)
    us_AGC_BGC = uu.sensit_tile_rename(sensit_type, tile_id, cn.pattern_annual_gain_AGC_BGC_natrl_forest_US)
    young_AGC = uu.sensit_tile_rename(sensit_type, tile_id, cn.pattern_annual_gain_AGC_natrl_forest_young)
    age_category = uu.sensit_tile_rename(sensit_type, tile_id, cn.pattern_age_cat_IPCC)
    ipcc_AGB_default = uu.sensit_tile_rename(sensit_type, tile_id, cn.pattern_annual_gain_AGB_IPCC_defaults)

    # Removal factor standard deviations
    mangrove_AGB_stdev = '{0}_{1}.tif'.format(tile_id, cn.pattern_stdev_annual_gain_AGB_mangrove)
    europe_AGC_BGC_stdev = uu.sensit_tile_rename(sensit_type, tile_id, cn.pattern_stdev_annual_gain_AGC_BGC_natrl_forest_Europe)
    plantations_AGC_BGC_stdev = uu.sensit_tile_rename(sensit_type, tile_id, cn.pattern_stdev_annual_gain_AGC_BGC_planted_forest_unmasked)
    us_AGC_BGC_stdev = uu.sensit_tile_rename(sensit_type, tile_id, cn.pattern_stdev_annual_gain_AGC_BGC_natrl_forest_US)
    young_AGC_stdev = uu.sensit_tile_rename(sensit_type, tile_id, cn.pattern_stdev_annual_gain_AGC_natrl_forest_young)
    ipcc_AGB_default_stdev = uu.sensit_tile_rename(sensit_type, tile_id, cn.pattern_stdev_annual_gain_AGB_IPCC_defaults)

    # Names of the output tiles
    removal_forest_type = '{0}_{1}.tif'.format(tile_id, output_pattern_list[0])
    annual_gain_AGC_all_forest_types = '{0}_{1}.tif'.format(tile_id, output_pattern_list[1])
    annual_gain_BGC_all_forest_types = '{0}_{1}.tif'.format(tile_id, output_pattern_list[2])
    annual_gain_AGC_BGC_all_forest_types = '{0}_{1}.tif'.format(tile_id, output_pattern_list[3]) # Not used further in the model. Created just for reference.
    stdev_annual_gain_AGC_all_forest_types = '{0}_{1}.tif'.format(tile_id, output_pattern_list[4])

    # Opens biomass tile
    with rasterio.open(model_extent) as model_extent_src:

        # Grabs metadata about the tif, like its location/projection/cellsize
        kwargs = model_extent_src.meta

        # Grabs the windows of the tile (stripes) so we can iterate over the entire tif without running out of memory
        windows = model_extent_src.block_windows(1)

        # Updates kwargs for the output dataset
        kwargs.update(
            driver='GTiff',
            count=1,
            compress='DEFLATE',
            nodata=0
        )

        # Checks whether there are mangrove or planted forest tiles. If so, they are opened.
        try:
            mangrove_AGB_src = rasterio.open(mangrove_AGB)
            mangrove_BGB_src = rasterio.open(mangrove_BGB)
            mangrove_AGB_stdev_src = rasterio.open(mangrove_AGB_stdev)
            uu.print_log("    Mangrove tiles (AGB and BGB) for {}".format(tile_id))
        except:
            uu.print_log("    No mangrove tile for {}".format(tile_id))

        try:
            europe_AGC_BGC_src = rasterio.open(europe_AGC_BGC)
            europe_AGC_BGC_stdev_src = rasterio.open(europe_AGC_BGC_stdev)
            uu.print_log("    Europe removal factor tile for {}".format(tile_id))
        except:
            uu.print_log("    No Europe removal factor tile for {}".format(tile_id))

        try:
            plantations_AGC_BGC_src = rasterio.open(plantations_AGC_BGC)
            plantations_AGC_BGC_stdev_src = rasterio.open(plantations_AGC_BGC_stdev)
            uu.print_log("    Planted forest tile for {}".format(tile_id))
        except:
            uu.print_log("    No planted forest tile for {}".format(tile_id))

        try:
            us_AGC_BGC_src = rasterio.open(us_AGC_BGC)
            us_AGC_BGC_stdev_src = rasterio.open(us_AGC_BGC_stdev)
            uu.print_log("    US removal factor tile for {}".format(tile_id))
        except:
            uu.print_log("    No US removal factor tile for {}".format(tile_id))

        try:
            young_AGC_src = rasterio.open(young_AGC)
            young_AGC_stdev_src = rasterio.open(young_AGC_stdev)
            uu.print_log("    Young forest removal factor tile for {}".format(tile_id))
        except:
            uu.print_log("    No young forest removal factor tile for {}".format(tile_id))

        try:
            age_category_src = rasterio.open(age_category)
            uu.print_log("    Age category tile for {}".format(tile_id))
        except:
            uu.print_log("    No age category tile for {}".format(tile_id))

        try:
            ipcc_AGB_default_src = rasterio.open(ipcc_AGB_default)
            ipcc_AGB_default_stdev_src = rasterio.open(ipcc_AGB_default_stdev)
            uu.print_log("    IPCC default removal rate tile for {}".format(tile_id))
        except:
            uu.print_log("    No IPCC default removal rate tile for {}".format(tile_id))

        # Opens the output tile, giving it the arguments of the input tiles
        removal_forest_type_dst = rasterio.open(removal_forest_type, 'w', **kwargs)

        # Adds metadata tags to the output raster
        uu.add_rasterio_tags(removal_forest_type_dst, sensit_type)
        removal_forest_type_dst.update_tags(
            key='6: mangroves. 5: European-specific rates. 4: planted forests. 3: US-specific rates. 2: young (<20 year) secondary forests. 1: old (>20 year) secondary forests and primary forests. Priority goes to the highest number.')
        removal_forest_type_dst.update_tags(
            source='Mangroves: IPCC wetlands supplement. Europe: Liz Goldman. Planted forests: Spatial Database of Planted Forests. USA: US FIA, via Rich Birdsey. Young natural forests: Cook-Patton et al. 2020. Old natural forests: IPCC Forests table 4.9')
        removal_forest_type_dst.update_tags(
            extent='Full model extent')

        # Updates kwargs for the removal rate outputs-- just need to change datatype
        kwargs.update(dtype='float32')

        annual_gain_AGC_all_forest_types_dst = rasterio.open(annual_gain_AGC_all_forest_types, 'w', **kwargs)
        annual_gain_BGC_all_forest_types_dst = rasterio.open(annual_gain_BGC_all_forest_types, 'w', **kwargs)
        annual_gain_AGC_BGC_all_forest_types_dst = rasterio.open(annual_gain_AGC_BGC_all_forest_types, 'w', **kwargs)
        stdev_annual_gain_AGC_all_forest_types_dst = rasterio.open(stdev_annual_gain_AGC_all_forest_types, 'w', **kwargs)

        # Adds metadata tags to the output raster
        uu.add_rasterio_tags(annual_gain_AGC_all_forest_types_dst, sensit_type)
        annual_gain_AGC_all_forest_types_dst.update_tags(
            units='megagrams aboveground carbon/ha/yr')
        annual_gain_AGC_all_forest_types_dst.update_tags(
            source='Mangroves: IPCC wetlands supplement Table 4.4. Europe: Liz Goldman. Planted forests: Spatial Database of Planted Forests. USA: US FIA, via Rich Birdsey. Young natural forests: Cook-Patton et al. 2020. Old natural forests: IPCC Forests table 4.9')
        annual_gain_AGC_all_forest_types_dst.update_tags(
            extent='Full model extent')

        # Adds metadata tags to the output raster
        uu.add_rasterio_tags(annual_gain_BGC_all_forest_types_dst, sensit_type)
        annual_gain_BGC_all_forest_types_dst.update_tags(
            units='megagrams belowground carbon/ha/yr')
        annual_gain_BGC_all_forest_types_dst.update_tags(
            source='Mangroves: IPCC wetlands supplement Table 4.4. Europe: Liz Goldman. Planted forests: Spatial Database of Planted Forests. USA: US FIA, via Rich Birdsey. Young natural forests: Cook-Patton et al. 2020. Old natural forests: IPCC Forests table 4.9')
        annual_gain_BGC_all_forest_types_dst.update_tags(
            extent='Full model extent')

        # Adds metadata tags to the output raster
        uu.add_rasterio_tags(annual_gain_AGC_BGC_all_forest_types_dst, sensit_type)
        annual_gain_AGC_BGC_all_forest_types_dst.update_tags(
            units='megagrams aboveground + belowground carbon/ha/yr')
        annual_gain_AGC_BGC_all_forest_types_dst.update_tags(
            source='Mangroves: IPCC wetlands supplement Table 4.4. Europe: Liz Goldman. Planted forests: Spatial Database of Planted Forests. USA: US FIA, via Rich Birdsey. Young natural forests: Cook-Patton et al. 2020. Old natural forests: IPCC Forests table 4.9')
        annual_gain_AGC_BGC_all_forest_types_dst.update_tags(
            extent='Full model extent')

        # Adds metadata tags to the output raster
        uu.add_rasterio_tags(stdev_annual_gain_AGC_all_forest_types_dst, sensit_type)
        stdev_annual_gain_AGC_all_forest_types_dst.update_tags(
            units='standard deviation for removal factor, in terms of megagrams aboveground carbon/ha/yr')
        stdev_annual_gain_AGC_all_forest_types_dst.update_tags(
            source='Mangroves: IPCC wetlands supplement Table 4.4. Europe: Liz Goldman. Planted forests: Spatial Database of Planted Forests. USA: US FIA, via Rich Birdsey. Young natural forests: Cook-Patton et al. 2020. Old natural forests: IPCC Forests table 4.9')
        stdev_annual_gain_AGC_all_forest_types_dst.update_tags(
            extent='Full model extent')

        uu.print_log("  Creating removal model forest type tile, AGC removal factor tile, BGC removal factor tile, and AGC removal factor standard deviation tile for {}".format(tile_id))

        uu.check_memory()

        # Iterates across the windows (1 pixel strips) of the input tile
        for idx, window in windows:

            model_extent_window = model_extent_src.read(1, window=window)

            # Output rasters' windows
            removal_forest_type_window = np.zeros((window.height, window.width), dtype='uint8')
            annual_gain_AGC_all_forest_types_window = np.zeros((window.height, window.width), dtype='float32')
            annual_gain_BGC_all_forest_types_window = np.zeros((window.height, window.width), dtype='float32')
            stdev_annual_gain_AGC_all_forest_types_window = np.zeros((window.height, window.width), dtype='float32')

            try:
                age_category_window = age_category_src.read(1, window=window)
            except:
                age_category_window = np.zeros((window.height, window.width), dtype='uint8')

            # Lowest priority
            try:
                ipcc_AGB_default_rate_window = ipcc_AGB_default_src.read(1, window=window)
                ipcc_AGB_default_stdev_window = ipcc_AGB_default_stdev_src.read(1, window=window)
                # In no_primary_gain, the AGB_default_rate_window = 0, so primary forest pixels would not be
                # assigned a removal forest type and therefore get exclude from the model later.
                # That is incorrect, so using model_extent as the criterion instead allows the primary forest pixels
                # that don't have rates under this sensitivity analysis to still be included in the model.
                # Unfortunately, model_extent is slightly different from the IPCC rate extent (no IPCC rates where
                # there is no ecozone information), but this is a very small difference and not worth worrying about.
                if sensit_type == 'no_primary_gain':
                    removal_forest_type_window = np.where(model_extent_window != 0,
                                                          cn.old_natural_rank,
                                                          removal_forest_type_window).astype('uint8')
                else:
                    removal_forest_type_window = np.where(ipcc_AGB_default_rate_window != 0,
                                                          cn.old_natural_rank,
                                                          removal_forest_type_window).astype('uint8')
                annual_gain_AGC_all_forest_types_window = np.where(ipcc_AGB_default_rate_window != 0,
                                                                   ipcc_AGB_default_rate_window * cn.biomass_to_c_non_mangrove,
                                                                   annual_gain_AGC_all_forest_types_window).astype('float32')
                annual_gain_BGC_all_forest_types_window = np.where(ipcc_AGB_default_rate_window != 0,
                                                                   ipcc_AGB_default_rate_window * cn.biomass_to_c_non_mangrove * cn.below_to_above_non_mang,
                                                                   annual_gain_BGC_all_forest_types_window).astype('float32')
                stdev_annual_gain_AGC_all_forest_types_window = np.where(ipcc_AGB_default_stdev_window != 0,
                                                                   ipcc_AGB_default_stdev_window * cn.biomass_to_c_non_mangrove,
                                                                   stdev_annual_gain_AGC_all_forest_types_window).astype('float32')
            except:
                pass

            try: # young_AGC_rate_window uses > because of the weird NaN in the tiles. If != is used, the young rate NaN overwrites the IPCC arrays
                young_AGC_rate_window = young_AGC_src.read(1, window=window)
                young_AGC_stdev_window = young_AGC_stdev_src.read(1, window=window)
                # Using the > with the NaN results in non-fatal "RuntimeWarning: invalid value encountered in greater".
                # This isn't actually a problem, so the "with" statement suppresses it, per https://stackoverflow.com/a/58026329/10839927
                with np.errstate(invalid='ignore'):
                    removal_forest_type_window = np.where((young_AGC_rate_window > 0) & (age_category_window == 1),
                                                          cn.young_natural_rank,
                                                          removal_forest_type_window).astype('uint8')
                    annual_gain_AGC_all_forest_types_window = np.where((young_AGC_rate_window > 0) & (age_category_window == 1),
                                                                       young_AGC_rate_window,
                                                                       annual_gain_AGC_all_forest_types_window).astype('float32')
                    annual_gain_BGC_all_forest_types_window = np.where((young_AGC_rate_window > 0) & (age_category_window == 1),
                                                                       young_AGC_rate_window * cn.below_to_above_non_mang,
                                                                       annual_gain_BGC_all_forest_types_window).astype('float32')
                    stdev_annual_gain_AGC_all_forest_types_window = np.where((young_AGC_stdev_window > 0) & (age_category_window == 1),
                                                                       young_AGC_stdev_window,
                                                                       stdev_annual_gain_AGC_all_forest_types_window).astype('float32')

            except:
                pass

            if sensit_type != 'US_removals':
                try:
                    us_AGC_BGC_rate_window = us_AGC_BGC_src.read(1, window=window)
                    us_AGC_BGC_stdev_window = us_AGC_BGC_stdev_src.read(1, window=window)
                    removal_forest_type_window = np.where(us_AGC_BGC_rate_window != 0, cn.US_rank, removal_forest_type_window).astype('uint8')
                    annual_gain_AGC_all_forest_types_window = np.where(us_AGC_BGC_rate_window != 0,
                                                                       us_AGC_BGC_rate_window / (1 + cn.below_to_above_non_mang),
                                                                       annual_gain_AGC_all_forest_types_window).astype('float32')
                    annual_gain_BGC_all_forest_types_window = np.where(us_AGC_BGC_rate_window != 0,
                                                                       (us_AGC_BGC_rate_window) -
                                                                       (us_AGC_BGC_rate_window / (1 + cn.below_to_above_non_mang)),
                                                                       annual_gain_BGC_all_forest_types_window).astype('float32')
                    stdev_annual_gain_AGC_all_forest_types_window = np.where(us_AGC_BGC_stdev_window != 0,
                                                                       us_AGC_BGC_stdev_window / (1 + cn.below_to_above_non_mang),
                                                                       stdev_annual_gain_AGC_all_forest_types_window).astype('float32')
                except:
                    pass

            try:
                plantations_AGC_BGC_rate_window = plantations_AGC_BGC_src.read(1, window=window)
                plantations_AGC_BGC_stdev_window = plantations_AGC_BGC_stdev_src.read(1, window=window)
                removal_forest_type_window = np.where(plantations_AGC_BGC_rate_window != 0, cn.planted_forest_rank, removal_forest_type_window).astype('uint8')
                annual_gain_AGC_all_forest_types_window = np.where(plantations_AGC_BGC_rate_window != 0,
                                                                   plantations_AGC_BGC_rate_window / (1 + cn.below_to_above_non_mang),
                                                                   annual_gain_AGC_all_forest_types_window).astype('float32')
                annual_gain_BGC_all_forest_types_window = np.where(plantations_AGC_BGC_rate_window != 0,
                                                                   (plantations_AGC_BGC_rate_window ) -
                                                                   (plantations_AGC_BGC_rate_window / (1 + cn.below_to_above_non_mang)),
                                                                   annual_gain_BGC_all_forest_types_window).astype('float32')
                stdev_annual_gain_AGC_all_forest_types_window = np.where(plantations_AGC_BGC_stdev_window != 0,
                                                                   plantations_AGC_BGC_stdev_window / (1 + cn.below_to_above_non_mang),
                                                                   stdev_annual_gain_AGC_all_forest_types_window).astype('float32')
            except:
                pass

            try:
                europe_AGC_BGC_rate_window = europe_AGC_BGC_src.read(1, window=window)
                europe_AGC_BGC_stdev_window = europe_AGC_BGC_stdev_src.read(1, window=window)
                removal_forest_type_window = np.where(europe_AGC_BGC_rate_window != 0, cn.europe_rank, removal_forest_type_window).astype('uint8')
                annual_gain_AGC_all_forest_types_window = np.where(europe_AGC_BGC_rate_window != 0,
                                                                   europe_AGC_BGC_rate_window / (1 + cn.below_to_above_non_mang),
                                                                   annual_gain_AGC_all_forest_types_window).astype('float32')
                annual_gain_BGC_all_forest_types_window = np.where(europe_AGC_BGC_rate_window != 0,
                                                                   (europe_AGC_BGC_rate_window) -
                                                                   (europe_AGC_BGC_rate_window / (1 + cn.below_to_above_non_mang)),
                                                                   annual_gain_BGC_all_forest_types_window).astype('float32')
                # NOTE: Nancy Harris thought that the European removal standard deviations were 2x too large,
                # per email on 8/30/2020. Thus, simplest fix is to leave original tiles 2x too large and
                # correct them only where composited with other stdev sources.
                stdev_annual_gain_AGC_all_forest_types_window = np.where(europe_AGC_BGC_stdev_window != 0,
                                                                   (europe_AGC_BGC_stdev_window/2) / (1 + cn.below_to_above_non_mang),
                                                                   stdev_annual_gain_AGC_all_forest_types_window).astype('float32')
            except:
                pass

            # Highest priority
            try:
                mangroves_AGB_rate_window = mangrove_AGB_src.read(1, window=window)
                mangroves_BGB_rate_window = mangrove_BGB_src.read(1, window=window)
                mangroves_AGB_stdev_window = mangrove_AGB_stdev_src.read(1, window=window)
                removal_forest_type_window = np.where(mangroves_AGB_rate_window != 0, cn.mangrove_rank, removal_forest_type_window).astype('uint8')
                annual_gain_AGC_all_forest_types_window = np.where(mangroves_AGB_rate_window != 0,
                                                                   mangroves_AGB_rate_window * cn.biomass_to_c_mangrove,
                                                                   annual_gain_AGC_all_forest_types_window).astype('float32')
                annual_gain_BGC_all_forest_types_window = np.where(mangroves_BGB_rate_window != 0,
                                                                   mangroves_BGB_rate_window * cn.biomass_to_c_mangrove,
                                                                   annual_gain_BGC_all_forest_types_window).astype('float32')
                stdev_annual_gain_AGC_all_forest_types_window = np.where(mangroves_AGB_stdev_window != 0,
                                                                   mangroves_AGB_stdev_window * cn.biomass_to_c_mangrove,
                                                                   stdev_annual_gain_AGC_all_forest_types_window).astype('float32')
            except:
                pass

            # Masks outputs to model output extent
            removal_forest_type_window = np.where(model_extent_window == 1, removal_forest_type_window, 0)
            annual_gain_AGC_all_forest_types_window = np.where(model_extent_window == 1, annual_gain_AGC_all_forest_types_window, 0)
            annual_gain_BGC_all_forest_types_window = np.where(model_extent_window == 1, annual_gain_BGC_all_forest_types_window, 0)
            annual_gain_AGC_BGC_all_forest_types_window = annual_gain_AGC_all_forest_types_window + annual_gain_BGC_all_forest_types_window
            stdev_annual_gain_AGC_all_forest_types_window = np.where(model_extent_window == 1, stdev_annual_gain_AGC_all_forest_types_window, 0)

            # Writes the outputs window to the output files
            removal_forest_type_dst.write_band(1, removal_forest_type_window, window=window)
            annual_gain_AGC_all_forest_types_dst.write_band(1, annual_gain_AGC_all_forest_types_window, window=window)
            annual_gain_BGC_all_forest_types_dst.write_band(1, annual_gain_BGC_all_forest_types_window, window=window)
            annual_gain_AGC_BGC_all_forest_types_dst.write_band(1, annual_gain_AGC_BGC_all_forest_types_window, window=window)
            stdev_annual_gain_AGC_all_forest_types_dst.write_band(1, stdev_annual_gain_AGC_all_forest_types_window, window=window)

    # Prints information about the tile that was just processed
    uu.end_of_fx_summary(start, tile_id, cn.pattern_removal_forest_type, no_upload)