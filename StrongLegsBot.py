import logging
import os
import time
import socket
import sqlite3 as sql
import sys

import _functions
import filters
import _reloadbot
import unpackconfig

cfg = unpackconfig.configUnpacker()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class IRC:
    def __init__(self):
        # Initializes all class variables
        self.config = cfg.unpackcfg()
        self.CHANNEL = sys.argv[1] if len(sys.argv) > 1 else "#thekillar25"
        self.USERNAME = self.config['settings_username']
        self.PASSWORD = self.config['settings_password']
        self.HOST = self.config['settings_host']
        self.PORT = int(self.config['settings_port'])

        self.privmsg_str = "PRIVMSG {channel} :".format(channel=self.CHANNEL)
        self.custom = False

        if os.path.isfile('debug.txt'):
            fileread = open('debug.txt', 'r')
            self.custom = fileread.readline().strip("\n")

    def init(self):
        try:
            sock.connect((self.HOST, self.PORT))
            sock.settimeout(0.01)
            self.send_raw('CAP REQ :twitch.tv/membership\r\n')
            self.send_raw('CAP REQ :twitch.tv/tags\r\n')
            self.send_raw('CAP REQ :twitch.tv/commands\r\n')
            self.send_raw('PASS %s\r\n' % self.PASSWORD)
            self.send_raw('NICK %s\r\n' % self.USERNAME)
            self.send_raw('JOIN %s\r\n' % self.CHANNEL)
        except Exception as ERR_exception:
            logging.critical(ERR_exception)

    # Send raw message to Twitch
    def send_raw(self, output):
        sock.send(output.format(channel=self.CHANNEL).encode("UTF-8"))

    def send_privmsg(self, output, me=False):
        me = '/me : ' if me else ''
        custom = self.custom if self.custom else ''
        formatted_output = "%s%s{output}\r\n"\
                           .format(output=output) % (me, custom)

        self.send_raw(self.privmsg_str + formatted_output)
        logging.info("[PRIVMSG] :| [SENT] %s: %s", self.CHANNEL, formatted_output.strip("\r\n"))

    def send_timeout(self, output, target, duration):
        custom = self.custom if self.custom else ''
        self.send_raw(self.privmsg_str + '.timeout {target} {duration} %s{reason}\r\n'
                      .format(target=target,
                              duration=duration,
                              reason=output)) % custom

    def send_ban(self, output, target):
        custom = self.custom if self.custom else ''
        self.send_raw(self.privmsg_str + '.ban {target} %s{reason}\r\n'
                      .format(target=target,
                              reason=output)) % custom

    def send_whisper(self, output, target):
        custom = self.custom if self.custom else ''
        formatted_output = ".w {target} %s{output}\r\n"\
                           .format(output=output, target=target) % custom
        self.send_raw(self.privmsg_str + formatted_output)
        logging.info("[WHISPER] :| [SENT] %s: %s" % (self.CHANNEL, formatted_output.strip("\r\n")))


