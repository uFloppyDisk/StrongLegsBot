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
