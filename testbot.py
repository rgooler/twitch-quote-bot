#!virtualenv/bin/python
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
        self.create_dbs(e.target)

    def on_pubmsg(self, c, e):
        recv = e.arguments[0]
        cmd = recv.split(' ')[0].lower()
        if not recv.startswith('!'):
            return
        if cmd == '!addquote' and self.check_perms(c, e, cmd):
            self.cmd_addquote(c, e)
        if recv.startswith('!quote') and self.check_perms(c, e, cmd):
            self.cmd_quote(c, e)
        if recv.startswith('!reg') and self.check_perms(c, e, cmd):
            self.cmd_reg(c, e)

    def cmd_addquote(self, c, e):
        quote = str(e.arguments[0][len('!addquote'):].strip())
        if quote is None:
            return
        sql = "INSERT INTO %s_quotes (quote) VALUES (?);" % e.target[1:]
        self.cursor.execute(sql, (quote,))
        self.db.commit()

    def cmd_reg(self, c, e):
        l = str(e.arguments[0][len('!reg'):].strip()).split(' ')
        action = l[0].lower()
        nick = l[1].lower()
        if action is None or nick is None:
            return
        elif action == 'add':
            sql = "INSERT INTO %s_regulars (user) VALUES (?);" % e.target[1:]
            self.cursor.execute(sql, (nick,))
            self.db.commit()
            c.privmsg(e.target, 'Added %s to list of regulars' % nick)
        elif action == 'del':
            sql = "DELETE FROM %s_regulars WHERE user=?" % e.target[1:]
            self.cursor.execute(sql, (nick,))
            self.db.commit()
            c.privmsg(e.target, 'Removed %s from list of regulars' % nick)

    def cmd_quote(self, c, e, recursions=0):
        if recursions >= 3:
            return
        # output random quote
        sql = 'SELECT MAX(id) FROM %s_quotes' % e.target[1:]
        self.cursor.execute(sql)
        m = self.cursor.fetchone()
        sql = 'SELECT quote FROM %s_quotes WHERE id = abs(random() %% ?)'
        sql = sql % e.target[1:]
        self.cursor.execute(sql, m)
        try:
            (quote,) = self.cursor.fetchone()
            c.privmsg(e.target, quote)
        except:
            # Sometimes, this returns a none. If so, try again
            self.cmd_quote(c, e, recursions + 1)

    def create_dbs(self, channel):
        channel = channel.strip('#')
        s = 'CREATE TABLE IF NOT EXISTS %s_quotes '
        s += '(id INTEGER PRIMARY KEY AUTOINCREMENT, quote TEXT)'
        self.cursor.execute(s % channel)
        s = 'CREATE TABLE IF NOT EXISTS %s_regulars '
        s += '(id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT)'
        self.cursor.execute(s % channel)
        self.db.commit()

    def check_perms(self, c, e, cmd):
        channel = e.target[:1]
        nick = e.source.nick
        if nick in self.channels[e.target].operdict:
            return True
        if cmd == '!addquote':
            return self.user_is_regular(channel, nick)
        else:
            return True

    def user_is_regular(self, channel, nick):
        sql = 'SELECT * FROM %s_regulars WHERE user=?' % channel
        self.cursor.execute(sql, (nick.lower(), ))
        try:
            if self.cursor.fetchone() is None:
                return False
            return True
        except:
            return False
        return False

if __name__ == "__main__":
    s = settings
    bot = TestBot(s.CHANNEL, s.USER, s.HOST, s.PASSWORD, s.PORT)
    bot.start()
