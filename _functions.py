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
import subprocess
import sys
import time

import StrongLegsBot
import unpackconfig

bot = StrongLegsBot.Bot()
cfg = unpackconfig.configUnpacker()


class Diagnostic:
    def __init__(self, irc, sqlconn):
        self.mainbotfile = "StrongLegsBot.py"
        self.osplatform = sys.platform
        self.irc = irc
        self.sqlConnectionChannel, self.sqlCursorChannel = sqlconn

    # Restarts instance as sockets cannot be reopened
    def bot_restart(self, possible_exit, logging_level):
        time.sleep(1)
        try:
            # Handles system dependent subprocess calls
            opener = "open" if self.osplatform == "darwin" else "python"
            subprocess.call([opener, self.mainbotfile, StrongLegsBot.IRC().CHANNEL, logging_level])

            # Closes SQLite connections if restart failed
            self.sqlCursorChannel.close()
            self.sqlConnectionChannel.close()

            raise SystemExit

        except not SystemExit:
            StrongLegsBot.Bot.mainloopbreak = True


class Parse:
    def __init__(self, irc, sqlconn, data):
        self.config = cfg.unpackcfg()
        self.irc = irc
        self.sqlConnectionChannel, self.sqlCursorChannel = sqlconn

        self.data_to_parse = data
        self.parsetype = None

        self.regex_server = self.config['regex_server']
        self.regex_whisper = self.config['regex_whisper']
        self.regex_privmsg = self.config['regex_privmsg']
        self.regex_newsubscriber = self.config['regex_server_newsubscriber']

        self.dictRegex = {"privmsg": self.regex_privmsg, "whisper": self.regex_whisper,
                          "server": self.regex_server, "new_subscriber": self.regex_newsubscriber}

        self.dictMatchedRegex = {}

        if re.search(self.dictRegex["privmsg"], self.data_to_parse) is not None:
            self.parsetype = "privmsg"

        elif re.search(self.dictRegex["whisper"], self.data_to_parse) is not None and self.parsetype is None:
            self.parsetype = "whisper"

        elif re.search(self.dictRegex["server"], self.data_to_parse) is not None and self.parsetype is None:
            self.parsetype = "server"

        elif re.search(self.dictRegex["new_subscriber"], self.data_to_parse) is not None and self.parsetype is None:
            self.parsetype = "new_subscriber"

        else:
            self.parsetype = None

    def parse(self):
        try:
            if self.parsetype == 'server':
                #############################
                #    SERVER PARSE GUIDE
                # Group:    Value:
                #
                #      1   Twitch Data Identifier (string)
                #
                #  NOTE: Server parse regex normally used to capture twitch data identifier
                #  in order to pass through a decision structure and parse each data type
                #  as specified by identifier.
                #  ex. if identifer == "USERSTATE":
                #          parsed = re.search(server_userstate)	//see below for corrosponding regex
                #
                #############################
                dictIdentifer = {"CAP * ACK": "CACK", "CLEARCHAT": "CLCH",
                                 "GLOBALUSERSTATE": "GLUS", "HOSTTARGET": "HOST",
                                 "NOTICE": "NOTE", "RECONNECT": "RECN",
                                 "ROOMSTATE": "RMST", "USERNOTICE": "USNT",
                                 "USERSTATE": "URST"}

                dontDisplay = [dictIdentifer["CAP * ACK"],
                               dictIdentifer["GLOBALUSERSTATE"],
                               "PING"]

                identifier = re.search(self.config["regex_server"], self.data_to_parse)
                info, parsed = self.parse_server(identifier.group(1), dictIdentifer, self.data_to_parse)
                display = False if "channel" not in info or identifier.group(1) in dontDisplay else True

                return "_server", identifier.group(1), info, display, parsed

            elif self.parsetype == 'whisper':
                #############################
                #    WHISPER PARSE GUIDE
                # Group:    Value:
                #
                #      1    Badges (string)
                #      2    Color (#<hex>)
                #      3    Display-name (string)
                #      4    Emotes (####:###-###, ###-###)
                #      5    Message-ID (integer)
                #      6    Thread-ID ([userid of sender]_[userid of receiver])
                #      7    Turbo (0 or 1)
                #      8    User-ID (integer)
                #      9    User-Type (string)
                #     10    Username (string)
                #     11    Receiver (string)
                #     12    Message (string)
                #
                #############################
                servermsg = re.search(self.config["regex_whisper"], self.data_to_parse)
                servermsg = {"badges": servermsg.group(1), "color": servermsg.group(2),
                             "display-name": servermsg.group(3), "emotes": servermsg.group(4),
                             "id": servermsg.group(5), "threadid": servermsg.group(6),
                             "turbo": servermsg.group(7), "user-id": servermsg.group(8),
                             "user-type": servermsg.group(9), "username": servermsg.group(10),
                             "receiver": servermsg.group(11), "privmsg": servermsg.group(12)}

                return self.parsetype, self.parsetype, servermsg, False,  "[RECV] %s_%s: %s" % (servermsg["id"],
                                                                                                servermsg["username"],
                                                                                                servermsg["privmsg"])

            elif self.parsetype == 'privmsg':
                #############################
                #    PRIVMSG PARSE GUIDE
                # Group:    Value:
                #
                #      1    Badges (string)
                #      2    Color (#<hex>)
                #      3    Display-Name (string)
                #      4    Emotes (####:###-###, ###-###)
                #      5    ID (Alpha-numerical)
                #      6    Mod (0 or 1)
                #      7    Room-ID (numerical)
                #      8    Subscriber (0 or 1)
                #      9    Turbo (0 or 1)
                #     10    User-ID (integer)
                #     11    User-Type (string)
                #     12    Username (string)
                #     13    Channel (#string)
                #     14    Privmsg (string)
                #
                # New:
                #
                #      1    Parameters snippet (string)
                #      2    Username (string)
                #      3    Channel (#string)
                #      4    Privmsg (string)
                #
                #############################

                servermsg = {}
                servermsg_split = self.data_to_parse.strip('@').split(" :", 2)

                parameters = servermsg_split[0].split(';')

                for parameter in parameters:
                    parameter_split = parameter.split('=')
                    servermsg[parameter_split[0]] = parameter_split[1]

                ircinfo = servermsg_split[1].split(" %s " % self.parsetype.upper())
                # username = ircinfo[0].split('!')[0]
                servermsg["username"] = ircinfo[0].split('!')[0]
                servermsg["channel"] = ircinfo[1]
                servermsg["privmsg"] = servermsg_split[2].strip('\r')

                self.sqlCursorChannel.execute('SELECT userlevel FROM userLevel WHERE userid == ?',
                                              (servermsg["user-id"],))
                sqlCursorOffload = self.sqlCursorChannel.fetchone()
                if sqlCursorOffload is None:
                    sqlCursorOffload = ("---",)

                parsed = "[RECV] %s: {%s} [%s]: %s" % (servermsg["channel"], sqlCursorOffload[0],
                                                       servermsg["username"], servermsg["privmsg"])
                return self.parsetype, self.parsetype, servermsg, True, parsed

            elif self.parsetype == "new_subscriber":
                servermsg = re.search(self.config["regex_server_newsubscriber"], self.data_to_parse)
                servermsg = {"username": servermsg.group(1), "channel": servermsg.group(2),
                             "message": servermsg.group(3)}
                return "_server", "nsub", servermsg, True, "[NSUB] %s [%s]: %s" % (servermsg["channel"],
                                                                                   servermsg["username"],
                                                                                   servermsg["message"])

            else:
                info = None
                return "UNKNOWN", self.parsetype, info, "%s" % self.data_to_parse

        except IndexError as e:
            logging.error(e)

    def parse_server(self, identifier, dictIdentifer, data):
        try:

            if identifier == "CAP * ACK":
                servermsg = data.split(" :")
                return servermsg, "[%s] %s" % (dictIdentifer[identifier], servermsg[1])

            elif identifier == "CLEARCHAT":
                #############################
                #    CLEARCHAT TIMEOUT/BAN PARSE GUIDE
                # Group:    Value:
                # Timeout:
                #      2    Duration (integer)
                #      3    Reason (string)
                #      4    Channel (#string)
                #      5    Target_username (string)
                #
                # Ban:
                #      1    Reason (string)
                #      4    Channel (#string)
                #      5    Target_username (string)
                #
                #############################

                servermsg = data.split(identifier + " ")
                clearchat_chatter = re.search(self.config["regex_server_clearchat_chatter"], data)

                if clearchat_chatter is not None:
                    if clearchat_chatter.group(2) is not None:
                        servermsg = {"duration": clearchat_chatter.group(2),
                                     "reason": clearchat_chatter.group(3).replace("\s", " ")
                                     if clearchat_chatter.group(3) != " " else "~None~",
                                     "channel": clearchat_chatter.group(4),
                                     "target_username": clearchat_chatter.group(5)}

                        return servermsg, "[%s] %s: TIMEOUT:%s TTL:%s Reason:%s" % (dictIdentifer[identifier],
                                                                                    servermsg["channel"],
                                                                                    servermsg["target_username"],
                                                                                    servermsg["duration"],
                                                                                    servermsg["reason"])

                    if clearchat_chatter.group(2) is None:
                        servermsg = {"reason": clearchat_chatter.group(1).replace("\s", " ")
                                     if clearchat_chatter.group(1) != " " else "~None~",
                                     "channel": clearchat_chatter.group(4),
                                     "target_username": clearchat_chatter.group(5)}

                        return servermsg, "[%s] %s: BAN:%s Reason:%s" % (dictIdentifer[identifier],
                                                                         servermsg["channel"],
                                                                         servermsg["target_username"],
                                                                         servermsg["reason"])

                return servermsg, "[%s] %s" % (dictIdentifer[identifier], servermsg[1])

            elif identifier == "GLOBALUSERSTATE":
                #############################
                #    GLOBALUSERSTATE PARSE GUIDE
                # Group:    Value:
                #      1    Badges (string)
                #      2    Color (#<hex>)
                #      3    Display-name (string)
                #      4    Emote-sets (####:###-###, ###-###)
                #      5    Turbo (0 or 1)
                #      6    User-id (numerical)
                #      7    User-type (string)
                #
                #############################

                servermsg = {}
                servermsg_split = self.data_to_parse.strip('@').split(" :", 1)

                parameters = servermsg_split[0].split(';')

                for parameter in parameters:
                    parameter_split = parameter.split('=')
                    servermsg[parameter_split[0]] = parameter_split[1]

                ircinfo = servermsg_split[1].split(" ")
                servermsg["host"] = ircinfo[0]
                servermsg["identifier"] = ircinfo[1].strip("\r")

                return servermsg, "[%s] [%s]" % (dictIdentifer[identifier], parameters)

            elif identifier == "HOSTTARGET":
                #############################
                #    HOSTTARGET PARSE GUIDE
                # Group:    Value:
                #      1    Hoster channel (#string)
                #      2    Hostee channel (#string or '-')
                #      3    Viewer count (integer)
                #
                #############################
                servermsg = re.search(self.config["regex_server_hosttarget"], data)
                servermsg = {"hoster": servermsg.group(1), "hostee": servermsg.group(2),
                             "viewers": servermsg.group(3)}
                return servermsg, "[%s] %s: %s hosted with %s" % (dictIdentifer[identifier],
                                                                  servermsg["hoster"],
                                                                  servermsg["hostee"],
                                                                  servermsg["viewers"])

            elif identifier == "JOIN":
                #############################
                #    JOIN PARSE GUIDE
                # Group:    Value:
                #      1    Username (string)
                #      2    Channel (#string)
                #
                #############################

                servermsg = {}
                ircinfo = data.split(" %s " % identifier.upper())
                servermsg["username"] = ircinfo[0].split('!')[0].strip(':')
                servermsg["channel"] = ircinfo[1].strip("\r\n")
                return servermsg, "[%s] %s: %s" % (identifier, servermsg["channel"], servermsg["username"])

            elif identifier == "MODE":
                #############################
                #    MODE PARSE GUIDE
                # Group:    Value:
                #      1    Channel (#string)
                #      2    +o or -o
                #      3    Username (string)
                #
                #############################

                servermsg = {}
                ircinfo = data.split(" ")
                servermsg["channel"] = ircinfo[2]
                servermsg["mode"] = ircinfo[3]
                servermsg["username"] = ircinfo[4]
                return servermsg, "[%s] %s: (%s) %s" % (identifier, servermsg["channel"],
                                                        servermsg["mode"], servermsg["username"])

            elif identifier == "NOTICE":
                #############################
                #    NOTICE PARSE GUIDE
                # Group:    Value:
                #      1    Msg-id (string)
                #      2    Channel (#string)
                #      3    Message (string)
                #
                #############################

                servermsg = re.search(self.config["regex_server_notice"], data)
                servermsg = {"id": servermsg.group(1), "channel": servermsg.group(2),
                             "message": servermsg.group(3)}
                return servermsg, "[%s] %s: (%s) %s" % (dictIdentifer[identifier], servermsg["channel"],
                                                        servermsg["id"], servermsg["message"])

            elif identifier == "PART":
                #############################
                #    PART PARSE GUIDE
                # Group:    Value:
                #      1    Username (string)
                #      2    Channel (#string)
                #
                #############################

                servermsg = {}
                ircinfo = data.split(" %s " % identifier.upper())
                servermsg["username"] = ircinfo[0].split('!')[0].strip(':')
                servermsg["channel"] = ircinfo[1].strip("\r\n")
                return servermsg, "[%s] %s: %s" % (identifier, servermsg["channel"], servermsg["username"])

            elif identifier == "PING":
                servermsg = data.split(identifier)
                return servermsg, "[%s] Ping requested with data '%s'" % (identifier, servermsg[1].strip("\r"))

            elif identifier == "RECONNECT":
                return self.data_to_parse, "RECN" + self.data_to_parse

            elif identifier == "ROOMSTATE":
                #############################
                #    ROOMSTATE PARSE GUIDE
                # Group:    Value:
                # Declarative:
                #      1    Broadcaster-Language (2-char string ex. "en")
                #      2    Emote-only (0 or 1)
                #      3    r9kbeta (0 or 1)
                #      4    Slow-mode (integer)
                #      5    Subscriber-only (0 or 1)
                #      6    Channel (#string)
                #
                # Update:
                #      1    Update-type (string)
                #      2    Update-value (0 or 1)
                #      3    Channel (#string)
                #
                #############################

                servermsg = re.search(self.config["regex_server_roomstate"], data)
                if servermsg is not None:
                    servermsg = {"broadcastlang": servermsg.group(1), "emoteonly": servermsg.group(2),
                                 "r9kbeta": servermsg.group(3), "slowmode": servermsg.group(4),
                                 "subscriberonly": servermsg.group(5), "channel": servermsg.group(6)}

                    return servermsg, "[%s] %s: [broadcast-lang=%s][subscriber-only=%s]" \
                                      "[slow-mode=%ss][r9k=%s][emote-only=%s]" % (dictIdentifer[identifier],
                                                                                  servermsg["channel"],
                                                                                  servermsg["broadcastlang"],
                                                                                  servermsg["subscriberonly"],
                                                                                  servermsg["slowmode"],
                                                                                  servermsg["r9kbeta"],
                                                                                  servermsg["emoteonly"])
                else:
                    servermsg = re.search(self.config["regex_server_roomstate_update"], data)
                    servermsg = {"updatetype": servermsg.group(1), "updatevalue": servermsg.group(2),
                                 "channel": servermsg.group(3)}
                    return servermsg, "[%s] %s UPDATE: %s=%s" % (dictIdentifer[identifier],
                                                                 servermsg["channel"],
                                                                 servermsg["updatetype"],
                                                                 servermsg["updatevalue"])

            elif identifier == "USERNOTICE":
                #############################
                #    USERNOTICE PARSE GUIDE
                # Group:    Value:
                #
                #      1    Badges (string)
                #      2    Color (#<hex>)
                #      3    Display-Name (string)
                #      4    Emotes (####:###-###, ###-###)
                #      5    Login (string)
                #      6    Mod (0 or 1)
                #      7    Msg-ID (string)
                #      8    Msg-param-months (integer)
                #      9    Room-ID (integer)
                #     10    Subscriber (0 or 1)
                #     11    System-msg (string)
                #     12    Turbo (0 or 1)
                #     13    User-ID (integer)
                #     14    User-type (string)
                #     15    Channel (#string)
                # With user message:
                #     16    Message (string)
                #
                #############################
                try:
                    servermsg = re.search(self.config["regex_server_usernotice_usermsg"], data)

                    if servermsg is not None:
                        servermsg = {"badges": servermsg.group(1), "color": servermsg.group(2),
                                     "display-name": servermsg.group(3), "emotes": servermsg.group(4),
                                     "username": servermsg.group(5), "mod": servermsg.group(6),
                                     "msg-id": servermsg.group(7), "msg-param-months": servermsg.group(8),
                                     "room-id": servermsg.group(9), "subscriber": servermsg.group(10),
                                     "system-msg": servermsg.group(11), "turbo": servermsg.group(12),
                                     "user-id": servermsg.group(13), "user-type": servermsg.group(14),
                                     "channel": servermsg.group(15), "message": servermsg.group(16)}

                        return servermsg, "[%s] %s: (%s) Userid: %s Username: %s consMonth: %s sysMsg: %s : %s" % \
                            (dictIdentifer[identifier],
                             servermsg["channel"],
                             servermsg["msg-id"],
                             servermsg["user-id"],
                             servermsg["username"],
                             servermsg["msg-param-months"],
                             servermsg["system-msg"].replace("\s", " "),
                             servermsg["message"])
                    else:
                        servermsg = re.search(self.config["regex_server_usernotice_nousermsg"], data)
                        servermsg = {"badges": servermsg.group(1), "color": servermsg.group(2),
                                     "display-name": servermsg.group(3), "emotes": servermsg.group(4),
                                     "username": servermsg.group(5), "mod": servermsg.group(6),
                                     "msg-id": servermsg.group(7), "msg-param-months": servermsg.group(8),
                                     "room-id": servermsg.group(9), "subscriber": servermsg.group(10),
                                     "system-msg": servermsg.group(11), "turbo": servermsg.group(12),
                                     "user-id": servermsg.group(13), "user-type": servermsg.group(14),
                                     "channel": servermsg.group(15)}

                        return servermsg, "[%s] %s: (%s) Userid: %s Username: %s consMonth: %s sysMsg: %s" % \
                                          (dictIdentifer[identifier],
                                           servermsg["channel"],
                                           servermsg["msg-id"],
                                           servermsg["user-id"],
                                           servermsg["username"],
                                           servermsg["msg-param-months"],
                                           servermsg["system-msg"].replace("\s", " "))

                except Exception as e:
                    logging.error("Usernotice parse error: %s", e)

            elif identifier == "USERSTATE":
                #############################
                #    USERSTATE PARSE GUIDE
                # Group:    Value:
                #      1    Badges (string)
                #      2    Color (#<hex>)
                #      3    Display-name (string)
                #      4    Emote-sets (####:###-###, ###-###)
                #      5    Mod (0 or 1)
                #      6    Subscriber (0 or 1)
                #      7    Turbo (0 or 1)
                #      8    User-type (string)
                #      9    Channel (#string)
                #
                #############################

                servermsg = {}
                servermsg_split = self.data_to_parse.strip('@').split(" :", 1)

                parameters = servermsg_split[0].split(';')

                for parameter in parameters:
                    parameter_split = parameter.split('=')
                    servermsg[parameter_split[0]] = parameter_split[1]

                ircinfo = servermsg_split[1].split(" ")
                servermsg["host"] = ircinfo[0]
                servermsg["identifier"] = ircinfo[1]
                servermsg["channel"] = ircinfo[2].strip("\r")

                return servermsg, "[%s] %s: [%s]" % (dictIdentifer[identifier],
                                                     servermsg["channel"],
                                                     servermsg)

            else:
                servermsg = data.split(" :")
                if identifier.strip().isdigit():
                    formatted_identifier = '_' + identifier.strip()
                else:
                    logging.error("Unrecognized server message, parse failed.")
                    formatted_identifier = identifier.strip()

                return servermsg, "[%s] %s :%s" % (formatted_identifier, self.config["settings_username"], servermsg[1])

        except Exception as e:
            logging.error(e)


