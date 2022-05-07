import numpy as np

include_features = [
    'binFiles','textFiles','textLines','javascriptLines','rustLines',
    'lockLines','htmlLines','jsonLines','markdownLines','imgFiles'
]

include_features = [
    'binFiles', 'imgFiles', 'textFiles', 'configurationLines',
    'datascienceLines', 'htmlLines', 'javascriptLines', 'jsonLines',
    'markdownLines', 'noexttextLines', 'pydataLines', 'pythonLines',
    'solidityLines', 'txtLines', 'yarnLines'
]

fields = [
    'numCommits', 'binFiles', 'imgFilePct', 'textFiles', 'textLines',
    'configurationLinePct',
    'datascienceLinePct', 'htmlLinePct', 'javascriptLinePct', 'jsonLinePct',
    'markdownLinePct', 'noexttextLinePct', 'pydataLinePct', 'pythonLinePct',
    'solidityLinePct', 'txtLinePct', 'yarnLinePct'
] # , 'shellLinePct' , 'yarnLinePct'


def make_feature_vector(feature_dicts, feature_names):
    return [np.log1p(feature_dicts[name]) for name in feature_names]

features_dict = {}
X_full = []
for commit_features in all_commit_features:
    commit_id = commit_features['commit']
    features_dict[commit_id] = commit_features
    feature_vector = make_feature_vector(commit_features, include_features)
    X_full.append(feature_vector)

X = []
y = []
for commit_id, labelling_spreadsheet_row in data_df.iterrows():
    commit_features = features_dict[commit_id]
    feature_vector = make_feature_vector(commit_features, include_features)
    target_label = labelling_spreadsheet_row[0]
    X.append(feature_vector)
    y.append(target_label)
