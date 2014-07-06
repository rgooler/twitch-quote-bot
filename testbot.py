#!virtualenv/bin/python
"""A simple example bot.

This is an example bot that uses the SingleServerIRCBot class from
irc.bot.  The bot enters a channel and listens for commands in
private messages and channel traffic.  Commands in channel messages
are given by prefixing the text by the bot name followed by a colon.
It also responds to DCC CHAT invitations and echos data sent in such
sessions.

The known commands are:

    stats -- Prints some channel information.

    disconnect -- Disconnect the bot.  The bot will try to reconnect
                  after 60 seconds.

    die -- Let the bot cease to exist.

    dcc -- Let the bot invite you to a DCC CHAT connection.
"""

import irc.bot
import irc.strings
import settings
import sqlite3


class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, password, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, password)],
                                            nickname, nickname)
        self.channel = channel
        self.db = sqlite3.connect('Quotes.db')
        self.cursor = self.db.cursor()

    def on_welcome(self, c, e):
        c.join(self.channel)
        sql = 'create table if not exists ' + self.channel + ' (id integer PRIMARY KEY, quote TEXT)'
        self.db.execute(sql)

    def on_pubmsg(self, c, e):
        print c.__dict__
        print e.__dict__
        recv = e.arguments[0]
        if not recv.startswith('!'):
            return
        if recv.startswith('!addquote'):
            self.do_command(e, '!addquote', recv[9:].strip())

    def do_command(self, e, cmd, args=None):
        # nick = e.source.nick
        # c = self.connection

        if cmd == "!addquote":
            pass
        if cmd == "!random":
            # output random quote
            pass


if __name__ == "__main__":
    s = settings
    bot = TestBot(s.CHANNEL, s.USER, s.HOST, s.PASSWORD, s.PORT)
    bot.start()
