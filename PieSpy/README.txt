This plugin requires that you have the PIL and aggdraw modules installed.
You don't need to set up aggdraw to work with freetype though since it's
too much of a hassle for even me!

This plugin makes pretty graphs based on the conversations users in your
channels have with each other. It figures out who's talking to each other
and then plots a graph of the social networks contained within your
channels. A nice example can be seen here:

	http://imgur.com/FrsJT.png

The plugin now supports configuring graph output and specializing it for
different channels. After changing config values, though, you will have to
reload the plugin in order for them to take effect. (Also, if you are
installing the plugin over an old version that didn't support configuring
graph output, you will have to restart your Supybot after installing to be
able to load the updated version.)

To install this plugin, place the PieSpy/ directory into your Supybot
plugin directory and tell your bot to `load PieSpy`.