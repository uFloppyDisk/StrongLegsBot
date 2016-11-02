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

import logging
import re

import unpackconfig


class filters:
    def __init__(self, irc, sqlconn, info, userlevel=0):
        self.cfg = unpackconfig.configUnpacker().unpackcfg()
        self.irc = irc
        self.sqlconn = sqlconn
        self.sqlConnectionChannel, self.sqlCursorChannel = self.sqlconn
        self.info = info

        self.sqlCursorChannel.execute('SELECT filtertype FROM filters')
        self.sqlCursorOffload = self.sqlCursorChannel.fetchall()

        self.sqlCursorChannel.execute('SELECT * FROM offenses WHERE userid == ?',
                                      (self.info["user-id"],))
        self.sqlCursorOffload = self.sqlCursorChannel.fetchone()

        if self.sqlCursorOffload is not None:
            self.UserOffenseCount = int(self.sqlCursorOffload[2])
        else:
            self.sqlCursorChannel.execute('INSERT INTO offenses (userid, username, offenses) VALUES (?, ?, ?)',
                                          (self.info["user-id"], self.info["username"], 0))
            self.sqlConnectionChannel.commit()
            self.UserOffenseCount = 0

    def spamprotection(self):
        pass

    def linkprotection(self):
        self.sqlCursorChannel.execute('SELECT * FROM filters WHERE filtertype == ?', ("link",))
        self.sqlCursorOffload = self.sqlCursorChannel.fetchone()

        if self.sqlCursorOffload is None:
            return False

        enabled = False
        ban_after_third = False

        if self.sqlCursorOffload[1] == 'true':
            enabled = True
        elif self.sqlCursorOffload[1] == 'false':
            return False

        if self.sqlCursorOffload[6] == 'true':
            ban_after_third = True
        elif self.sqlCursorOffload[6] == 'false':
            ban_after_third = False

        if enabled:
            if int(self.info['userlevel']) <= int(self.sqlCursorOffload[3]):
                if re.search(self.cfg['regex_filter_links'], self.info['privmsg']) is not None:
                    logging.info("Link discovered in %s from user %s", self.info["channel"], self.info["username"])
                    self.UserOffenseCount += 1
                    self.sqlCursorChannel.execute('UPDATE offenses SET offenses = ? WHERE userid = ?',
                                                  (self.UserOffenseCount, self.info["user-id"]))
                    self.sqlConnectionChannel.commit()

                    if 0 < self.UserOffenseCount <= 3:
                        reason = "(TIMEOUT) Automatically timed out for posting a link by StrongLegsBot"
                        self.irc.send_timeout(reason, self.info['username'],
                                              self.sqlCursorOffload[(self.UserOffenseCount + 2)])
                        self.irc.send_privmsg(self.sqlCursorOffload[7].format(**self.info))
                        return True

                    elif self.UserOffenseCount > 3 and not ban_after_third:
                        reason = "(TIMEOUT) Automatically timed out for posting a link by StrongLegsBot"
                        self.irc.send_timeout(reason, self.info['username'], self.sqlCursorOffload[5])
                        self.irc.send_privmsg(self.sqlCursorOffload[7].format(**self.info))
                        return True

                    elif self.UserOffenseCount > 3 and ban_after_third:
                        reason = "(BAN) Automatically banned for posting a link by StrongLegsBot"
                        self.irc.send_ban(reason, self.info['username'])
                        self.irc.send_privmsg(self.sqlCursorOffload[7].format(**self.info))
                        return True

                    else:
                        pass

        return False
