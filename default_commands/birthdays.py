import re
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

        temp_split = self.message.split(" ")
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
