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

from .constants import ConfigDefaults
import default_commands
from default_commands._exceptions import *


class config:
    def __init__(self, bot, irc, sqlconn, info, userlevel=0, whisper=False):
        self.local_dispatch_map = {"set": self.defaultedit, "reset": self.defaultreset}
        self.bot = bot
        self.irc = irc
        self.sqlConnectionChannel, self.sqlCursorChannel = sqlconn
        self.info = info
        self.message = info["privmsg"]
        self.userlevel = userlevel
        self.whisper = whisper
        self.sqlVariableString = "SELECT value FROM config WHERE grouping=? AND variable=?"

        self.configdefaults = ConfigDefaults(sqlconn)

        self.min_userlevel_edit = int(self.configdefaults.sqlExecute(
            self.sqlVariableString, ("config", "min_userlevel_edit")).fetchone()[0])

        self.sqlCursorChannel.execute("SELECT grouping FROM config")

    def chat_access(self):
        temp_sqloffload = self.sqlCursorChannel.fetchall()
        try:
            temp_split = self.message.split(' ')
            if len(temp_split) > 1:
                if self.userlevel >= self.min_userlevel_edit:
                    if temp_split[1] in list(self.local_dispatch_map.keys()):
                        self.local_dispatch_map[temp_split[1]]()
                    elif (temp_split[1],) in list(temp_sqloffload):
                        self.defaultdisplay()
                    else:
                        self.irc.send_privmsg("Error: '%s' is not a valid command variation." % temp_split[1])
                        return
                else:
                    self.irc.send_privmsg('Error: You are not allowed to use any variations of {command}.'
                                          .format(command=default_commands.dispatch_naming['commands']))
                    return
            else:
                raise DCIncorrectAmountArgsError

        except DCIncorrectAmountArgsError:
            self.irc.send_privmsg("Error: Incorrect amount of arguments given.")
            return

    def testfor(self, args, value):
        try:
            datatypes = {
                "boolean": ("True", "False", "true", "false", "0", "1"),
                "integer": (int, str.isdigit),
                "string": (str,),
            }

            args = args.split(",")
            value = str(value)
            if args[0] in list(datatypes.keys()):
                try:
                    if args[0] == "string":
                        return True, args
                    elif args[0] == "integer" and (datatypes[args[0]][0](value) or
                                                   datatypes[args[0]][1](value)):
                        return True, args
                    elif args[0] == "boolean" and value in datatypes[args[0]]:
                        return True, args
                    else:
                        raise TypeError("Datatype test failed.")

                except TypeError as te:
                    logging.error("TypeError: %s" % str(te))
                    return False, args, TypeError

            else:
                logging.error("Error: Specified datatype not found.")
                return False, args, Exception

        except Exception as e:
            self.irc.send_whisper("Testfor error: %s" % str(e), self.info["username"])

    def defaultdisplay(self):
        parameters = self.message.split(" ", 1)
        split_params = parameters[1].strip().split(" ")
        try:
            if len(split_params) < 1:
                raise DCIncorrectAmountArgsError

            parameters = parameters[1].strip()

            self.sqlCursorChannel.execute("SELECT * FROM config WHERE grouping = ?",
                                          (split_params[0],))

            checkforGrouping = self.sqlCursorChannel.fetchone()

            self.sqlCursorChannel.execute("SELECT * FROM config "
                                          "WHERE grouping = ?",
                                          (split_params[0],))

            if len(split_params) >= 2:
                self.sqlCursorChannel.execute("SELECT * FROM config "
                                              "WHERE grouping = ? AND variable = ?",
                                              (split_params[0], split_params[1]))

            sqlCursorOffload = self.sqlCursorChannel.fetchall()

            if not checkforGrouping or not sqlCursorOffload:
                raise DCDatabaseEntryDoesNotExist

        except DCUserlevelIncorrectError:
            self.irc.send_privmsg("Error: You do not have permissions to configure settings.")
            return

        except DCDatabaseEntryDoesNotExist:
            self.irc.send_privmsg("Error: Variable '%s' doesn't exist under '%s'" % (split_params[1], split_params[0]))
            return

        except DCIncorrectDataType:
            return

        except DCIncorrectAmountArgsError:
            self.irc.send_privmsg("Error: Incorrect amount of arguments given.")
            return

        except Exception as e:
            self.irc.send_whisper("%s Display Config Error: %s" % (self.irc.CHANNEL, str(e)), "floppydisk_")
            return

        else:
            if len(split_params) >= 2:
                self.irc.send_privmsg("Option '%s' under '%s' is set to '%s'" %
                                      (split_params[1], split_params[0], sqlCursorOffload[0][2]))
            else:
                allvariables = []
                [allvariables.append(entry[1]) for entry in sqlCursorOffload]
                self.irc.send_privmsg("Variables under '%s': %s" %
                                      (split_params[0], ", ".join(sorted(allvariables))))

    def defaultedit(self):
        parameters = self.message.split("set", 1)
        split_params = parameters[1].strip().split(" ")
        try:
            if len(split_params) < 3:
                raise DCIncorrectAmountArgsError

            parameters = parameters[1].strip()

            self.sqlCursorChannel.execute("SELECT * FROM config WHERE grouping = ?",
                                          (split_params[0],))

            checkforGrouping = self.sqlCursorChannel.fetchone()

            self.sqlCursorChannel.execute("SELECT value, args, userlevel FROM config "
                                          "WHERE grouping = ? AND variable = ?",
                                          (split_params[0], split_params[1]))

            sqlCursorOffload = self.sqlCursorChannel.fetchone()

            if not checkforGrouping or not sqlCursorOffload:
                raise DCDatabaseEntryDoesNotExist

            if self.userlevel < sqlCursorOffload[2]:
                self.irc.send_privmsg("You do not have permissions to configure '%s' under '%s'." %
                                      (split_params[1], split_params[0]))
                return

            return_tuple = self.testfor(sqlCursorOffload[1], " ".join(split_params[2:]))

            if return_tuple[0] and return_tuple[1][0] == "integer":
                args = return_tuple[1]
                if len(args[1]) > 1:
                    split_arg = args[1].split("-")
                    if not int(split_arg[0]) >= int(split_params[2]) >= int(split_arg[1]):
                        self.irc.send_privmsg("Error: Integer out of bounds, %s (inclusive)" %
                                              args[1])
                        raise DCIntegerOutOfBounds

            if not return_tuple[0]:
                if return_tuple[2] == TypeError:
                    self.irc.send_privmsg("Error: Incorrect datatype as value. '%s' is not a(n) '%s'"
                                          % (split_params[2], sqlCursorOffload[1].split(",")[0]))
                    raise DCIncorrectDataType
                else:
                    raise return_tuple[2]

        except DCUserlevelIncorrectError:
            self.irc.send_privmsg("Error: You do not have permissions to configure settings.")
            return

        except DCDatabaseEntryDoesNotExist:
            self.irc.send_privmsg("Error: Variable '%s' doesn't exist under '%s'" % (split_params[1], split_params[0]))
            return

        except DCIncorrectDataType:
            return

        except DCIntegerOutOfBounds:
            return

        except DCIncorrectAmountArgsError:
            self.irc.send_privmsg("Error: Incorrect amount of arguments given.")
            return

        except TypeError:
            return

        except Exception as e:
            self.irc.send_whisper("%s Set Config Error: %s" % (self.irc.CHANNEL, str(e)))
            return

        else:
            self.sqlCursorChannel.execute("UPDATE config SET value = ?"
                                          " WHERE grouping = ? AND variable = ?",
                                          (" ".join(split_params[2:]), split_params[0], split_params[1]))

            self.sqlConnectionChannel.commit()

            self.irc.send_privmsg("Option '%s' under '%s' set to '%s'" % (split_params[1], split_params[0],
                                                                          " ".join(split_params[2:])))
            return

    def defaultreset(self):
        parameters = self.message.split("reset", 1)
        split_params = parameters[1].strip().split(" ")
        try:
            if len(parameters[1]) <= 1:
                raise DCIncorrectAmountArgsError

            parameters = parameters[1].strip()

            self.sqlCursorChannel.execute("SELECT * FROM config WHERE grouping = ?",
                                          (split_params[0],))

            checkforGrouping = self.sqlCursorChannel.fetchone()

            self.sqlCursorChannel.execute("SELECT value, args, userlevel FROM config "
                                          "WHERE grouping = ? AND variable = ?",
                                          (split_params[0], split_params[1]))

            sqlCursorOffload = self.sqlCursorChannel.fetchone()

            if not checkforGrouping or not sqlCursorOffload:
                raise DCDatabaseEntryDoesNotExist

        except DCDatabaseEntryDoesNotExist:
            self.irc.send_privmsg("Error: Variable '%s' doesn't exist under '%s'" % (split_params[1], split_params[0]))
            return

        except DCIncorrectAmountArgsError:
            self.irc.send_privmsg("Error: Incorrect amount of arguments given.")
            return

        except Exception as e:
            self.irc.send_whisper("%s Set Config Error: %s" % (self.irc.CHANNEL, str(e)), "floppydisk_")
            return

        else:
            self.configdefaults.defaults[split_params[0]](3, split_params[1])
            self.irc.send_privmsg("Option '%s' under '%s' reset to default." % (split_params[1], split_params[0]))
            return
