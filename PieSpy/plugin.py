###
# Copyright (c) 2010, William Donaldson
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import pyPie

import supybot.conf as conf
import supybot.world as world
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.registry as registry
import supybot.callbacks as callbacks

class PieSpy(callbacks.Plugin):
    """This plugin creates a social networking graph based on the connections
    between the users talking in your channels."""
    threaded = True
    instances = {}
    
    def __init__(self, irc):
        self.__parent = super(PieSpy, self)
        self.__parent.__init__(irc)
        for ircd in world.ircs:
            self.instances[ircd.network] = \
                pyPie.PieInstance(ircd.nick, 
                                  ircd.network,
                                  outputDirectory=conf.supybot.directories.data.dirize("PieSpy/%s/images/" % ircd.network)
                                  )
    
    def doPrivmsg(self, irc, msg):
        if irc.isChannel(msg.args[0]):
            channel = msg.args[0]
            sender = msg.nick
            if ircmsgs.isAction(msg):
                message = ircmsgs.unAction(msg)
            else:    
                message = msg.args[1]
            self.instances[irc.network].onMessage(channel, sender, message)
    
    def doMode(self, irc, msg):
        channel = msg.args[0]
        sender = msg.nick
        self.instances[irc.network].onMode(channel, sender)
    
    def doJoin(self, irc, msg):
        channel = msg.args[0]
        sender = msg.nick
        self.instances[irc.network].onJoin(channel, sender)
    
    def doKick(self, irc, msg):
        channel = msg.args[0]
        sender = msg.nick
        kicked = msg.args[1].split(',')
        for nick in kicked:
            self.instances[irc.network].onKick(channel, sender, nick)
    
    def doNick(self, irc, msg):
        oldNick = msg.nick
        newNick = msg.args[0]
        self.instances[irc.network].onNickChange(oldNick, newNick)


Class = PieSpy


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
