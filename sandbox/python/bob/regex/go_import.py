import re

'''
Breadcrumbs:
  Go Imports:
https://golangdocs.com/import-in-golang
https://www.digitalocean.com/community/tutorials/importing-packages-in-go

  Python Regex:
https://www.w3schools.com/python/python_regex.asp
https://coderslegacy.com/python/regex-match-multiline-text/
https://www.thegeekstuff.com/2014/07/advanced-python-regex/
'''

go_source = open('../data/go_import.go', 'r')
#pattern = r'import[\s\r\n]*\([_\."\w\r\n]*([a-z_/]*)[_\."\w\r\n]*\)'
pattern = r'import[\s\r\n]*\((?:(?:[^\"\)]|[\s\r\n])*\"([^\"]*)\"[^\"]*)*\)'
#pattern = r'multiline(?:\r|\n|\r\n|\n\r)*( potato )(?:\r|\n|\r\n|\n\r)*multiline'
pattern = r'multiline(?:.)*(_potato_)(?:.)*multiline'
go_import_regex = re.compile(pattern, re.MULTILINE & re.DOTALL)
# go_import_regex = re.compile(pattern, re.MULTILINE)
# go_import_regex = re.compile(pattern, re.DOTALL)

print("---------- READING FULL SOURCE ---------------")
full_source = go_source.read()
match = go_import_regex.search(full_source)
if match:
    print(match.groups())

print("---------- FULL SOURCE FINDALL ----------------")
pattern = r'multiline(?:.)*(_potato_)(?:.)*multiline'
print(re.findall(pattern, full_source, re.MULTILINE))
print(re.findall(pattern, full_source, re.DOTALL))
print(re.findall(pattern, full_source, re.MULTILINE & re.DOTALL))

print("---------- READING LINE BY LINE ---------------")
for go in go_source:
    print(f'testing:{go}')
    match = go_import_regex.search(full_source)
    if match:
        print(match.groups())

print("---------- COPY OF EXAMPLE CODE ---------------")
mystring="""This is some random text.
Hello World.
This is Goodbye.
"""

print(re.findall("^This.*", mystring, re.MULTILINE))
