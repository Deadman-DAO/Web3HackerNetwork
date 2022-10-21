import os
import sys

relative_project_root = '../../../..'
relative_lib_root = f'{relative_project_root}/python'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), relative_lib_root))
from w3hn.dependency.python import PythonDependencyAnalyzer

analyzer = PythonDependencyAnalyzer()

src_path = 'data/samples/source/python/imports.py'
relative_src_path = f'{relative_project_root}/{src_path}'
src_path = os.path.join(os.path.dirname(__file__), relative_src_path)

deps = analyzer.get_dependencies(src_path)
for dep in deps:
    print(dep)

