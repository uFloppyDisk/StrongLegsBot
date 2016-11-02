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

import default_commands
from default_commands._exceptions import *


class config:
    def __init__(self, irc, sqlconn, info, userlevel=0, whisper=False):
        self.local_dispatch_map = {"edit": self.defaultedit}
        self.irc = irc
        self.sqlConnectionChannel, self.sqlCursorChannel = sqlconn
        self.info = info
        self.message = info["privmsg"]
        self.userlevel = userlevel
        self.whisper = whisper

        try:
            temp_split = self.message.split(' ')
            if len(temp_split) > 1:
                if userlevel >= 250:
                    if temp_split[1] in list(self.local_dispatch_map.keys()):
                        self.local_dispatch_map[temp_split[1]]()
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
                "integer": str.isdigit,
                "string": (str,),
            }

            args = args.split(",")
            if args[0] in list(datatypes.keys()):
                try:
                    if args[0] == "string":
                        return True, args
                    elif args[0] == "integer" and datatypes[args[0]](value):
                        return True, args
                    elif args[0] == "boolean" and value in datatypes[args[0]]:
                        return True, args
                    else:
                        raise TypeError

                except TypeError:
                    logging.info("TypeError")
                    return False, args

            else:
                logging.info("Other")
                return False, args

        except Exception as e:
            self.irc.send_whisper("Testfor error: %s" % str(e), self.info["username"])

    def defaultedit(self):
        parameters = self.message.split("edit", 1)
        split_params = parameters[1].strip().split(" ")
        try:
            if len(parameters[1]) <= 2:
                raise DCIncorrectAmountArgsError

            parameters = parameters[1].strip()

            self.sqlCursorChannel.execute("SELECT * FROM config WHERE grouping = ?",
                                          (split_params[0],))

            checkforGrouping = self.sqlCursorChannel.fetchone()

            self.sqlCursorChannel.execute("SELECT value, args, userlevel FROM config "
                                          "WHERE grouping = ? AND variable = ?",
                                          (split_params[0], split_params[1]))

            sqlCursorOffload = self.sqlCursorChannel.fetchone()

            if not (sqlCursorOffload, checkforGrouping):
                raise DCDatabaseEntryDoesNotExist

            if len(split_params) == 2:
                self.irc.send_privmsg("Error: Not implemented.")
                return

            elif len(split_params) >= 3:
                if self.userlevel < sqlCursorOffload[2]:
                    self.irc.send_privmsg("You do not have permissions to configure '%s' under '%s'." %
                                          (split_params[1], split_params[0]))
                    return

                if not self.testfor(sqlCursorOffload[1], " ".join(split_params[2:]))[0]:
                    self.irc.send_privmsg("Error: Incorrect datatype as value. '%s' is not a(n) '%s'"
                                          % (split_params[2], sqlCursorOffload[1]))
                    raise DCIncorrectDataType

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
            self.irc.send_privmsg(str(e))
            return

        else:
            self.sqlCursorChannel.execute("UPDATE config SET value = ?"
                                          " WHERE grouping = ? AND variable = ?",
                                          (" ".join(split_params[2:]), split_params[0], split_params[1]))

            self.sqlConnectionChannel.commit()

            self.irc.send_privmsg("Option '%s' set to '%s'" % (split_params[1], " ".join(split_params[2:])))
            return
