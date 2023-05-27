############# Command line tool create a 3D map from presets' values ##################################################################################
############# Alessandro Anatrini 2021 rev. 2023 ######################################################################################################

import argparse
from utils import *


### Args parser
parser = argparse.ArgumentParser(description="device2map is a python script that generate a a 3Dmap from a .json file contained presets' values.")

    ### Positional arguments
parser.add_argument('json_path', action='store', type=str, help="Path to a json containing presets' data.")
parser.add_argument('map', action='store', type=str, help="Name of the generated map.")

    ### Optional arguments
parser.add_argument('-scaler', default='none', type=str, help="Set the scaling method: 'standard', 'min_max', 'robust'. Default='none'.")
parser.add_argument('-dim', default='principal_component', type=str, help="Set the dimensionality reduction method: 'principal_component', 'singular_value', 'indipendent_component', 'isometric_mapping', 'uniform_manifold'. Default='principal_component'.")


args = parser.parse_args()

### Load from file and format to dataframe
data = pd.read_json(args.json_path)
data = data.T.reset_index()
data.rename(columns={'index': 'preset_name'}, inplace=True)
df = pd.DataFrame(data['data'].values.tolist(), data['preset_name']).add_prefix('param' + '_')
df_param = df.copy().reset_index(drop=True)


### Generate a map
ask_map = str(input("Do you want to generate a map ? (y/n): ")).lower().strip()
if prompt_bool(ask_map) is True :

    # scaling (perhaps not necessary since values are already normalised, but worth having it to build statistics)
    if args.scaler :
        df_scaler = scaler(df_param, args.scaler)
    else :
        df_scaler = df_param
    # reduction
    df_reduction = dim_reduction(df_scaler, args.dim)
    eval_variance(df_reduction)
    # create min max xyz dict for conversion
    d_mimax = {}
    d_mimax['min'] = df_reduction.min(axis=0).tolist()
    d_mimax['max'] = df_reduction.max(axis=0).tolist()
    make_mimax = DictUtils(d_mimax)
    mimax_name = 'mimax_{0}'.format(args.map)
    make_mimax.new_dict(mimax_name, STATS_DIR)
    print('A file named {} contaning minimum and maximum values for each axes has been created.'.format(mimax_name))

    # write map
    dict_map = make_map(data, df_scaler, df_reduction)
    make_map = DictUtils(dict_map)
    make_map.new_dict(args.map, MAP_DIR)
    print('A map named {} has been created.'.format(args.map))
else :
    exit(0)

ask_stats = str(input("Do you want to generate statistics for inverse conversion ? (y/n): ")).lower().strip()
if prompt_bool(ask_stats) is True :

    # store a statistics dict for inverse scaling on max
    df_stats = df_param.describe().iloc[1:, :].reset_index()
    df_stats.rename(columns={'index': 'statistics'}, inplace=True)
    dict_stats = dict(zip(df_stats['statistics'], df_stats.iloc[:, 1:].values.tolist())) # drop first column because it contains statistics measurement's name
    make_stats = DictUtils(dict_stats)
    stats_name = 'stats_{0}'.format(args.map)
    make_stats.new_dict(stats_name, STATS_DIR)
    print('A file named {} contaning presets\' statistics has been created.'.format(stats_name))
else :
    exit(0)

