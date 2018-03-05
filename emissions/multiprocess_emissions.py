import multiprocessing
import subprocess
import calc_emissions
import utilities
import tile_peat_dict


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


biomass_tile_list = ['10S_170E', '10S_170W', '10S_180W', '20N_000E', '20N_010E', '20N_010W', '20N_020E', '20N_020W', '20N_030E', '20N_030W', '20N_040E', '20N_050E', '20N_060W', '20N_070E', '20N_070W', '20N_080E', '20N_080W', '20N_090E', '20N_090W', '20N_100E', '20N_100W', '20N_110E', '20N_110W', '20N_120E', '20N_120W', '20N_130E', '20N_140E', '20N_160E', '20N_160W', '20N_170E', '20N_170W', '20S_010E', '20S_020E', '20S_030E', '20S_030W', '20S_040E', '20S_050E', '20S_050W', '20S_060W', '20S_070W', '20S_080W', '20S_090W', '20S_110E', '20S_110W', '20S_120E', '20S_130E', '20S_130W', '20S_140E', '20S_140W', '20S_150E', '20S_150W', '20S_160E', '20S_160W', '20S_170E', '20S_180W', '30N_000E', '30N_010E', '30N_010W', '30N_020E', '30N_020W', '30N_030E', '30N_040E', '30N_050E', '30N_060E', '30N_070E', '30N_080E', '30N_080W', '30N_090E', '30N_090W', '30N_100E', '30N_100W', '30N_110E', '30N_110W', '30N_120E', '30N_120W', '30N_130E', '30N_140E', '30N_150E', '30N_160W', '30N_170W', '30N_180W', '30S_010E', '30S_020E', '30S_020W', '30S_030E', '30S_060W', '30S_070E', '30S_070W', '30S_080W', '30S_090W', '30S_110E', '30S_120E', '30S_130E', '30S_140E', '30S_150E', '30S_170E', '30S_180W', '40N_000E', '40N_010E', '40N_010W', '40N_020E', '40N_020W', '40N_030E', '40N_030W', '40N_040E', '40N_040W', '40N_050E', '40N_060E', '40N_070E', '40N_070W', '40N_080E', '40N_080W', '40N_090E', '40N_090W', '40N_100E', '40N_100W', '40N_110E', '40N_110W', '40N_120E', '40N_120W', '40N_130E', '40N_130W', '40N_140E', '40S_010W', '40S_020W', '40S_030E', '40S_050E', '40S_060E', '40S_070E', '40S_070W', '40S_080W', '40S_140E', '40S_160E', '40S_170E', '40S_180W', '50N_000E', '50N_010E', '50N_010W', '50N_020E', '50N_030E', '50N_040E', '50N_050E', '50N_060E', '50N_060W', '50N_070E', '50N_070W', '50N_080E', '50N_080W', '50N_090E', '50N_090W', '50N_100E', '50N_100W', '50N_110E', '50N_110W', '50N_120E', '50N_120W', '50N_130E', '50N_130W', '50N_140E', '50N_150E', '50S_000E', '50S_030W', '50S_040W', '50S_050W', '50S_060E', '50S_060W', '50S_070E', '50S_070W', '50S_080W', '50S_150E', '50S_160E', '50S_170E', '60N_000E', '60N_010E', '60N_010W', '60N_020E', '60N_020W', '60N_030E', '60N_040E', '60N_050E', '60N_050W', '60N_060E', '60N_060W', '60N_070E', '60N_070W', '60N_080E', '60N_080W', '60N_090E', '60N_090W', '60N_100E', '60N_100W', '60N_110E', '60N_110W', '60N_120E', '60N_120W', '60N_130E', '60N_130W', '60N_140E', '60N_140W', '60N_150E', '60N_150W', '60N_160E', '60N_160W', '60N_170E', '60N_170W', '60N_180W', '70N_000E', '70N_010E', '70N_010W', '70N_020E', '70N_020W', '70N_030E', '70N_030W', '70N_040E', '70N_040W', '70N_050E', '70N_050W', '70N_060E', '70N_060W', '70N_070E', '70N_070W', '70N_080E', '70N_080W', '70N_090E', '70N_090W', '70N_100E', '70N_100W', '70N_110E', '70N_110W', '70N_120E', '70N_120W', '70N_130E', '70N_130W', '70N_140E', '70N_140W', '70N_150E', '70N_150W', '70N_160E', '70N_160W', '70N_170E', '70N_170W', '70N_180W', '80N_010E', '80N_010W', '80N_020E', '80N_020W', '80N_030E', '80N_030W', '80N_040E', '80N_040W', '80N_050E', '80N_050W', '80N_060E', '80N_060W', '80N_070E', '80N_070W', '80N_080E', '80N_080W', '80N_090E', '80N_090W', '80N_100E', '80N_100W', '80N_110E', '80N_110W', '80N_120E', '80N_120W', '80N_130E', '80N_130W', '80N_140E', '80N_140W', '80N_150E', '80N_150W', '80N_160E', '80N_160W', '80N_170E', '80N_170W', '80N_180W']

tiles_in_chunk = 5

for chunk in chunks(biomass_tile_list, tiles_in_chunk):

    with open('status.txt', 'a') as textfile:
        textfile.write(str(chunk) + "\n")

    for tile_id in chunk:
        print tile_id

        # download files
        peat_file = tile_peat_dict.tile_peat_dict(tile_id) # based on tile id, know which peat file to download (hwsd, hist, jukka)

        files = {'carbon_pool':['bgc', 'carbon', 'deadwood', 'soil', 'litter'], 'data_prep': [peat_file, 'fao_ecozones_bor_tem_tro', 'ifl_2000', 'gfw_plantations', 'tsc_model', 'climate_zone'], 'burned_area':['burn_loss_year']}

        utilities.download(files, tile_id)

        #download hansen tile
        hansen_tile = utilities.wgetloss(tile_id)

        #if idn plant tile downloaded, mask loss with plantations because we know that idn gfw_plantations
        # were established in yr 2000.
        if tile_id in ['00N_090E', '00N_100E', '00N_110E', '00N_120E', '00N_130E', '00N_140E', '10N_090E', '10N_100E', '10N_110E', '10N_120E', '10N_130E', '10N_140E']:
            print "cutting out plantations in idn, mys"
            utilities.mask_loss(tile_id)

    count = multiprocessing.cpu_count()
    pool = multiprocessing.Pool(processes=20)
    pool.map(calc_emissions.calc_emissions, chunk)