# Class housing main loop for SLB
class Bot:
    def __init__(self):
        sock.settimeout(0.01)
        self.data = "."
        self.databuffer = ''
        self.temp = ''
        self.currentdatetime = 0
        self.currentdatetimelist = []
        self.olddatetime = 0
        self.olddatetimelist = []
        self.startmarkloop = 0
        self.endmarkloop = 0
        self.previous_line = None
        self.mainloopbreak = False

        self.sqlConnectionChannel = None
        self.sqlCursorChannel = None
        self.sqlconn = None

        self.ignoredusersfile = None
        self.ignoredusersread = None
        self.ignoredusers = None

        self.birthdayusers = {}

    def init(self):
        self.currentdatetime = time.gmtime(time.time())
        self.olddatetime = time.gmtime(time.time())
        self.ignoredusersfile = open('ignoredusers.txt', 'r')
        self.ignoredusersread = self.ignoredusersfile.readlines()
        self.ignoredusers = [username.strip('\n').strip('\r') for username in self.ignoredusersread]

        if sys.platform == "linux2":
            self.sqlConnectionChannel = sql.connect('SLB.sqlDatabase/{}DB.db'
                                                    .format(IRC().CHANNEL.strip("#")))
        else:
            self.sqlConnectionChannel = sql.connect(os.path.dirname(os.path.abspath(__file__)) +
                                                    '\SLB.sqlDatabase\{}DB.db'
                                                    .format(IRC().CHANNEL.strip("#").strip("\n")))

        self.sqlCursorChannel = self.sqlConnectionChannel.cursor()
        self.sqlconn = (self.sqlConnectionChannel, self.sqlCursorChannel)

        self.sqlCursorChannel.execute(
            'CREATE TABLE IF NOT EXISTS birthdays(userid TEXT, username TEXT, displayname TEXT, date TEXT)'
        )
        self.sqlCursorChannel.execute(
            'CREATE TABLE IF NOT EXISTS config(variable TEXT, value TEXT, args TEXT)'
        )

        self.olddatetimelist = [int(self.olddatetime[index]) for index in range(0, 6)]
        self.currentdatetimelist = [int(self.currentdatetime[index]) for index in range(0, 6)]

        self.getbirthdayusers()
        return

    def getbirthdayusers(self):
        self.sqlCursorChannel.execute("SELECT * FROM birthdays WHERE date LIKE ?",
                                      ('{}%'.format("%s/%s" % (self.currentdatetimelist[2],
                                                               self.currentdatetimelist[1])),))
        sqlCursorOffload = self.sqlCursorChannel.fetchall()

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
                    temp_age = (self.currentdatetimelist[0] - temp_birthyear)
                    temp_age = ordinal(temp_age)

                self.birthdayusers[username] = (displayname, temp_age)

        else:
            pass

        logging.info("[_BOTCOM] :| [CVAR] Birthday users: %s" % list(self.birthdayusers.keys()))

        return

    def main(self):
        while not self.mainloopbreak:
            try:
                try:
                    # Attempts a data grab from twitch
                    self.data = sock.recv(1024).decode("UTF-8")
                    self.databuffer = self.databuffer + self.data  # Appends data received to buffer
                    self.temp = self.databuffer.rsplit('\n')  # Splits buffer into list
                    self.databuffer = self.temp.pop()  # Grabs the last list item and assigns to buffer

                except socket.timeout:
                    self.temp = []  # Makes empty list if socket returns None

                # Checks if socket conn closed, then restarts
                if len(self.data) == 0:
                    _funcdiagnose.bot_restart("Lost connection with Twitch IRC server", user_loggingchoice)

                # Captures current time for response time measuring
                if self.temp:
                    self.olddatetime = self.currentdatetime
                    self.olddatetimelist = list(map(int, self.olddatetime))
                    self.currentdatetime = time.gmtime(time.time())
                    self.currentdatetimelist = list(map(int, self.currentdatetime))

                    self.startmarkloop = time.time()
                    logging.debug("START MARK")

                    if (self.currentdatetimelist[2] - self.olddatetimelist[2]) != 0:
                        self.getbirthdayusers()
                        return

                else:
                    continue

                # Loop for dealing with each item separately
                for line in self.temp:
                    logging.debug(repr(line))

                    # Parse and extract data from line and display formatted string
                    parsetype, identifier, info, display, parsed = _functions.parse(irc, self.sqlconn, line).parse()

                    if display:
                        logging.info("[%s] :| %s", parsetype.upper(), parsed)

                    if "username" in info and info["username"] in self.ignoredusers:
                        continue

                    if identifier == "366":
                        logging.info("[_BOTCOM] :| [JOIN] Joined %s Successfully..." % irc.CHANNEL)

                    # Find and deal with periodic ping request (approx. every 5 minutes,
                    # socket disconnect after 11 minutes)
                    if identifier == "PING":
                        pingstring = info[1]
                        pingstring = pingstring.replace(":", "").strip("\r")
                        irc.send_raw("PONG%s\r\n" % pingstring)

                    if identifier == "JOIN":
                        if info["username"] in list(self.birthdayusers.keys()):
                            irc.send_privmsg("Birthday Boy/Girl %s has joined the chat!"
                                             " Wish them a happy %s birthday!"
                                             % (self.birthdayusers[info["username"]][0],
                                                self.birthdayusers[info["username"]][1]),
                                             True)

                    if identifier == "PART":
                        pass

                    # Find and deal with user chat messages, majority of activity occurs here
                    if identifier == "privmsg":
                        handleuserlevel = (info["user-id"], info["username"], info["user-type"],
                                           info["subscriber"], info["turbo"])

                        # Determines user's status as an integer
                        #   0 - Normal users
                        #  50 - Turbo
                        # 100 - Subscribers
                        # 150 - Regulars
                        # 250 - Moderators
                        # 350 - Global Moderators
                        # 400 - Broadcaster
                        # 500 - Admin
                        # 600 - Staff
                        # 700 - TheKillar25

                        userlevel = _funcdata.handleUserLevel(handleuserlevel)
                        info["userlevel"] = userlevel

                        # Passes user through filters if permission level is under 250
                        if userlevel < 250:
                            if filters.filters(irc, self.sqlconn, info).linkprotection():
                                continue  # If one of the filters return True, the user is omitted

                        # -=-=-=-=-=-=-= Non-restricted users past this point =-=-=-=-=-=-=-

                        _funcdata.handleCommands(info)

                        if info["userlevel"] >= 700 and info["privmsg"].startswith("$forcerestart"):
                            _funcdiagnose.bot_restart("Forced restart by bot admin", user_loggingchoice)

                    # Find and deal with whispers
                    if identifier == "whisper":
                        if irc.CHANNEL in info['privmsg']:
                            logging.info("[%s] :| %s", parsetype.upper(), parsed)

                        handleuserlevel = (info["user-id"], info["username"], info["user-type"],
                                           0, info["turbo"])
                        userlevel = _funcdata.handleUserLevel(handleuserlevel, True)
                        info["userlevel"] = userlevel

                        temp_split_message = info["privmsg"].split(" ")
                        if info["username"] == 'thekillar25':
                            if temp_split_message[0] == '!reload':
                                logging.warning("IMPORTANT: Reloading app resources")
                                try:
                                    _reloadbot.reloadall()
                                except Exception as e:
                                    logging.error(e)

                            if temp_split_message[0] == '$forcerestart':
                                if len(temp_split_message) == 2:
                                    if temp_split_message[1] in ('all', irc.CHANNEL):
                                        _funcdiagnose.bot_restart("Forced restart by admin", user_loggingchoice)
                                elif len(temp_split_message) > 2:
                                    if temp_split_message[1] in ('all', irc.CHANNEL):
                                        if temp_split_message[2] in ('/me', '.me'):
                                            irc.send_privmsg(" ".join(temp_split_message[3:]), True)
                                        else:
                                            irc.send_privmsg(" ".join(temp_split_message[2:]))

                                        _funcdiagnose.bot_restart("Forced restart by admin", user_loggingchoice)

                            if temp_split_message[0] == '$stop':
                                if len(temp_split_message) == 2:
                                    if temp_split_message[1] in ('all', irc.CHANNEL):
                                        raise KeyboardInterrupt
                                elif len(temp_split_message) > 2:
                                    if temp_split_message[1] in ('all', irc.CHANNEL):
                                        if temp_split_message[2] in ('/me', '.me'):
                                            irc.send_privmsg(" ".join(temp_split_message[3:]), True)
                                        else:
                                            irc.send_privmsg(" ".join(temp_split_message[2:]))

                                        raise KeyboardInterrupt

                            if temp_split_message[0] == '$send' and userlevel >= 400:
                                if len(temp_split_message) <= 2:
                                    pass

                                if len(temp_split_message) > 2:
                                    if temp_split_message[1] == irc.CHANNEL or \
                                            (temp_split_message[1] == 'all' and userlevel >= 700):
                                        if temp_split_message[2] in ('/me', '.me'):
                                            irc.send_privmsg(" ".join(temp_split_message[3:]), True)
                                        else:
                                            irc.send_privmsg(" ".join(temp_split_message[2:]))

                        if temp_split_message[0] == irc.CHANNEL:
                            _funcdata.handleCommands(info, " ".join(temp_split_message[1:]), True)

                    if self.temp.index(line) == len(self.temp) - 1:
                        self.endmarkloop = time.time()
                        logging.debug("END MARK: Dealt with data chunk in %s milliseconds." %
                                      ((self.endmarkloop - self.startmarkloop) * 1000))

            except KeyboardInterrupt:
                logging.critical('Process Interrupted')
                self.mainloopbreak = True


if __name__ == '__main__':
    logging_levels = {'debug': logging.DEBUG, 'info': logging.INFO,
                      'warning': logging.WARNING, 'error': logging.ERROR,
                      'critical': logging.CRITICAL}

    # Set logging level based on sys.argv or set to default if none given
    if len(sys.argv) == 3:
        user_loggingchoice = sys.argv[2]
    else:
        user_loggingchoice = ""

    if user_loggingchoice.lower() not in logging_levels:  # If user entered a logging level that is incorrect
        logging_level = logging.INFO
    else:
        logging_level = logging_levels[user_loggingchoice]

    # Set logging formatting default
    logging.basicConfig(format='<%(asctime)s> %(filename)s:%(levelname)s:%(lineno)s: %(message)s',
                        level=logging_level)

    # Create instances of each class in StrongLegsBot and initialize IRC conn
    irc = IRC()
    irc.init()
    bot = Bot()
    bot.init()

    # Shorten function calls and create instance
    _funcdiagnose = _functions.diagnostic(irc, bot.sqlconn)
    _funcdata = _functions.data(irc, bot.sqlconn)

    bot.main()
    sys.exit("Main loop exited")
