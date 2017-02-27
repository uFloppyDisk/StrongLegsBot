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

from .constants import ConfigDefaults, boolean
import default_commands


class regulars:
    def __init__(self, bot, irc, sqlconn, info, userlevel=0, whisper=False):
        self.local_dispatch_map = {'add': self.add, 'delete': self.delete, 'help': '',
                                   '': ''}
        self.bot = bot
        self.irc = irc
        self.sqlConnectionChannel, self.sqlCursorChannel = sqlconn
        self.info = info
        self.message = info["privmsg"]
        self.userlevel = userlevel
        self.whisper = whisper
        self.sqlVariableString = "SELECT value FROM config WHERE grouping=? AND variable=?"

        self.configdefaults = ConfigDefaults(sqlconn)

        self.enabled = boolean(self.configdefaults.sqlExecute(
            self.sqlVariableString, ("regulars", "enabled")).fetchone()[0])

        self.commandkeyword = self.configdefaults.sqlExecute(
            self.sqlVariableString, ("regulars", "keyword")).fetchone()[0]
        default_commands.dispatch_naming["regulars"] = self.commandkeyword

        if not self.enabled:
            return

        self.min_userlevel = int(self.configdefaults.sqlExecute(
            self.sqlVariableString, ("regulars", "min_userlevel")).fetchone()[0])
        self.min_userlevel_edit = int(self.configdefaults.sqlExecute(
            self.sqlVariableString, ("regulars", "min_userlevel_edit")).fetchone()[0])

    def chat_access(self):
        temp_split = self.message.split(' ')
        if len(temp_split) > 1:
            if self.userlevel >= self.min_userlevel_edit:
                if temp_split[1] in list(self.local_dispatch_map.keys()):
                    self.local_dispatch_map[temp_split[1]]()
                else:
                    self.irc.send_privmsg("Error: '%s' is not a valid command variation." % temp_split[1])
                    return
            else:
                self.irc.send_privmsg('Error: You are not allowed to use any variations of {command}.'
                                      .format(command=default_commands.dispatch_naming['regulars']))
                return

    def add(self):
        parameters = self.message.split("add", 1)
        if len(parameters[1]) <= 0:
            logging.warning("No arguments found")
            self.irc.send_privmsg("Error: Incorrect amount of arguments given.")
            return

        parameters = parameters[1].strip()
        split_params = parameters.split(" ")
        command_reg_to_add = split_params[0].lower()

        self.sqlCursorChannel.execute('SELECT * FROM regulars WHERE username = ?', (command_reg_to_add,))
        sqlCursorOffLoad = self.sqlCursorChannel.fetchone()
        if sqlCursorOffLoad is not None:
            self.irc.send_privmsg('Error: User already in regulars list.', True)
            return

        self.sqlCursorChannel.execute('SELECT userid FROM userlevel WHERE username = ?', (command_reg_to_add,))
        sqlCursorOffLoad = self.sqlCursorChannel.fetchone()
        if sqlCursorOffLoad is None:
            self.irc.send_privmsg('Error: User is not present in database. (must send message once in the chat)', True)
            return

        self.sqlCursorChannel.execute('INSERT INTO regulars (userid, username) VALUES (?, ?)',
                                      (sqlCursorOffLoad[0], command_reg_to_add))

        self.sqlConnectionChannel.commit()

        self.irc.send_privmsg('Added username to regulars list.', True)
        return

    def delete(self):
        parameters = self.message.split("delete", 1)
        if len(parameters[1]) <= 0:
            logging.warning("No arguments found")
            self.irc.send_privmsg("Error: Incorrect amount of arguments given.")
            return

        parameters = parameters[1].strip()
        split_params = parameters.split(" ")
        command_reg_to_del = split_params[0].lower()

        self.sqlCursorChannel.execute('SELECT * FROM regulars WHERE username = ?', (command_reg_to_del,))
        sqlCursorOffLoad = self.sqlCursorChannel.fetchone()
        if sqlCursorOffLoad is None:
            self.irc.send_privmsg("Error: User doesn't exist in regular list.", True)
            return

        self.sqlCursorChannel.execute('DELETE FROM regulars WHERE username = ?',
                                      (command_reg_to_del, ))

        self.sqlConnectionChannel.commit()

        self.irc.send_privmsg('Deleted username from regulars list.', True)
        return

