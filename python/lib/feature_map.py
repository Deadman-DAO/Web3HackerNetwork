import os
import json

def make_action( encoding, action, file_types ):
    return dict( encoding=encoding, action=action, file_types=file_types )

def get_actions():
    return [
        make_action( 'binary', 'img', ['png', 'jpg', 'gif', 'drawio'] ),
        make_action( 'binary', 'noextbin', ['noextbin'] ),
        make_action( 'text', 'javascript', ['js', 'jsx', 'ts', 'tsx', 'vue'] ),
        make_action( 'text', 'rust', ['rs', 'toml'] ),
        make_action( 'text', 'markdown', ['md'] ),
        make_action( 'text', 'json', ['json'] ),
        make_action( 'text', 'lock', ['lock'] ),
        make_action( 'text', 'yarn', ['yml', 'yaml']),
        make_action( 'text', 'html', ['html', 'css', 'scss']),
        make_action( 'text', 'clojure', ['clj']),
        make_action( 'text', 'shell', ['sh']),
        make_action( 'text', 'gitignore', ['gitignore']),
        make_action( 'text', 'noexttext', ['noexttext']),
    ]

def percent(numerator, denominator):
    if (numerator == 0): return 0
    if (denominator == 0): return 100
    truncated = int(100 * 100 * numerator / denominator)
    # Winsorizing the over-100% cases (which can happen, eg: when net bytes is 10 but this file added 100 bytes)
    # This is a short-term hack, need to revisit as we explore the meaning of adding, removing, and changing lines
    percent = truncated / 100
    if (percent > 100): return 100
    return truncated / 100

def addBinFeatures(typeArray, statDict, statName, file_types):
    singleTypeArray = [typeEntry for typeEntry in typeArray if typeEntry['fileType'] in file_types]
    statDict[statName + 'Files'] = sum([typeEntry['stats']['occurrences'] for typeEntry in singleTypeArray])
    statDict[statName + 'FilePct'] = percent(statDict[statName + 'Files'], statDict['totalFiles'])

def addTextFeatures(typeArray, statDict, statName, file_types):
    singleTypeArray = [typeEntry for typeEntry in typeArray if typeEntry['fileType'] in file_types]
    statDict[statName + 'Files'] = sum([typeEntry['stats']['occurrences'] for typeEntry in singleTypeArray])
    statDict[statName + 'Lines'] = sum([typeEntry['stats']['textLineCount'] for typeEntry in singleTypeArray])
    statDict[statName + 'FilePct'] = percent(statDict[statName + 'Files'], statDict['totalFiles'])
    statDict[statName + 'LinePct'] = percent(statDict[statName + 'Lines'], statDict['textLines'])

def extract_features(commit):
    if 'files' in commit:
        num_files = commit['files']
    else:
        num_files = commit['file']
    typeDict = commit['fileTypes']
    typeArray = [{'fileType': key, 'stats': typeDict[key]} for key in typeDict.keys()]
    textTypeArray = [typeEntry for typeEntry in typeArray if typeEntry['stats']['textLineCount'] > 0]
    binTypeArray = [typeEntry for typeEntry in typeArray if typeEntry['stats']['binByteCount'] > 0]
    
    statDict = {}
    statDict['commit'] = commit['commit']
    statDict['author'] = commit['Author']
    
    statDict['totalFiles'] = int(num_files)
    statDict['binFiles'] = sum([typeEntry['stats']['occurrences'] for typeEntry in binTypeArray])
    statDict['textFiles'] = sum([typeEntry['stats']['occurrences'] for typeEntry in textTypeArray])
    statDict['textLines'] = sum([typeEntry['stats']['textLineCount'] for typeEntry in textTypeArray])

    for action in get_actions():
        if (action['encoding'] == 'binary'):
            addBinFeatures(typeArray, statDict, action['action'], action['file_types'])
        elif (action['encoding'] == 'text'):
            addTextFeatures(typeArray, statDict, action['action'], action['file_types'])

    return statDict

def get_commit_features(all_commit_stats):
    all_features = []
    for commit in all_commit_stats:
        commit_id = commit['commit']
        commit_features = extract_features(commit)
        all_features.append(commit_features)
    return all_features;
