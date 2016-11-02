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

from constants import ConfigDefaults
import default_commands
from default_commands._exceptions import *


class birthdays:
    def __init__(self, irc, sqlconn, info, userlevel=0, whisper=False):
        self.local_dispatch_map = {'': self.addtodb}

        self.irc = irc
        self.sqlConnectionChannel, self.sqlCursorChannel = sqlconn
        self.info = info
        self.userlevel = userlevel
        self.whisper = whisper
        self.message = info["privmsg"]

        self.configdefaults = ConfigDefaults(sqlconn)

        self.enabled = bool(self.configdefaults.sqlSelectValueString("birthdays", "enabled").fetchone()[0])

        temp_split = self.message.split(" ")
        if self.enabled:
            if len(temp_split) > 1:
                if self.info["userlevel"] >= 150:
                    if temp_split[1]:
                        self.local_dispatch_map['']()
                    else:
                        raise DCBirthdaysFormatError
                else:
                    raise DCUserlevelIncorrectError

            else:
                self.irc.send_whisper("Error: Usage '{help}'".format(
                    help=default_commands.help_defaults[default_commands.dispatch_naming['birthdays']]['']
                        .format(command=default_commands.dispatch_naming['birthdays'])
                ), self.info["username"])
                return

    def addtodb(self):
        try:
            self.sqlCursorChannel.execute("SELECT userid, date FROM birthdays WHERE userid == ?",
                                          (self.info["user-id"],))
            sqlCursorOffload = self.sqlCursorChannel.fetchone()
            try:
                parameters = self.message.split(" ")
                birthdate = parameters[1]
                regexmatch = r'(?:^\d{2}\/\d{2}\/\d{4}|^\d{2}\/\d{2}$)'

                if len(parameters) > 2:
                    raise IndexError

                if re.search(regexmatch, birthdate, flags=re.MULTILINE) is not None:
                    if sqlCursorOffload is None:
                        self.irc.send_whisper("Added birthdate '%s' successfully." % birthdate, self.info["username"])

                        self.sqlCursorChannel.execute("INSERT INTO birthdays (userid, username, displayname, date) "
                                                      "VALUES (?, ?, ?, ?)",
                                                      (self.info["user-id"], self.info["username"],
                                                       self.info["display-name"], birthdate))

                        self.sqlConnectionChannel.commit()

                    else:
                        raise DCDatabaseEntryExists
                else:
                    raise DCBirthdaysFormatError

            except DCBirthdaysFormatError:
                self.irc.send_whisper("Error: You must provide your birthdate in this format 'DD/MM/YYYY'"
                                      " (Providing the year is optional).",
                                      self.info["username"])
                return

            except DCDatabaseEntryExists:
                self.irc.send_whisper('Error: Your birthdate already exists in the database: \'%s\''
                                      ' If the existing birthdate is incorrect, please whisper TheKillar25.'
                                      % sqlCursorOffload[1],
                                      self.info["username"])
                return

            except DCUserlevelIncorrectError:
                self.irc.send_whisper('Error: You are not allowed to use {command}.'
                                      .format(command=default_commands.dispatch_naming['commands']),
                                      self.info["username"])

                return

            except IndexError:
                self.irc.send_whisper("Error: Usage '{help}'".format(
                    help=default_commands.help_defaults[default_commands.dispatch_naming['birthdays']]['']
                        .format(command=default_commands.dispatch_naming['birthdays'])
                ), self.info["username"])
                return

            except Exception as e:
                self.irc.send_whisper("Error: Unexpected error occurred.",
                                      self.info["username"])

                self.irc.send_whisper("%s Add Birthday Error: %s" % (self.irc.CHANNEL, str(e)), "thekillar25")
                return

        except Exception as e:
            self.irc.send_whisper("Error: Unexpected error occurred.",
                                  self.info["username"])

            self.irc.send_whisper("%s Add Birthday Error: %s" % (self.irc.CHANNEL, str(e)), "thekillar25")
            return


def getbirthdayusers(sqlconn, configdefaults, currentdatetimelist):
    if int(configdefaults.sqlSelectValueString("birthdays", "enabled").fetchone()[0]):
        sqlConnectionChannel, sqlCursorChannel = sqlconn
        birthdayusers = {}
        sqlCursorChannel.execute("SELECT * FROM birthdays WHERE date LIKE ?",
                                 ('{}%'.format("%s/%s" % (currentdatetimelist[2],
                                                          currentdatetimelist[1])),))
        sqlCursorOffload = sqlCursorChannel.fetchall()

        if sqlCursorOffload:
            for entry in sqlCursorOffload:
                username = entry[1]
                displayname = entry[2]
                temp_age = ""
                temp_split_date = entry[3].split("/")
                if len(temp_split_date) == 3:
                    def ordinal(n):
                        return "%d%s" % (n, "tsnrhtdd"[(n // 10 % 10 != 1) *
                                                       (n % 10 < 4) * n % 10::4])

                    temp_birthyear = int(temp_split_date[2])
                    temp_age = (currentdatetimelist[0] - temp_birthyear)
                    temp_age = ordinal(temp_age)

                birthdayusers[username] = (displayname, temp_age)

        else:
            pass

        logging.info("[_BOTCOM] :| [CVAR] Birthday users: %s" % list(birthdayusers.keys()))

        return birthdayusers

    return {}


def joinevent(irc, configdefaults, birthdayusers, username):
    if username in list(birthdayusers.keys()) and \
            bool(configdefaults.sqlSelectValueString("birthdays", "enabled").fetchone()[0]):
        irc.send_privmsg("Birthday Boy/Girl %s has joined the chat!"
                         " Wish them a happy %s birthday!"
                         % (birthdayusers[username][0],
                            birthdayusers[username][1]),
                         True)
