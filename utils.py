import json
import numpy as np
import os
import pandas as pd
import umap

from sklearn import manifold
from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler
from sklearn.decomposition import FastICA, PCA, TruncatedSVD



### Reduction constants
MAP_IO = ['input', 'output']
N_COMPS = 3
NEIGHBORS = 5
DISTANCE = 0.3

### Folder names
MAP_DIR = 'maps'
STATS_DIR = 'statistics'


##############################################################
##############################################################
### User utilities
    # user prompt
def prompt_bool(check):
    try :
        if check[0] == 'y':
            return True
        elif check[0] == 'n':
            return False
        else:
            print('Invalid Input')
            return prompt_bool()
    except Exception as error:
        print('Please enter valid inputs !!!')
        print(error)
        return prompt_bool()


##############################################################
##############################################################
### Dictionary utilities
class DictUtils(dict):

    '''Class to perform different kind of operations within a dictionary'''
    def __init__(self, d={}):
        self.dict = d  

    # write dictionary to a file
    def new_dict(self, file_name, dir):

        path = os.getcwd()
        path_map = '{0}/{1}'.format(path, dir)
        
        if os.path.isdir(path_map) is False :
            os.makedirs(path_map)
            
        path_abs = os.path.join(path_map, file_name + '.json')
        
        with open(path_abs, 'w') as file :
            file.write('')
            json.dump(self.dict, file, indent=3)
            file.close()


##############################################################
##############################################################
### Scaling and reducer utilities
    # scaling functions
def none(df):
    return df

def standard(df):
    ss_features = StandardScaler().fit_transform(df.values)
    df_ss_features = pd.DataFrame(ss_features, index=df.index, columns=df.columns)
    return df_ss_features
    
def min_max(df):
    mm_features = MinMaxScaler().fit_transform(df.values)
    df_mm_features = pd.DataFrame(mm_features, index=df.index, columns=df.columns)
    return df_mm_features

def robust(df):
    rs_features = RobustScaler().fit_transform(df.values)
    df_rs_features = pd.DataFrame(rs_features, index=df.index, columns=df.columns)
    return df_rs_features

def invalid_scaler(df):
    raise Exception('Invalid scaler selection!!!')

def scaler(x, choosen_scaler='standard') :
    scl = {
        'none': none,
        'standard': standard,
        'min_max': min_max,
        'robust': robust
    }
    choosen_scaler_function = scl.get(choosen_scaler, invalid_scaler)
    return choosen_scaler_function(x)


    # dimensionality reduction functions
def principal_component(df):
    pca = PCA(n_components=N_COMPS).fit_transform(df.values)
    return pca

def singular_value(df):
    svd = TruncatedSVD(n_components=N_COMPS, random_state=42).fit_transform(df.values)
    return svd

def indipendent_component(df):
    ica = FastICA(n_components=N_COMPS, random_state=42).fit_transform(df.values)
    return ica

def isometric_mapping(df):
    iso = manifold.Isomap(n_neighbors=NEIGHBORS, n_components=N_COMPS, n_jobs=-1).fit_transform(df.values)
    return iso

def uniform_manifold(df):
    ump = umap.UMAP(n_neighbors=NEIGHBORS, min_dist=DISTANCE, n_components=N_COMPS).fit_transform(df.values)
    return ump

def invalid_reduction(df):
    raise Exception('Invalid dimensionality reduction method!!!')

def dim_reduction(x, choosen_reduction='principal_component'):
    red = {
        'principal_component': principal_component,
        'singular_value': singular_value,
        'indipendent_component': indipendent_component,
        'isometric_mapping': isometric_mapping,
        'uniform_manifold': uniform_manifold
    }
    choosen_reduction_function = red.get(choosen_reduction, invalid_reduction)
    return choosen_reduction_function(x)

def eval_variance(df):
    x = df[:,0]
    y = df[:,1]
    z = df[:,2]

    bound_pts = np.array([np.ptp(x), np.ptp(y), np.ptp(z)])
    # scale to unit length
    two_norm = np.linalg.norm(bound_pts)
    # estimate variance (Bessel correction)
    range_unit_length = [item / two_norm for item in bound_pts]
    score = np.float_power(np.std(range_unit_length), 2)
    print('The choosen scaler and reduction method generate a space with a variance of {}.'.format(score))

### Create map for linear regression on max (uses numerical index, for maps without bank/preset_name)
def make_map(data, df_out, df_in):

    df_out['name'] = data['preset_name']
    df_out['io'] = MAP_IO[1]

    # convert df into dictionary
    dict_out = dict(zip(df_out['name'], df_out.values.tolist()))
    # set index to select from arr_in
    i = -1
    dict_map = {}
    for key, value in dict_out.items() :
        i += 1
        # the constant in last column becomes a key ('output') of a subdict, key 'input' contains the values of dimensionality reduction 
        dict_map[key] = {MAP_IO[1]: value[:-2], MAP_IO[0]: df_in[i].tolist()}

    # return a dict to be used for linear regression
    return dict_map