import logging
import re

import default_commands
from default_commands._exceptions import *


class Commands:
    def __init__(self, irc, sqlconn, info, userlevel=0):
        self.local_dispatch_map = {'add': self.add, 'edit': self.edit,
                                   'delete': self.delete, 'help': self.help,
                                   '': self.disp_commands}
        self.irc = irc
        self.sqlConnectionChannel, self.sqlCursorChannel = sqlconn
        self.info = info
        self.message = info["privmsg"]
        self.userlevel = userlevel

        self.sqlCursorChannel.execute('CREATE TABLE IF NOT EXISTS commands(userlevel INTEGER, keyword TEXT, output TEXT, args INTEGER, sendtype TEXT, syntaxerr TEXT)')

        temp_split = self.message.split(' ')
        if len(temp_split) > 1:
            if temp_split[1] == 'help':
                self.help()
            elif userlevel >= 250:
                if temp_split[1] == 'add':
                    self.add()
                elif temp_split[1] == 'edit':
                    self.edit()
                elif temp_split[1] == 'delete':
                    self.delete()
                else:
                    self.irc.send_privmsg("Error: '%s' is not a valid command variation." % temp_split[1])
                    return
            else:
                self.irc.send_privmsg('Error: You are not allowed to use any variations of {command}.'
                                      .format(command=default_commands.dispatch_naming['commands']))
                return
        else:
            self.disp_commands()

    def disp_commands(self):
        self.sqlCursorChannel.execute('SELECT userlevel FROM commands')

        sqlCursorOffload = self.sqlCursorChannel.fetchall()

        if sqlCursorOffload == []:
            self.irc.send_privmsg(': Error: Channel %s has no custom commands.' % self.irc.CHANNEL, True)
            return

        self.sqlCursorChannel.execute('SELECT * FROM commands WHERE userlevel <= ?', (self.userlevel,))

        sqlCursorOffload = self.sqlCursorChannel.fetchall()

        command_dict = {}
        command_string = ''

        for entry in sqlCursorOffload:
            if entry[0] not in command_dict.keys():
                command_dict[entry[0]] = []

            command_dict[entry[0]].append(entry[1])

        if sqlCursorOffload == []:
            self.irc.send_whisper("Error: Channel '%s' has no commands available for use with your current userlevel "
                                  "(%s)" % (self.irc.CHANNEL, self.userlevel), self.info['username'])
            return

        for key in sorted(command_dict.keys(), reverse=True):
            command_string += ("%s: %s | " % (key, ", ".join(sorted(command_dict[key]))))

        self.irc.send_whisper('Custom commands in channel %s, available with your userlevel (%s), are: %s'
                              % (self.irc.CHANNEL, self.userlevel, command_string.strip(" | ")),
                              self.info['username'])
        return

    def help(self):
        parameters = self.message.split("help", 1)
        if len(parameters[1]) <= 0:
            command_keyword = default_commands.dispatch_naming['commands']
            if command_keyword not in default_commands.help_defaults:
                self.irc.send_privmsg("Error: '%s' is not a valid command variation." % command_keyword)
                return

            command_help = default_commands.help_defaults[command_keyword][''].format(command=command_keyword)
            self.irc.send_privmsg(('%s help -> ' + command_help) % command_keyword, True)
            return

        parameters = parameters[1].strip()
        split_params = parameters.split(" ")
        command_keyword = split_params[0].strip()
        command_variant = split_params[1].strip() if len(split_params) == 2 else ''

        try:
            if command_keyword in default_commands.dispatch_map:
                command_help = default_commands.help_defaults[command_keyword][command_variant] \
                    .format(command=command_keyword)
                self.irc.send_privmsg(('%s %s -> ' + command_help) % (command_keyword, command_variant), True)
            else:
                self.irc.send_privmsg("Error: '%s' is not a valid command." % command_keyword)
                return
        except KeyError:
            self.irc.send_privmsg("Error: '%s' is not a valid command variation of '%s'."
                                  % (command_variant, command_keyword))
            return

    def add(self):
        try:
            parameters = self.message.split("add", 1)
            if len(parameters[1]) <= 0:
                raise DCIncorrectAmountArgsError

            parameters = parameters[1].strip()
            split_params = parameters.split(" ")
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
                elif split_params[split_pos].startswith("-sm=") and self.info["userlevel"] >= 400:
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

                elif split_params[split_pos].startswith("-sm=") and self.info["userlevel"] < 400:
                    self.irc.send_privmsg("Permissions Error: You don't have the permissions to specify command "
                                          "sendmode.")

                else:
                    command_sendmode = "privmsg"

            command_keyword = split_params[command_offset]

            if command_keyword in default_commands.dispatch_map:
                self.irc.send_privmsg("Error: Command keyword must not shadow a default command.")
                return

            command_output = " ".join(split_params[(command_offset + 1):])

            self.sqlCursorChannel.execute('SELECT keyword FROM commands WHERE keyword == ?',
                                          (command_keyword,))
            sqlCursorOffload = self.sqlCursorChannel.fetchone()
            if sqlCursorOffload is not None:
                self.irc.send_privmsg("Error: Command with keyword '%s' already exists." % command_keyword)
                return

            command_args = 0
            for x in range(3):
                for word in command_output.split(" "):
                    if "{arg%d}" % (x + 1) in word:
                        command_args += 1
                        break

            syntaxerr = "Error: Unexpected error occurred."

            if command_args > 0:
                syntaxerr = "Syntax Error: %s" % command_keyword
                for x in range(command_args):
                    syntaxerr += " <arg%d>" % (x + 1)

            self.sqlCursorChannel.execute(
                'INSERT INTO commands (userlevel, keyword, output, args, sendtype, syntaxerr) '
                'VALUES (?, ?, ?, ?, ?, ?)', (command_userlevel, command_keyword, command_output,
                                              command_args, command_sendmode, syntaxerr)
            )
            self.sqlConnectionChannel.commit()

            self.irc.send_privmsg("Added '%s' successfully." % command_keyword)
            return

        except DCIncorrectAmountArgsError:
            logging.warning("No arguments found")
            self.irc.send_privmsg("Error: Incorrect amount of arguments given.")

        except DCSyntaxError:
            pass

        except IndexError:
            self.irc.send_privmsg("Error: Incorrect amount of arguments given.")
            return

        except Exception as e:
            self.irc.send_privmsg("@TheKillar25, There is a FUCKING issue man, help me pls :( %s" % str(e))
            return

    def edit(self):
        parameters = self.message.split("edit", 1)
        if len(parameters[1]) <= 0:
            logging.warning("No arguments found")
            self.irc.send_privmsg("Error: Incorrect amount of arguments given.")
            return
        try:
            parameters = parameters[1].strip()
            split_params = parameters.split(" ")
            command_output = ""
            command_args = 0
            command_syntaxerr = "Error: Unexpected error occurred"
            command_offset = 0
            command_userlevel = 0
            command_sendmode = "privmsg"
            output_specified = False
            userlevel_specified = False
            sendmode_specified = False

            command_keyword = split_params[0]
            if len(split_params) <= 1:
                self.irc.send_privmsg("Error: Edit command must have at least 1 edit parameter "
                                      "(type \"{command} help {command} edit\" for information."
                                      .format(command=default_commands.dispatch_naming["commands"]))
                return

            self.sqlCursorChannel.execute('SELECT * FROM commands WHERE keyword == ?',
                                          (command_keyword,))

            sqlCursorOffload = self.sqlCursorChannel.fetchone()

            if sqlCursorOffload is None:
                self.irc.send_privmsg("Error: Command with keyword '%s' does not exist" % command_keyword)
                return

            if "-output=" in parameters:
                regex_output = '-output=(.*\")'
                regex_output = re.search(regex_output, parameters)
                if regex_output is not None:
                    if regex_output.group(1) == '' or regex_output.group(1) == '""'\
                            or re.match('"\s+"', regex_output.group(1)):

                        self.irc.send_privmsg("Error: Output must not be nil.")
                        return
                    elif regex_output.group(1) == '"' or (not regex_output.group(1).startswith('"')
                                                          or not regex_output.group(1).endswith('"')):
                        self.irc.send_privmsg("Error: Output must be surrounded with double-quotes.")
                        return
                    elif regex_output.group(1) != '':
                        command_output = regex_output.group(1).strip('"')
                        output_specified = True
                    else:
                        command_output = sqlCursorOffload[2]
                else:
                    self.irc.send_privmsg("Error: Output must not be nil.")
                    return

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

                elif split_params[split_pos].startswith("-sm=") and self.info["userlevel"] >= 400:
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

                elif split_params[split_pos].startswith("-sm=") and self.info["userlevel"] < 400:
                    self.irc.send_privmsg("Permissions Error: You don't have the permissions to specify command "
                                          "sendmode.")

                else:
                    command_sendmode = "privmsg"

            if not output_specified and sqlCursorOffload is not None:
                command_output = sqlCursorOffload[2]
                command_args = sqlCursorOffload[3]
                command_syntaxerr = sqlCursorOffload[5]

            elif output_specified:
                command_args = 0
                for x in range(3):
                    for word in command_output.split(" "):
                        if "{arg%d}" % (x + 1) in word:
                            command_args += 1
                            break

                if command_args > 0:
                    command_syntaxerr = "Syntax Error: %s" % command_keyword
                    for x in range(command_args):
                        command_syntaxerr += " <arg%d>" % (x + 1)
                else:
                    command_syntaxerr = "Error: Unexpected error occurred"

            else:
                self.irc.send_privmsg("Unexpected Error has ocurred.")
                logging.error("Edit command error.")
                return

            if not userlevel_specified and sqlCursorOffload is not None:
                command_userlevel = int(sqlCursorOffload[0])

            if not sendmode_specified and sqlCursorOffload is not None:
                command_sendmode = sqlCursorOffload[4]

            self.sqlCursorChannel.execute(
                'UPDATE commands SET userlevel = ?, output = ?, args = ?, sendtype = ?, syntaxerr = ? '
                'WHERE keyword = ?', (command_userlevel, command_output, command_args, command_sendmode,
                                      command_syntaxerr, command_keyword)
            )
            self.sqlConnectionChannel.commit()

            self.irc.send_privmsg("Edited '%s' successfully." % command_keyword)
            return

        except IndexError:
            self.irc.send_privmsg("Error: Incorrect amount of arguments given.")
            return

        except Exception as e:
            self.irc.send_privmsg("@TheKillar25, There is a FUCKING issue man, help me pls :( %s" % str(e))
            return

    def delete(self):
        parameters = self.message.split("delete", 1)
        if len(parameters[1]) <= 0:
            logging.warning("No arguments found")
            self.irc.send_privmsg("Error: Incorrect amount of arguments given.")
            return
        try:
            parameters = parameters[1].strip()
            split_params = parameters.split(" ")
            command_keyword = split_params[0]

            self.sqlCursorChannel.execute('SELECT keyword FROM commands WHERE keyword == ?',
                                          (command_keyword,))
            sqlCursorOffload = self.sqlCursorChannel.fetchone()

            if sqlCursorOffload is None:
                self.irc.send_privmsg("Error: Command with keyword '%s' does not exist" % command_keyword)
                return
            else:
                self.sqlCursorChannel.execute(
                    'DELETE FROM commands WHERE keyword == ?',
                    (command_keyword,)
                )
                self.sqlConnectionChannel.commit()

            self.irc.send_privmsg("Deleted '%s' successfully." % command_keyword)
            return

        except IndexError:
            self.irc.send_privmsg("Error: Incorrect amount of arguments given.")
            return

        except Exception as e:
            self.irc.send_privmsg("@TheKillar25, There is a FUCKING issue man, help me pls :( %s" % str(e))
            return
