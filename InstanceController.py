import os
import subprocess
import sys
import time

processes = 0
dictChannelKeys = {}
dictChannelsin = {}
dictProcesses = {}


def addInstance(channel, processes):
    if channel in dictChannelKeys.keys():
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
    user_input = raw_input("Channel: ")

    if user_input in dictChannelKeys.keys():
        deleteInstance(user_input, processes)
    else:
        addInstance(user_input, processes)