class Data:
    def __init__(self, irc, sqlconn):
        self.irc = irc
        self.channel = irc.CHANNEL

        self.sqlconn = sqlconn
        self.sqlConnectionChannel, self.sqlCursorChannel = self.sqlconn

        self.sqlCursorChannel.execute('CREATE TABLE IF NOT EXISTS userLevel(userid INTEGER, userlevel INTEGER, username TEXT)')
        self.sqlCursorChannel.execute('CREATE TABLE IF NOT EXISTS commands(userlevel INTEGER, keyword TEXT, output TEXT, args INTEGER, sendtype TEXT, syntaxerr TEXT)')
        self.sqlCursorChannel.execute('CREATE TABLE IF NOT EXISTS regulars(userid INTEGER, username TEXT)')
        self.sqlCursorChannel.execute('CREATE TABLE IF NOT EXISTS faq(userlevel INTEGER, name TEXT, regexp TEXT, output TEXT, sendtype TEXT)')
        self.sqlCursorChannel.execute('CREATE TABLE IF NOT EXISTS filters'
                                      '(filtertype TEXT, enabled TEXT, maxuserlevel INTEGER, first_timeout INTEGER, '
                                      'second_timeout INTEGER, third_timeout INTEGER, ban_after_third TEXT, message TEXT)')
        self.sqlCursorChannel.execute('CREATE TABLE IF NOT EXISTS offenses'
                                      '(userid INTEGER, username TEXT, offenses INTEGER)')

        self.sqlConnectionChannel.commit()

    def handleUserLevel(self, handleuserlevel, whisper=False):
        userid, username, usertype, subscriber, turbo = handleuserlevel
        try:
            self.sqlCursorChannel.execute('SELECT userid FROM regulars WHERE userid == ?', (userid,))

            isRegular = self.sqlCursorChannel.fetchone()
            userlevel = 0
            dictUserType = {'mod': 250, 'global_mod': 350,
                            'admin': 500, 'staff': 600}

            if not whisper:
                if username == 'thekillar25':
                    userlevel = 700

                elif usertype == '':
                    logging.debug('Checking non-special user')
                    if int(turbo) == 1:
                        userlevel = 50
                    if int(subscriber) == 1:
                        userlevel = 100
                    if isRegular is not None:
                        userlevel = 150
                    if username == self.channel.strip("#"):
                        userlevel = 400
                    logging.debug('Done checking non-special user')

                elif usertype in list(dictUserType.keys()):
                    logging.debug('Checking special user')
                    userlevel = dictUserType[usertype]
                    logging.debug('Done checking special user')

                else:
                    userlevel = -1

                self.sqlCursorChannel.execute('SELECT userlevel FROM userLevel WHERE userid == ?', (userid,))
                sqlCursorOffload = self.sqlCursorChannel.fetchone()

                if not sqlCursorOffload:
                    logging.debug("Adding user to userLevel for channel %s", self.channel)
                    self.sqlCursorChannel.execute('INSERT INTO userLevel (userid, userlevel, username) VALUES (?, ?, ?)',
                                                  (userid, userlevel, username))

                elif userlevel != sqlCursorOffload[0]:
                    logging.debug("Userlevel mismatch in %s", self.channel)
                    self.sqlCursorChannel.execute('UPDATE userLevel SET userlevel = ? WHERE userid == ?',
                                                  (userlevel, userid))

                else:
                    pass

                self.sqlConnectionChannel.commit()

            else:
                if username == 'thekillar25':
                    userlevel = 700

                elif usertype == '':
                    logging.debug('Checking non-special user')
                    if int(turbo) == 1:
                        userlevel = 50
                    logging.debug('Done checking non-special user')

                elif usertype in list(dictUserType.keys()):
                    logging.debug('Checking special user')
                    userlevel = dictUserType[usertype]
                    logging.debug('Done checking special user')

                else:
                    userlevel = -1

            return userlevel

        except Exception as e:
            logging.exception(e)
