import re

go_source = open('../data/go_import.go', 'r')
#pattern = r'import[\s\r\n]*\([_\."\w\r\n]*([a-z_/]*)[_\."\w\r\n]*\)'
pattern = r'import[\s\r\n]*\((?:(?:[^\"\)]|[\s\r\n])*\"([^\"]*)\"[^\"]*)*\)'
pattern = r'import([\s\w\r\n]*)import'
pattern = r'multiline(?:\r|\n|\r\n|\n\r)*( potato )(?:\r|\n|\r\n|\n\r)*multiline'
go_import_regex = re.compile(pattern, re.MULTILINE)

for go in go_source:
    match = go_import_regex.search(go)
    if match:
        print(match.groups())
