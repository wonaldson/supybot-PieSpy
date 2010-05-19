This plugin requires that you have the PIL and aggdraw modules installed.
You don't need to set up aggdraw to work with freetype though since it's
too much of a hassle for even me!

This plugin makes pretty graphs based on the conversations users in your
channels have with each other. It figures out who's talking to each other
and then plots a graph of the social networks contained within your
channels. A nice example can be seen here:

	http://imgur.com/FrsJT.png

The plugin is in a very early state and right now doesn't support
configuring the graph output to the extent that the original PieSpy did.
This will be worked on in the future.

To install this plugin, place the PieSpy/ directory into your Supybot
plugin directory and tell your bot to `load PieSpy`.