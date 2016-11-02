"""
Copyright 2016 Pawel Bartusiak

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import _functions
import default_commands
import filters
import StrongLegsBot
import unpackconfig
import importlib


def reloadall():
    importlib.reload(unpackconfig)
    importlib.reload(StrongLegsBot)
    importlib.reload(_functions)
    importlib.reload(default_commands)
    importlib.reload(filters)
