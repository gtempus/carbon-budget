from subprocess import Popen, PIPE, STDOUT, check_call
from osgeo import gdal
import utilities
import glob
import shutil
import sys
sys.path.append('../')
import constants_and_names as cn
import universal_util as uu


def stack_ba_hv(hv_tile):

    start_year = 2000 + cn.loss_years
    end_year = 2000 + cn.loss_years + 1

    # Assumes that only the last year of fires are being processed
    for year in range(start_year, end_year): # End year is not included in burn year product

        # Download hdf files from s3 into folders by h and v
        output_dir = utilities.makedir('{0}/{1}/raw/'.format(hv_tile, year))
        utilities.download_df(year, hv_tile, output_dir)

        # convert hdf to array
        hdf_files = glob.glob(output_dir + "*hdf")

        if len(hdf_files) > 0:
            array_list = []
            for hdf in hdf_files:
                array = utilities.hdf_to_array(hdf)
                array_list.append(array)

            # stack arrays, get 1 raster for the year and tile
            stacked_year_array = utilities.stack_arrays(array_list)
            max_stacked_year_array = stacked_year_array.max(0)

            # convert stacked month arrays to 1 raster for the year
            template_hdf = hdf_files[0]

            year_folder = utilities.makedir('{0}/{1}/stacked/'.format(hv_tile, year))

            stacked_year_raster = utilities.array_to_raster(hv_tile, year, max_stacked_year_array, template_hdf,
                                                            year_folder)

            # upload to s3
            cmd = ['aws', 's3', 'cp', stacked_year_raster, cn.burn_year_stacked_hv_tif_dir]
            uu.log_subprocess_output_full(cmd)

            # remove files
            shutil.rmtree(output_dir)

        else:
            pass
