project_root_path = '.'
lib_path = project_root_path + '/python/lib/'
import json
import sys
sys.path.append(lib_path)
import commit_features

dataset_dir = project_root_path + '/data/github/2022-04-07-marine-search'
project_stats_dir = dataset_dir + '/projects'
classifier_features = [
    'binFiles','textFiles','textLines','javascriptLines','rustLines',
    'lockLines','htmlLines','jsonLines','markdownLines','imgFiles'
]
all_commit_features = commit_features.load_all(project_stats_dir, 'commit-stat.log.json')
X = commit_features.make_matrix(all_commit_features, classifier_features)

import pickle
model_path = project_root_path + '/sandbox/data/bob/logit-clf.dat'
fin = open(model_path, 'rb')
model_deserial = pickle.load(fin)
fin.close()
y_pred = model_deserial.predict(X)
print(len(y_pred))

hacker_histories = {}
for i in range(len(y_pred)):
    features = all_commit_features[i]
    pred = y_pred[i]
    author = features['author']
    features['predicted_class'] = pred
    if author not in hacker_histories: hacker_histories[author] = []
    hacker_commits = hacker_histories[author]
    hacker_commits.append(features)

import matplotlib.pyplot as plt

hacker_histograms = []
for hacker in hacker_histories.keys():
    commits = hacker_histories[hacker]
    commit_types = [commit['predicted_class'] for commit in commits]
    observed_types = list(set(commit_types))
    hacker_commit_types = []
    for observed_type in observed_types:
        observations = [1 for commit_type in commit_types if commit_type == observed_type]
        count = len(observations)
        hacker_commit_types.append(dict(num_commits=count, commit_type=observed_type))
    sorted_list = sorted(hacker_commit_types, key=lambda d: d['num_commits'])
    sorted_list.reverse()
    hacker_histograms.append(dict(hacker=hacker, commit_stats=sorted_list))

sorted_histograms = sorted(hacker_histograms, key=lambda d: d['hacker'].lower())
for histo in sorted_histograms:
    print(histo['hacker'])
    for row in histo['commit_stats']:
        print(str(row['num_commits']) + "\t" + str(row['commit_type']))
    print()
    break

import json

out_path = project_root_path + '/sandbox/data/bob/hacker_history.json'
out_handle = open(out_path, "w");
out_handle.write(json.dumps(sorted_histograms, indent=2));
out_handle.flush()
out_handle.close()
