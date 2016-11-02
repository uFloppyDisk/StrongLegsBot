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

import re

import default_commands
from default_commands._exceptions import *


class faq:
    def __init__(self, irc, sqlconn, info, userlevel=0, whisper=False):
        self.local_dispatch_map = {'add': self.add, 'edit': self.edit,
                                   'delete': self.delete, 'help': self.help,
                                   '': ''}
        self.irc = irc
        self.sqlConnectionChannel, self.sqlCursorChannel = sqlconn
        self.info = info
        self.message = info["privmsg"]
        self.userlevel = userlevel
        self.whisper = whisper

        temp_split = self.message.split(' ')
        if len(temp_split) > 1:
            if temp_split[1] == 'help':
                self.help()
            elif userlevel >= 400:
                if temp_split[1] in list(self.local_dispatch_map.keys()):
                    self.local_dispatch_map[temp_split[1]]()
                else:
                    self.irc.send_privmsg("Error: '%s' is not a valid command variation." % temp_split[1])
                    return
            else:
                self.irc.send_privmsg('Error: You are not allowed to use any variations of {command}.'
                                      .format(command=default_commands.dispatch_naming['faq']))
                return
        else:
            pass

    def help(self):
        pass

    def add(self):
        parameters = self.message.split("add", 1)
        if len(parameters[1]) <= 0:
            raise DCIncorrectAmountArgsError

        parameters = parameters[1].strip()
        split_params = parameters.split(" ")
        command_name = ''
        command_regex = ''
        command_offset = 0
        command_userlevel = 0
        command_sendmode = "privmsg"
        userlevel_specified = False
        sendmode_specified = False

        for split_pos in range(len(split_params)):
            if userlevel_specified and sendmode_specified:
                break

            if userlevel_specified:
                pass
            elif split_params[split_pos].startswith("-ul="):
                command_offset += 1
                temp_split_parms = split_params[split_pos].split("=", 1)
                if temp_split_parms[1] != '':
                    if 0 <= int(temp_split_parms[1]) <= 700:
                        command_userlevel = temp_split_parms[1]
                        userlevel_specified = True
                    else:
                        self.irc.send_privmsg("Error: Invalid userlevel, must be 0 <= userlevel <= 700.")
                        return
                else:
                    self.irc.send_privmsg("Error: Userlevel cannot be nil.")
                    return
            else:
                command_userlevel = 0

            if sendmode_specified:
                pass
            elif split_params[split_pos].startswith("-sm=") and self.userlevel >= 400:
                temp_split_parms = split_params[split_pos].split("=", 1)
                command_offset += 1
                if temp_split_parms[1] != '':
                    if temp_split_parms[1] in ("privmsg", "whisper"):
                        command_sendmode = temp_split_parms[1]
                        sendmode_specified = True
                    else:
                        self.irc.send_privmsg("Error: Invalid sendtype, must be 'privmsg' or 'whisper'.")
                        return
                else:
                    self.irc.send_privmsg("Error: Sendmode cannot be nil.")
                    return

            elif split_params[split_pos].startswith("-sm=") and self.userlevel < 400:
                self.irc.send_privmsg("Permissions Error: You don't have the permissions to specify faq sendmode.")

            else:
                command_sendmode = "privmsg"

        command_name = split_params[command_offset]

        self.sqlCursorChannel.execute('SELECT name FROM faq WHERE name == ?', (command_name,))
        sqlCursorOffload = self.sqlCursorChannel.fetchone()

        if sqlCursorOffload is not None:
            self.irc.send_privmsg("Error: Faq with name '%s' already exists." % command_name)
            return

        temp_parameters = ''
        if "\\'" in split_params[command_offset + 1]:
            regex_output = r"\\'(.*?)\'\\"
            regex_output = re.search(regex_output, parameters)
            if regex_output is not None:
                if regex_output.group(1) == "" or regex_output.group(1) == "\\''\\" \
                        or re.match(r"\s+'\\", regex_output.group(1)):

                    self.irc.send_privmsg("Error: Regular expression must not be nil.")
                    return

                elif regex_output.group(1) != "":
                    command_regex = regex_output.group(1)
                    temp_parameters = parameters[(regex_output.end() + 1):]

                else:
                    self.irc.send_privmsg("Error: Unexpected error occurred.")
                    return

            else:
                self.irc.send_privmsg("Error: Regular expression must be surrounded with closing characters "
                                      "(\'<regex>'\).")
                return

        else:
            self.irc.send_privmsg("Error: Regular expression must be given.")
            return

        if temp_parameters == '':
            self.irc.send_privmsg("Error: Output must be given.")
            return

        command_output = temp_parameters

        self.irc.send_privmsg("Success: Name: '%s' | Regexp: '%s' | Output: '%s'" %
                              (command_name, command_regex, command_output))
        return

    def edit(self):
        pass

    def delete(self):
        pass
