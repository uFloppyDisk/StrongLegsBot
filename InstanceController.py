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

import os
import subprocess
import sys
import time

processes = 0
dictChannelKeys = {}
dictChannelsin = {}
dictProcesses = {}


def addInstance(channel, processes):
    if channel in list(dictChannelKeys.keys()):
        return

    opener = "open" if sys.platform == "darwin" else "python"
    process = subprocess.Popen([opener, "StrongLegsBot.py", channel, "info"])

    dictProcesses["%s" % processes] = process.pid
    dictChannelKeys["%s" % channel] = str(processes)
    processes += 1


def deleteInstance(channel, processes):
    pid = dictProcesses[dictChannelKeys[channel]]
    os.system("taskkill /pid %s /f" % str(pid))
    processes -= 1


channels_file = open("channels.txt", "r")
for channel in channels_file.readlines():
    time.sleep(2)
    addInstance(channel.strip("\n"), processes)

user_input = None

while user_input != "end":
    user_input = eval(input("Channel: "))

    if user_input in list(dictChannelKeys.keys()):
        deleteInstance(user_input, processes)
    else:
        addInstance(user_input, processes)
