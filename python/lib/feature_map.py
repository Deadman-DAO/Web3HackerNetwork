import os
import json

def make_action( encoding, action, file_types ):
    return dict( encoding=encoding, action=action, file_types=file_types )

def get_actions(project_root_path):
    in_path = project_root_path + '/python/cfg/action_types.json'
    return json.loads(open(in_path, 'r').read())
    # return [
    #     make_action( 'binary', 'img', ['png', 'jpg', 'gif', 'drawio', 'svg'] ),
    #     make_action( 'binary', 'noextbin', ['noextbin'] ),
    #     make_action( 'text', 'clojure', ['clj']),
    #     make_action( 'text', 'configuration', ['ini', 'cfg', 'conf']),
    #     make_action( 'text', 'datascience', ['ipynb']),
    #     make_action( 'text', 'gitignore', ['gitignore']),
    #     make_action( 'text', 'html', ['html', 'css', 'scss']),
    #     make_action( 'text', 'javascript', ['js', 'jsx', 'ts', 'tsx', 'vue'] ),
    #     make_action( 'text', 'json', ['json'] ),
    #     make_action( 'text', 'lock', ['lock'] ),
    #     make_action( 'text', 'markdown', ['md'] ),
    #     make_action( 'text', 'noexttext', ['noexttext']),
    #     make_action( 'text', 'pydata', ['rst'] ), # ReStructuredText, python data
    #     make_action( 'text', 'python', ['py'] ),
    #     make_action( 'text', 'rust', ['rs', 'toml'] ),
    #     make_action( 'text', 'shell', ['sh']),
    #     make_action( 'text', 'solidity', ['sol']),
    #     make_action( 'text', 'txt', ['txt']),
    #     make_action( 'text', 'yarn', ['yml', 'yaml']),
    # ]

def percent(numerator, denominator):
    if (numerator == 0): return 0
    if (denominator == 0): return 100
    truncated = int(100 * 100 * numerator / denominator)
    return truncated / 100

def sum_stat(dicts, key):
    return sum([a_dict['stats'][key] for a_dict in dicts])

def addBinFeatures(typeArray, statDict, statName, file_types):
    singleTypeArray = [typeEntry for typeEntry in typeArray if typeEntry['fileType'] in file_types]
    statDict[statName + 'Files'] = sum_stat(singleTypeArray, 'occurrences')
    statDict[statName + 'FilePct'] = percent(statDict[statName + 'Files'], statDict['totalFiles'])

def addTextFeatures(typeArray, statDict, statName, file_types):
    singleTypeArray = [typeEntry for typeEntry in typeArray if typeEntry['fileType'] in file_types]
    statDict[statName + 'Files'] = sum_stat(singleTypeArray, 'occurrences')
    statDict[statName + 'Lines'] = sum_stat(singleTypeArray, 'inserts')
    statDict[statName + 'FilePct'] = percent(statDict[statName + 'Files'], statDict['totalFiles'])
    statDict[statName + 'LinePct'] = percent(statDict[statName + 'Lines'], statDict['textLines'])

def extract_features(project_root_path, commit):
    typeDict = commit['fileTypes']
    typeArray = [{'fileType': key, 'stats': typeDict[key]} for key in typeDict.keys()]
    textTypeArray = [typeEntry for typeEntry in typeArray if typeEntry['stats']['inserts'] > 0 or typeEntry['stats']['deletes'] > 0]
    binTypeArray = [typeEntry for typeEntry in typeArray if typeEntry['stats']['inserts'] == 0 and typeEntry['stats']['deletes'] == 0]

    occurrences_list = [type_entry['stats']['occurrences'] for type_entry in typeArray]
    num_files = sum(occurrences_list)
    
    statDict = {}
    statDict['commit'] = commit['commit']
    statDict['author'] = commit['Author']
    
    statDict['totalFiles'] = int(num_files)
    statDict['binFiles'] = sum_stat(binTypeArray, 'occurrences')
    statDict['textFiles'] = sum_stat(textTypeArray, 'occurrences')
    statDict['textLines'] = sum_stat(textTypeArray, 'inserts')

    actions = get_actions(project_root_path)
    for action in actions:
        action_code = action['action']
        types = action['file_types']
        if (action['encoding'] == 'binary'):
            addBinFeatures(typeArray, statDict, action_code, types)
        elif (action['encoding'] == 'text'):
            addTextFeatures(typeArray, statDict, action_code, types)

    return statDict

def get_commit_features(project_root_path, all_commit_stats):
    all_features = []
    for commit in all_commit_stats:
        commit_id = commit['commit']
        commit_features = extract_features(project_root_path, commit)
        all_features.append(commit_features)
    return all_features;
