import numpy as np
import pandas as pd
#import json
#import sys
#sys.path.append('.') # this lib was loaded; sys.path must already include this dir
import commit_stats
import feature_map

# see make_hacker_history.py for example use
def load_all(path, file_name):
    all_commit_stats = commit_stats.load_commit_stats(file_name, path)
    all_commit_features = feature_map.get_commit_features(all_commit_stats)
    return all_commit_features

def make_vector(feature_dict, feature_names):
    return [np.log1p(feature_dict[name]) for name in feature_names]

# see make_hacker_history.py for example use
def make_matrix(all_feature_dicts, feature_names):
    X = []
    for feature_dict in all_feature_dicts:
        commit_id = feature_dict['commit']
        feature_vector = make_vector(feature_dict, feature_names)
        X.append(feature_vector)
    return X

# passsing in all_feature_dicts will become a memory problem
def make_training_set(labeling_path, all_feature_dicts, selected_features):
    data_df = pd.read_csv(labeling_path, sep='\t', index_col=0)
    features_dict = {}
    for features in all_feature_dicts:
        commit_id = features['commit']
        features_dict[commit_id] = features
    X = []
    y = []
    for commit_id, labelling_spreadsheet_row in data_df.iterrows():
        commit_features = features_dict[commit_id]
        feature_vector = make_vector(commit_features, selected_features)
        target_label = labelling_spreadsheet_row[0]
        X.append(feature_vector)
        y.append(target_label)
    return X, y
