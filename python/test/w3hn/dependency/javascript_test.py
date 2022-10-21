import os
import sys

# ========== Project Root Path =================
this_path = os.path.abspath(sys.path[0])
project_dir = 'Web3HackerNetwork'
w3hndex = this_path.index(project_dir)
root_path = this_path[0:w3hndex + len(project_dir)]
# ---------- Local Library Path ----------------
if f'{root_path}/python' not in sys.path:
    sys.path.insert(0, f'{root_path}/python')
# ---------- Local Libraries -------------------
from w3hn.dependency.javascript import JavascriptDependencyAnalyzer
# ----------------------------------------------

analyzer = JavascriptDependencyAnalyzer()

src_path = f'{root_path}/data/samples/source/javascript/dependencies.js'

deps = analyzer.get_dependencies(src_path)
print()
print("Found the following dependencies:")
for dep in deps:
    print(dep)

