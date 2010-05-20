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

import re

import supybot.conf as conf
import supybot.ircutils as ircutils
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('PieSpy', True)

PieSpy = conf.registerPlugin('PieSpy')
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(PieSpy, 'someConfigVariableName',
#     registry.Boolean(False, """Help for someConfigVariableName."""))

#############################################################################
####### --------------------------- Image --------------------------- #######
#############################################################################

conf.registerGroup(PieSpy, 'image')

conf.registerChannelValue(PieSpy.image, 'outputWidth',
    registry.PositiveInteger(800, """Determines the width in pixels of the
    resulting graph."""))
conf.registerChannelValue(PieSpy.image, 'outputHeight',
    registry.PositiveInteger(600, """Determines the height in pixels of the
    resulting graph."""))
conf.registerGlobalValue(PieSpy.image, 'outputDirectory',
    registry.String(
        conf.supybot.directories.data.dirize("PieSpy/"),
        """Determines the directory images will be output to."""))
conf.registerGlobalValue(PieSpy.image, 'createCurrent',
    registry.Boolean(True, """Determines whether the current graph will be
    saved to a specific file."""))
conf.registerGlobalValue(PieSpy.image, 'createArchive',
    registry.Boolean(False, """Determines whether past graphs will be saved.
    This is turned off by default to prevent your hard drive space from being
    needlessly wasted!"""))
conf.registerGlobalValue(PieSpy.image, 'createRestorePoints',
    registry.Boolean(True, """Determines whether a restore point for the last
    graph generated will be saved. If your bot goes down and you have this
    enabled, PieSpy will be able to pick up from where it left off when your
    bot comes back online. Otherwise, it would start a fresh graph."""))

#############################################################################
####### --------------------------- Color --------------------------- #######
#############################################################################

class Color(registry.String):
    """Value must be a string representing a color that can be understood by
    PIL's ImageColor.getrgb()."""
    _colorregexes = [re.compile(x) for x in [
        "#\w\w\w$",
        "#\w\w\w\w\w\w$",
        "rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$",
        "rgb\(\s*(\d+)%\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)$",
        "hsl\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)$",
    ]]
    _colormap = [
        # X11 colour table (from "CSS3 module: Color working draft"), with
        # gray/grey spelling issues fixed.  This is a superset of HTML 4.0
        # colour names used in CSS 1.
        "aliceblue",
        "antiquewhite",
        "aqua",
        "aquamarine",
        "azure",
        "beige",
        "bisque",
        "black",
        "blanchedalmond",
        "blue",
        "blueviolet",
        "brown",
        "burlywood",
        "cadetblue",
        "chartreuse",
        "chocolate",
        "coral",
        "cornflowerblue",
        "cornsilk",
        "crimson",
        "cyan",
        "darkblue",
        "darkcyan",
        "darkgoldenrod",
        "darkgray",
        "darkgrey",
        "darkgreen",
        "darkkhaki",
        "darkmagenta",
        "darkolivegreen",
        "darkorange",
        "darkorchid",
        "darkred",
        "darksalmon",
        "darkseagreen",
        "darkslateblue",
        "darkslategray",
        "darkslategrey",
        "darkturquoise",
        "darkviolet",
        "deeppink",
        "deepskyblue",
        "dimgray",
        "dimgrey",
        "dodgerblue",
        "firebrick",
        "floralwhite",
        "forestgreen",
        "fuchsia",
        "gainsboro",
        "ghostwhite",
        "gold",
        "goldenrod",
        "gray",
        "grey",
        "green",
        "greenyellow",
        "honeydew",
        "hotpink",
        "indianred",
        "indigo",
        "ivory",
        "khaki",
        "lavender",
        "lavenderblush",
        "lawngreen",
        "lemonchiffon",
        "lightblue",
        "lightcoral",
        "lightcyan",
        "lightgoldenrodyellow",
        "lightgreen",
        "lightgray",
        "lightgrey",
        "lightpink",
        "lightsalmon",
        "lightseagreen",
        "lightskyblue",
        "lightslategray",
        "lightslategrey",
        "lightsteelblue",
        "lightyellow",
        "lime",
        "limegreen",
        "linen",
        "magenta",
        "maroon",
        "mediumaquamarine",
        "mediumblue",
        "mediumorchid",
        "mediumpurple",
        "mediumseagreen",
        "mediumslateblue",
        "mediumspringgreen",
        "mediumturquoise",
        "mediumvioletred",
        "midnightblue",
        "mintcream",
        "mistyrose",
        "moccasin",
        "navajowhite",
        "navy",
        "oldlace",
        "olive",
        "olivedrab",
        "orange",
        "orangered",
        "orchid",
        "palegoldenrod",
        "palegreen",
        "paleturquoise",
        "palevioletred",
        "papayawhip",
        "peachpuff",
        "peru",
        "pink",
        "plum",
        "powderblue",
        "purple",
        "red",
        "rosybrown",
        "royalblue",
        "saddlebrown",
        "salmon",
        "sandybrown",
        "seagreen",
        "seashell",
        "sienna",
        "silver",
        "skyblue",
        "slateblue",
        "slategray",
        "slategrey",
        "snow",
        "springgreen",
        "steelblue",
        "tan",
        "teal",
        "thistle",
        "tomato",
        "turquoise",
        "violet",
        "wheat",
        "white",
        "whitesmoke",
        "yellow",
        "yellowgreen",
    ]
    def setValue(self, v):
        ismatch = False
        for regex in self._colorregexes:
            m = regex.match(v)
            if m:
                ismatch = True
                break
        if not ismatch:
            if v.lower() not in self._colormap:
                self.error()
        registry.String.setValue(self, v)

conf.registerGroup(PieSpy, 'color')

conf.registerChannelValue(PieSpy.color, 'backgroundColor',
    Color("#FFFFFF", """Determines the color of the graph's background."""))
conf.registerChannelValue(PieSpy.color, 'channelColor',
    Color("#EEEEFF", """Determines the color the channel name will be printed
    in on the graph."""))
conf.registerChannelValue(PieSpy.color, 'labelColor',
    Color("#000000", """Determines the color the node labels will be printed
    in on the graph."""))
conf.registerChannelValue(PieSpy.color, 'titleColor',
    Color("#9999CC", """Determines the color the title will be printed in on
    the graph."""))
conf.registerChannelValue(PieSpy.color, 'nodeColor',
    Color("#FFFF00", """Determines the color the node will be drawn in on the
    graph."""))
conf.registerChannelValue(PieSpy.color, 'edgeColor',
    Color("#6666FF", """Determines the color the edges will be drawn in on the
    graph."""))
conf.registerChannelValue(PieSpy.color, 'borderColor',
    Color("#666666", """Determines the color the border will be drawn in on
    the graph."""))

#############################################################################
####### -------------------------- Ignore --------------------------- #######
#############################################################################

class Nick(registry.String):
    """Value is not a valid nick."""
    def set(self, s):
        if not ircutils.isNick(s):
            self.error()
        registry.String.set(self, s)

class CommaSeparatedListOfNicks(registry.SeparatedListOf):
    """Value must be a comma separated list of nicks."""
    Value = Nick
    def splitter(self, s):
        return re.split(r'\s*,\s*', s)
    joiner = ', '.join

conf.registerGroup(PieSpy, 'ignore')

conf.registerChannelValue(PieSpy.ignore, 'ignoreSet',
    CommaSeparatedListOfNicks("", """Determines which nicks will be
    ignored."""))

#############################################################################
####### ------------------------- Advanced -------------------------- #######
#############################################################################

_adv_warning = """\n\nDO NOT EDIT THIS VALUE UNLESS YOU KNOW WHAT YOU ARE DOING.
    Bad things could happen!"""

conf.registerGroup(PieSpy, 'advanced')

conf.registerGlobalValue(PieSpy.advanced, 'temporalDecayAmount',
    registry.Float(0.02, """Determines how quickly existing edges
    decay."""+_adv_warning))
conf.registerGlobalValue(PieSpy.advanced, 'springEmbedderIterations',
    registry.PositiveInteger(1000, """Determines how many times the spring
    embedder is run between graphs."""+_adv_warning))
conf.registerGlobalValue(PieSpy.advanced, 'k',
    registry.Float(2, """It's magic!"""+_adv_warning))
conf.registerGlobalValue(PieSpy.advanced, 'c',
    registry.Float(0.01, """It's magic!"""+_adv_warning))
conf.registerGlobalValue(PieSpy.advanced, 'maxRepulsiveForceDistance',
    registry.PositiveFloat(6, """Determines the maximum repulsive force
    between two nodes."""+_adv_warning))
conf.registerGlobalValue(PieSpy.advanced, 'maxNodeMovement',
    registry.PositiveFloat(0.5, """"""+_adv_warning))
conf.registerGlobalValue(PieSpy.advanced, 'minDiagramSize',
    registry.PositiveFloat(10, """"""+_adv_warning))
conf.registerGlobalValue(PieSpy.advanced, 'borderSize',
    registry.NonNegativeInteger(50, """Determines the size of the border
    around the graph in pixels."""+_adv_warning))
conf.registerGlobalValue(PieSpy.advanced, 'nodeRadius',
    registry.PositiveInteger(5, """Determines the size of the nodes drawn
    on the graph in pixels."""+_adv_warning))
conf.registerGlobalValue(PieSpy.advanced, 'edgeThreshold',
    registry.Float(0, """Determines the minimum weight an edge must have
    to be drawn on the graph."""+_adv_warning))
conf.registerGlobalValue(PieSpy.advanced, 'showEdges',
    registry.Boolean(True, """Determines whether the edges will be drawn on
    the graph."""+_adv_warning))

#############################################################################
####### ------------------------- Heuristic ------------------------- #######
#############################################################################

conf.registerGroup(PieSpy, 'heuristic')

conf.registerGlobalValue(PieSpy.heuristic, 'adjacencyInferenceHeuristic',
    registry.Float(0.1, """Determines the weighting of this inference
    heuristic."""+_adv_warning))
conf.registerGlobalValue(PieSpy.heuristic, 'binarySequenceInferenceHeuristic',
    registry.Float(1, """Determines the weighting of this inference
    heuristic."""+_adv_warning))
conf.registerGlobalValue(PieSpy.heuristic, 'directAddressingInferenceHeuristic',
    registry.Float(1, """Determines the weighting of this inference
    heuristic."""+_adv_warning))
conf.registerGlobalValue(PieSpy.heuristic, 'indirectAddressingInferenceHeuristic',
    registry.Float(0.3, """Determines the weighting of this inference
    heuristic."""+_adv_warning))

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
