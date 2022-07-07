import pandas as pd
import os

"""
Stupid attempt to map class types to functions
DID NOT WORK
Without any explanation the type('stingy thingy') doesn't seem to EQUAL (at least on a hash level) 
    moby_dict[str, do_stringy_thingy_method.
It seemed like a cool idea, to be able to look up the right handler function in a map and call it.
"""


def iter_list(obj, directory):
    for n in obj:
        recurseword(n, directory)


def iter_vals(dic,  directory):
    for n in dic.values():
        recurseword(n, directory)


def unknown_type(thing,  directory):
    print('Unknown!')
    if hasattr(thing, '__iter__'):
        iter_list(thing, directory)
    else:
        print("I don't know what to do with this:", thing, dir(thing), type(thing))


file_map = {}


def process_dir_entry(dir_entry, directory):
    if dir_entry.is_dir():
#        print('Directory:', dir_entry.name, dir_entry.path, type(dir_entry))
        recurseword(os.scandir(dir_entry), directory+dir_entry.name+'/')
    else:
        if dir_entry.name not in file_map:
            file_map[dir_entry.name] = 0
        file_map[dir_entry.name] += 1


twist = {
    type([]): iter_list,
    type(()): iter_list,
    type({}): iter_vals
}


def recurseword(thingy, directory):
    twist.get(type(thingy), unknown_type)(thingy, directory)


scandir_iter = os.scandir('.')
dir_entry = next(scandir_iter)
twist[type(scandir_iter)] = iter_list
twist[type(dir_entry)] = process_dir_entry
print(twist)
recurseword(scandir_iter, './')
new_set = {}
for k, v in file_map.items():
    if v > 10:
        new_set[k] = v
pd.DataFrame(new_set, new_set.values())