import re
import json
import os
import sys

relative_lib = "../../../../python"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), relative_lib))
from w3hn.dependency.python import PythonDependencyAnalyzer

from django.contrib import admin, bus, car

from as_things_with_commas import admin as adm, bus as long_car, car as short_bus

import django.contrib

import django.contrib.admin

foo = django.contrib.bus.get_num_riders()

from blah import bar
