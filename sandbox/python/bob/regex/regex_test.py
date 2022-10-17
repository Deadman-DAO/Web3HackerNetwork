import re

import regex

foo = "a{b{c}{d}}"

matches = regex.findall('(\{([^{}]|(?R))*\})', foo)

for match in matches:
    print(match)

#
bar = """ (outer1
   (center2
     (inner3)
     (inner4)
   center5)
 outer6)
 (outer7
   (inner8)
 outer9)
 (outer10
 outer11)
"""

pattern = '(\(([^()]|(?R))*\))'
pattern = '\(((?>[^()]+)|(?R))*\)'

matches = regex.findall(pattern, bar)
for match in matches:
    print(match)
    

# def recurse(line):
#     if '{' in line:
#         parts = re.findall('([^{]*){([^}]*)}(.*)', line)
#         deeper_parts = recurse(parts[1])
#         trailing_parts = recurse(parts[2])
#     else:
#         return None

# recurse(foo)



Don't use regex.

Instead, a simple recursive function will suffice. Here's the general structure:

def recursive_bracket_parser(s, i):
    while i < len(s):
        if s[i] == '(':
            i = recursive_bracket_parser(s, i+1)
        elif s[i] == ')':
            return i+1
        else:
            # process whatever is at s[i]
            i += 1
    return i

For example, here's a function that will parse the input into a nested list structure:

def parse_to_list(s, i=0):
    result = []
    while i < len(s):
        if s[i] == '(':
            i, r = parse_to_list(s, i+1)
            result.append(r)
        elif s[i] == ')':
            return i+1, result
        else:
            result.append(s[i])
            i += 1
    return i, result

Calling this like parse_to_list('((a) ((b)) ((c)(d)))efg') produces the result [[['a'], ' ', [['b']], ' ', [['c'], ['d']]], 'e', 'f', 'g'].
