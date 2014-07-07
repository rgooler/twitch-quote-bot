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
        self.db = sqlite3.connect('Bot.db')
        self.cursor = self.db.cursor()

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_join(self, c, e):
        s = 'CREATE TABLE IF NOT EXISTS %s_quotes '
        s += '(id INTEGER PRIMARY KEY AUTOINCREMENT, quote TEXT)'
        self.cursor.execute(s % e.target[1:])

    def on_pubmsg(self, c, e):
        recv = e.arguments[0]
        if not recv.startswith('!'):
            return
        if recv.startswith('!addquote'):
            self.cmd_addquote(c, e)
            # if nick in self.channels[e.target].operdict:
            #    self.cmd_addquote(e)
            #    return
            # else:
            #     print 'not op'
            #    self.do_command(e, '!addquote')
            #    return
        if recv.startswith('!quote'):
            self.cmd_sayquote(c, e)

    def cmd_addquote(self, c, e):
        print 'cmd_addquote()'
        quote = e.arguments[0]
        if quote is None:
            return
        # quote = str(e.arguments[0][len('!addquote'):].strip())
        sql = "INSERT INTO %s_quotes (quote) VALUES (?);" % e.target[1:]
        self.cursor.execute(sql, (quote,))
        self.db.commit()

    def cmd_sayquote(self, c, e, recursions=0):
        if recursions >= 3:
            return
        print 'cmd_sayquote()'
        # output random quote
        sql = 'SELECT quote FROM %s_quotes WHERE '
        sql += 'id = (abs(random()) %% (SELECT MAX(id) FROM %s_quotes));'
        sql = sql % (e.target[1:], e.target[1:])
        self.cursor.execute(sql)
        try:
            (quote,) = self.cursor.fetchone()
            print quote
            c.privmsg(e.target, quote)
        except:
            # Sometimes, this returns a none. If so, try again
            self.cmd_sayquote(c, e, recursions + 1)

if __name__ == "__main__":
    s = settings
    bot = TestBot(s.CHANNEL, s.USER, s.HOST, s.PASSWORD, s.PORT)
    bot.start()
