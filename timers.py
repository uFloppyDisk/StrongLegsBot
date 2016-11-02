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
import sqlite3 as sql
import threading

import StrongLegsBot

StrongLegsBot.IRC().init()

sqlConnectionChannel = sql.connect(os.path.dirname(os.path.abspath(__file__)) + '\SLB.sqlDatabase\{}DB.db'
                                   .format(StrongLegsBot.IRC().CHANNEL.strip("#")))
sqlCursorChannel = sqlConnectionChannel.cursor()


class timer:
    def __init__(self):
        self.active_timers = {}
        self.test_timer = None

    def privmsg_timer(self, timer_delay, timer_privmsg):
        StrongLegsBot.IRC().send_privmsg(timer_privmsg)
        self.test_timer = threading.Timer(timer_delay, self.privmsg_timer, [timer_delay, timer_privmsg])
        self.test_timer.start()

    def cancel_timer(self):
        self.test_timer.cancel()

if __name__ == "__main__":
    timer_name = input('Test timer name: ')
    timer_privmsg = input('Test timer message: ')
    timer_delay = input('Test timer delay(secs): ')
    while True:
        pass
