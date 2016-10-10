import logging
import os
import sys
import sqlite3 as sql

import default_commands
from default_commands._exceptions import *

class regulars:
    def __init__(self, irc, msg_info, message, userlevel=0):
        self.local_dispatch_map = {'add': self.add, 'delete': self.delete, 'help': '',
                                   '': ''}
        self.irc = irc
        self.msg_info = msg_info
        self.message = message
        self.userlevel = userlevel

        if sys.platform == 'linux2':
            self.sqlConnectionChannel = sql.connect('SLB.sqlDatabase/{}DB.db'
                                                    .format(self.irc.CHANNEL.strip("#")))
        else:
            self.sqlConnectionChannel = sql.connect(os.path.dirname(__file__).rstrip('\\default_commands\\') +
                                                    '\SLB.sqlDatabase\{}DB.db'
                                                    .format(self.irc.CHANNEL.strip("#").strip("\n")))

        self.sqlCursorChannel = self.sqlConnectionChannel.cursor()

        self.sqlCursorChannel.execute('CREATE TABLE IF NOT EXISTS regulars(userid INTEGER, username TEXT)')

        temp_split = message.split(' ')
        if len(temp_split) > 1:
            if userlevel >= 250:
                if temp_split[1] == 'add':
                    self.add()
                elif temp_split[1] == 'delete':
                    self.delete()
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

