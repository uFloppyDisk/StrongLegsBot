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

        self.sqlCursorChannel.execute('CREATE TABLE IF NOT EXISTS filters'
                                      '(filtertype TEXT, enabled TEXT, maxuserlevel INTEGER, first_timeout INTEGER, '
                                      'second_timeout INTEGER, third_timeout INTEGER, ban_after_third TEXT, message TEXT)')
        self.sqlConnectionChannel.commit()

        self.sqlCursorChannel.execute('CREATE TABLE IF NOT EXISTS offenses'
                                      '(userid INTEGER, username TEXT, offenses INTEGER)')
        self.sqlConnectionChannel.commit()

        self.sqlCursorChannel.execute('SELECT filtertype FROM filters')
        self.sqlCursorOffload = self.sqlCursorChannel.fetchall()

        lstFiltertypes = ['link', 'spam', 'emote_spam', 'banphrases']

        # if len(lstFiltertypes) > len(self.sqlCursorOffload):
        #     for filtertype in lstFiltertypes:
        #         for x in range(len(self.sqlCursorOffload)):
        #             if filtertype not in self.sqlCursorOffload[x][0]:
        #                 logging.warning("%s not found in sql database" % filtertype)
        #                 self.sqlCursorChannel.execute('INSERT INTO filters (filtertype, enabled) VALUES (?, ?)',
        #                                               (filtertype, "false"))
        #                 self.sqlConnectionChannel.commit()
        #                 break

        # try:
        self.sqlCursorChannel.execute('SELECT maxuserlevel, first_timeout, second_timeout, third_timeout, '
                                      'ban_after_third, message FROM filters')
        self.sqlCursorOffload = self.sqlCursorChannel.fetchall()
        iter_row = -1

        dictColumns = {0: "maxuserlevel", 1: "first_timeout",
                       2: "second_timeout", 3: "third_timeout",
                       4: "ban_after_third", 5: "message"}

        dictDefaults = {"maxuserlevel": 150, "first_timeout": 10,
                        "second_timeout": 600, "third_timeout": 600,
                        "ban_after_third": "false", "message": "None"}

        if None in self.sqlCursorOffload or '' in self.sqlCursorOffload:
            for row in self.sqlCursorOffload[0:]:
                iter_row += 1
                iter_column = -1
                for column in self.sqlCursorOffload[iter_row]:
                    iter_column += 1
                    if column is None:
                        self.sqlCursorChannel.execute('UPDATE filters SET {} = ?'.format(dictColumns[iter_column]),
                                                      (dictDefaults[dictColumns[iter_column]],))
                        self.sqlConnectionChannel.commit()
                        # except Exception as err:
                        #     logging.error(err)

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

        enabled = False
        ban_after_third = False
        if self.sqlCursorOffload[1] == 'true':
            enabled = True
        elif self.sqlCursorOffload[1] == 'false':
            enabled = False

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
