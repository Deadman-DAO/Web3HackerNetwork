import re
import json

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

def get_dependencies(path):
    depends = list()

    # capture single-line imports
    full_source = ""
    go_source = open('../data/go_import.go', 'r')
    for go_line in go_source:
        # print(go_line)
        go_line = re.sub("//.*", "", go_line)
        # print(go_line)
        deps = re.findall('import[^\"]*\"([^\"]*)\"', go_line)
        depends.extend(deps)
        full_source += go_line

    # print(full_source)
    ptrn = "import[^\(]*\(([^\)]*)\)"
    # print(re.findall(ptrn, full_source, re.DOTALL))
    lines = re.findall(ptrn, full_source, re.DOTALL)
    for line in lines:
        deps = re.findall('[^\"]*\"([^\"]*)\"[^\"]*', line, re.DOTALL)
        depends.extend(deps)

    return list(set(depends))

print()
print("Target Raw Data Form")
owner = "apache"
repo_name = "ant"
path = '../data/go_import.go'
dependencies = get_dependencies(path)
print('owner\trepo_name\tfile_path\tdependency')
for dep in dependencies:
    print(f'{owner}\t{repo_name}\t{path}\t{dep}')

file_dependencies = dict()
file_dependencies[path] = dependencies

repo_dict = dict()
repo_dict['owner'] = 'apache'
repo_dict['repo_name'] = 'ant'
repo_dict['file_dependencies'] = {path: dependencies}

print()
print("Target JSON Data Form")
print(json.dumps(repo_dict, indent=2))
print()


def other_old():
    go_source = open(path, 'r')
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

    print("--------- 2 match dotall ---------------")
    mystring = """import ("foo")
    import (
    "bar"
    )
    import ( "zoom" // annoying comment about "dave"
    "schwartz"
    )
    """
    ptrn = "import \(([^\)]*)\)"
    print(re.findall(ptrn, mystring, re.DOTALL))
    lines = re.findall(ptrn, mystring, re.DOTALL)
    depends = list()
    for line in lines:
        deps = re.findall('[^\"]*\"([^\"]*)\"[^\"]*', line, re.DOTALL)
        depends.extend(deps)
    print(depends)


def borken():
    print("------------- 2 match dotal 2 ------------")
    ptrn = "import \([^\"\)]*\"([^\"]*)\"[^\"\)]*\)"
    print(re.findall(ptrn, mystring, re.DOTALL))

    print("------------- 2 match dotal 2 ------------")
    ptrn = "import +\((?:[^\"\)]*\"([^\"]*)\"[^\"\)]*)*\)"
    print(re.findall(ptrn, mystring, re.DOTALL))

    print("---------- EXAMPLE MULTILINE ---------------")
    mystring="""This is some random text.
    Hello World.
    This is Goodbye.
    """

    print(re.findall("^This.*", mystring, re.MULTILINE))


    print("---------- EXAMPLE DOTALL ---------------")
    mystring="""This is some random text.
    Hello World.
    This is Goodbye.
    """

    print(re.findall("^This.*", mystring, re.DOTALL))

    print("---------- EXAMPLE DOTALL & MULTILINE ---------------")
    mystring="""This is some random text.
    Hello World.
    This is Goodbye.
    """

    print(re.findall("^This.*", mystring, re.DOTALL & re.MULTILINE))

    print("---------- READING LINE BY LINE ---------------")
    for go in go_source:
        print(f'testing:{go}')
        match = go_import_regex.search(full_source)
        if match:
            print(match.groups())

