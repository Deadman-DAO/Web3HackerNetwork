import numpy as np
#import json
#import sys
#sys.path.append('.') # this lib was loaded; sys.path must already include this dir
import commit_stats
import feature_map

def load_all(path, file_name):
    all_commit_stats = commit_stats.load_commit_stats(file_name, path)
    all_commit_features = feature_map.get_commit_features(all_commit_stats)
    return all_commit_features

def make_vector(feature_dict, feature_names):
    return [np.log1p(feature_dict[name]) for name in feature_names]

def make_matrix(all_feature_dicts, feature_names):
    X = []
    for feature_dict in all_feature_dicts:
        commit_id = feature_dict['commit']
        feature_vector = make_vector(feature_dict, feature_names)
        X.append(feature_vector)
    return X
