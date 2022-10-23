import sys
import os
# ========== Project Root Path =================
this_path = os.path.abspath(sys.path[0])
print("Hi there!  I'm __init__.py.")
project_dir = 'Web3HackerNetwork'
w3hndex = this_path.index(project_dir)
root_path = this_path[0:w3hndex + len(project_dir)]
# ---------- Local Library Path ----------------
if f'{root_path}/python' not in sys.path:
    sys.path.insert(0, f'{root_path}/python')
# ---------- Local Libraries ------------------- 