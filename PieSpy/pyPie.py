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

from PIL import Image, ImageDraw, ImageColor, ImageFont
from random import random
from datetime import datetime
import math, os, re, pickle, aggdraw
from time import time

def getset(s):
    return [x.lower() for x in s.split(",")]

def getcolor(s):
    return ImageColor.getrgb(s)

MIN_SEQ_SIZE = 5
    
colorstrip = re.compile("\x02|\x1F|\x16|\x0F|(\x03\d{1,2}(,\d{1,2})?)")

class PieInstance:
    VERSION = "PieSpy for Supybot"
    def __init__(self,
                 nick,
                 server,
                 outputWidth=800,
                 outputHeight=600,
                 outputDirectory="./images/",
                 createCurrent=True,
                 createArchive=False,
                 createRestorePoints=True,
                 backgroundColor="#ffffff",
                 channelColor="#eeeeff",
                 labelColor="#000000",
                 titleColor="#9999cc",
                 nodeColor="#ffff00",
                 edgeColor="#6666ff",
                 borderColor="#666666",
                 ignoreSet=[],
                 temporalDecayAmount=0.02,
                 springEmbedderIterations=1000,
                 k=2,
                 c=0.01,
                 maxRepulsiveForceDistance=6,
                 maxNodeMovement=0.5,
                 minDiagramSize=10,
                 borderSize=50,
                 nodeRadius=5,
                 edgeThreshold=0,
                 showEdges=True,
                 adjacencyInferenceHeuristic=0.1,
                 binarySequenceInferenceHeuristic=1,
                 directAddressingInferenceHeuristic=1,
                 indirectAddressingInferenceHeuristic=0.3,
                 version=""
                 ):
        
        #VERSION += version
        self.graphs = {}
        
        self.config = {}
        
        # [Server]
        self.config['nick'] = nick
        self.config['server'] = server
        
        # [Image]
        self.config['outputWidth'] = outputWidth
        self.config['outputHeight'] = outputHeight
        self.config['outputDirectory'] = outputDirectory
        self.config['createCurrent'] = createCurrent
        self.config['createArchive'] = createArchive
        self.config['createRestorePoints'] = createRestorePoints
        
        # [Color]
        self.config['backgroundColor'] = getcolor(backgroundColor)
        self.config['channelColor'] = getcolor(channelColor)
        self.config['labelColor'] = getcolor(labelColor)
        self.config['titleColor'] = getcolor(titleColor)
        self.config['nodeColor'] = getcolor(nodeColor)
        self.config['edgeColor'] = getcolor(edgeColor)
        self.config['borderColor'] = getcolor(borderColor)
        
        # [Ignore]
        self.config['ignoreSet'] = ignoreSet
        
        # [Advanced]
        self.config['temporalDecayAmount'] = temporalDecayAmount
        self.config['springEmbedderIterations'] = springEmbedderIterations
        self.config['k'] = k
        self.config['c'] = c
        self.config['maxRepulsiveForceDistance'] = maxRepulsiveForceDistance
        self.config['maxNodeMovement'] = maxNodeMovement
        self.config['minDiagramSize'] = minDiagramSize
        self.config['borderSize'] = borderSize
        self.config['nodeRadius'] = nodeRadius
        self.config['edgeThreshold'] = edgeThreshold
        self.config['showEdges'] = showEdges
        
        # [Heuristic]
        self.config['AdjacencyInferenceHeuristic'] = adjacencyInferenceHeuristic
        self.config['BinarySequenceInferenceHeuristic'] = binarySequenceInferenceHeuristic
        self.config['DirectAddressingInferenceHeuristic'] = directAddressingInferenceHeuristic
        self.config['IndirectAddressingInferenceHeuristic'] = indirectAddressingInferenceHeuristic

    def stripFormatting(self, message):
        return colorstrip.sub("", message)
    
    def onMessage(self, channel, sender, message):
        if sender.lower() not in self.config['ignoreSet']:
            self.add(channel, sender)
            key = channel.lower()
            graph = self.graphs.get(key)
            graph.infer(sender, self.stripFormatting(message))
    
    def onAction(self, sender, target, action):
        if target[0] in "#&!+":
            self.onMessage(target, sender, action)
    
    def onMode(self, channel, sourceNick):
        self.add(channel, sourceNick)
    
    def onJoin(self, channel, sender):
        self.add(channel, sender)
    
    def onKick(self, channel, kickerNick, recipientNick):
        self.add(channel, kickerNick)
        self.add(channel, recipientNick)
    
    def onNickChange(self, oldNick, newNick):
        self.changeNick(oldNick, newNick)
    
    def onUserList(self, channel, nicks):
        for nick in nicks:
            self.add(channel, nick)
    
    def add(self, channel, nick):
        if nick.lower() not in self.config['ignoreSet']:
            node = Node(nick)
            key = channel.lower()
        
            graph = None
            try:
                graph = self.graphs[key]
            except KeyError:
                if self.config['createRestorePoints']:
                    graph = self.readGraph(key)
                    if graph is None:
                        graph = Graph(channel, self.config)
                        self.graphs[key] = graph
                    else:
                        graph.config = self.config
                        self.graphs[key] = graph
        
            graph.addNode(node)
    
    def changeNick(self, oldNick, newNick):
        for graph in self.graphs.values():
            oldNode = Node(oldNick)
            newNode = Node(newNick)
            graph.mergeNode(oldNode, newNode)
    
    def readGraph(self, channel):
        graph = None
        try:
            strippedChannel = self.config['server'] + "-" + channel.lower()[1:]
            channelDir = os.path.join(self.config['outputDirectory'], strippedChannel)
            fn = os.path.join(channelDir, strippedChannel + "-restore.dat")
            f = open(fn, 'r')
            graph = pickle.load(f)
            f.close()
        except IOError, e:
            # couldn't load
            pass
        return graph

class Graph:
    def __init__(self, channel, config):
        self.config = config
        self.nodes = {}
        self.edges = {}
        self.minX = float("inf")
        self.maxX = float("-inf")
        self.minY = float("inf")
        self.maxY = float("-inf")
        self.maxWeight = 0
        self.label = channel
        self.caption = ""
        self.frameCount = 0
        self.lastFile = None
        self.heuristics = []
        self.heuristics.append(DirectAddressingInferenceHeuristic(self, config))
        self.heuristics.append(IndirectAddressingInferenceHeuristic(self, config))
        self.heuristics.append(AdjacencyInferenceHeuristic(self, config))
        self.heuristics.append(BinarySequenceInferenceHeuristic(self, config))
    
    def __str__(self):
        return self.label + "\nNodes: " + str([str(x) for x in self.nodes.values()]) \
            + "\nEdges:" + str([str(x) for x in self.edges.values()]) + "\n" + str(self.minX) + " " \
            + str(self.maxX) + " " + str(self.minY) + " " + str(self.maxY) \
            + " " + str(self.maxWeight) + "\n" + self.caption + "\n" \
            + str(self.frameCount)
    
    def infer(self, nick, message):
        if nick.lower() not in self.config['ignoreSet']:
            for heuristic in self.heuristics:
                heuristic.infer(nick, message)
    
    def addNode(self, node):
        if node in self.nodes.keys():
            node = self.nodes[node]
        else:
            self.nodes[node] = node
        node.weight += 1
    
    def removeNode(self, node):
        if node in self.nodes:
            del self.nodes[node]
            
            for key in self.edges.keys():
                edge = self.edges[key]
                if edge.source == node or edge.target == node:
                    del self.edges[key]
            return True
        return False    
    
    def mergeNode(self, oldNode, newNode):
        if oldNode not in self.nodes:
            return
        
        nick = newNode.nick
        
        if newNode != oldNode:
            self.removeNode(newNode)
        
        changedEdges = []
        for edge in self.edges.values():
            if edge.source == oldNode or edge.target == oldNode:
                changedEdges.append(edge)
        
        for edge in changedEdges:
            del self.edges[edge]
        
        oldNode = self.nodes[oldNode]
        del self.nodes[oldNode]
        oldNode.nick = nick
        self.nodes[oldNode] = oldNode
        
        for edge in changedEdges:
            self.edges[edge] = edge
        
        if oldNode in self.getConnectedNodes():
            # redraw
            self.makeNextImage()
    
    def addEdge(self, source, target, weight):
        if (source == target or weight <= 0):
            return False
        
        # Ensure both nodes are in the graph.
        self.addNode(source)
        self.addNode(target)
        
        edge = Edge(source, target)
        if edge in self.edges:
            edge = self.edges[edge]
        else:
            source = self.nodes[source]
            target = self.nodes[target]
            edge = Edge(source, target)
            self.edges[edge] = edge
        edge.weight += weight
        
        self.makeNextImage()
        return True
    
    def decay(self, amount):
        for key in self.edges.keys():
            edge = self.edges[key]
            edge.weight -= amount
            if edge.weight <= 0:
                del self.edges[key]
        
        for key in self.nodes.keys():
            node = self.nodes[key]
            node.weight -= amount
            if node.weight <= 0:
                node.weight = 0
    
    def getConnectedNodes(self):
        connectedNodes = set()
        for edge in self.edges.values():
            connectedNodes.add(edge.source)
            connectedNodes.add(edge.target)
        return connectedNodes
    
    def doLayout(self, iterations):
        nodes = list(self.getConnectedNodes())
        edges = self.edges.values()
        
        k = self.config['k']
        c = self.config['c']
        
        # Repulsive forces between nodes that are further apart than this are ignored.
        maxRepulsiveForceDistance = self.config['maxRepulsiveForceDistance']
        
        for i in xrange(iterations):
            # Calculate forces acting on nodes due to node-node repulsions
            for a in nodes:
                for b in nodes[nodes.index(a)+1:]:
                    deltaX = b.x - a.x
                    deltaY = b.y - a.y
                    
                    distanceSquared = deltaX ** 2 + deltaY ** 2
                    
                    if distanceSquared < 0.01:
                        deltaX = random() / 10 + 0.1
                        deltaY = random() / 10 + 0.1
                        distanceSquared = deltaX ** 2 + deltaY ** 2
                    
                    distance = math.sqrt(distanceSquared)
                    
                    if distance < maxRepulsiveForceDistance:
                        repulsiveForce = k ** 2 / distance
                        
                        b.fx += (repulsiveForce * deltaX / distance)
                        b.fy += (repulsiveForce * deltaY / distance)
                        a.fx -= (repulsiveForce * deltaX / distance)
                        a.fy -= (repulsiveForce * deltaY / distance)
            
            # Calculate forces acting on nodes due to edge attractions.
            for edge in edges:
                a = edge.source
                b = edge.target
                
                deltaX = b.x - a.x
                deltaY = b.y - a.y
                
                distanceSquared = deltaX ** 2 + deltaY ** 2
                
                if distanceSquared < 0.01:
                    deltaX = random() / 10 + 0.1
                    deltaY = random() / 10 + 0.1
                    distanceSquared = deltaX ** 2 + deltaY ** 2
                
                distance = math.sqrt(distanceSquared)
                
                if (distance > maxRepulsiveForceDistance):
                    distance = maxRepulsiveForceDistance
                
                distanceSquared = distance ** 2
                
                attractiveForce = (distanceSquared - k ** 2) / k
                
                weight = edge.weight
                if weight < 1:
                    weight = 1
                
                attractiveForce *= (math.log(weight) * 0.5) + 1
                
                b.fx = b.fx - attractiveForce * deltaX / distance
                b.fy = b.fy - attractiveForce * deltaY / distance
                a.fx = a.fx + attractiveForce * deltaX / distance
                a.fy = a.fy + attractiveForce * deltaY / distance
            
            # Now move each node to its new location...
            
            for node in nodes:
                xMovement = c * node.fx
                yMovement = c * node.fy
                
                maxNodeMovement = self.config['maxNodeMovement']
                if xMovement > maxNodeMovement:
                    xMovement = maxNodeMovement
                elif xMovement < -maxNodeMovement:
                    xMovement = -maxNodeMovement
                if yMovement > maxNodeMovement:
                    yMovement = maxNodeMovement
                elif yMovement < -maxNodeMovement:
                    yMovement = -maxNodeMovement
                
                node.x += xMovement
                node.y += yMovement
                
                node.fx = 0
                node.fy = 0
    
    def calcBounds(self, width, height):
        POS_INF = float("inf")
        NEG_INF = float("-inf")
        minX = POS_INF
        maxX = NEG_INF
        minY = POS_INF
        maxY = NEG_INF
        maxWeight = 0
        
        nodes = self.getConnectedNodes()
        for node in nodes:
            if node.x > maxX:
                maxX = node.x
            if node.x < minX:
                minX = node.x
            if node.y > maxY:
                maxY = node.y
            if node.y < minY:
                minY = node.y
        
        # Increase size if too small
        minSize = self.config['minDiagramSize']
        if (maxX - minX < minSize):
            midX = (maxX + minX) / 2
            minX = midX - (minSize / 2)
            maxX = midX + (minSize / 2)
        if (maxY - minY < minSize):
            midY = (maxY + minY) / 2
            minY = midY - (minSize / 2)
            maxY = midY + (minSize / 2)
        
        # Work out the maximum weight
        for edge in self.edges.values():
            if edge.weight > maxWeight:
                maxWeight = edge.weight
        
        # Jibble the boundaries to maintain the aspect ratio
        xyRatio = ((maxX - minX) / (maxY - minY)) / (width / height)
        if xyRatio > 1:
            # Diagram is wider than it is high
            dy = maxY - minY
            dy = dy * xyRatio - dy
            minY = minY - dy / 2
            maxY = maxY + dy / 2
        elif xyRatio < 1:
            # Diagram is higher than it is wide
            dx = maxX - minX
            dx = dx / xyRatio - dx
            minX = minX - dx / 2
            maxX = maxX + dx / 2
        
        self.minX = minX
        self.maxX = maxX
        self.minY = minY
        self.maxY = maxY
        self.maxWeight = maxWeight
    
    def drawImage(self, width, height, borderSize, nodeRadius, edgeThreshold, showEdges):
        fontDir = os.path.dirname(os.path.abspath( __file__ )) # thanks jtatum
        
        nodes = self.getConnectedNodes()
        im = Image.new("RGBA", (width, height))
        #draw = ImageDraw.Draw(im)
        # I don't want to spend time getting aggdraw's text drawing to work,
        # so I'll just shuffle between that and ImageDraw.
        draw = aggdraw.Draw(im)
        d = ImageDraw.Draw(im)
        
        #draw.rectangle([1, 1, width-2, height-2], fill=self.config['backgroundColor'])
        #draw.rectangle([0, 0, width-1, height-1], outline=self.config['borderColor'])
        p = aggdraw.Pen(self.config['borderColor'])
        b = aggdraw.Brush(self.config['backgroundColor'])
        draw.rectangle([0, 0, width-1, height-1], p, b)
        
        awidth = width - borderSize * 3
        aheight = height - borderSize * 2
        
        draw.flush()
        
        ifont = ImageFont.truetype(os.path.join(fontDir,"DejaVuSans-Bold.ttf"), 64)
        d.text([borderSize + 20, 16], self.label, font=ifont, fill=self.config['channelColor'])
        
        ifont = ImageFont.truetype(os.path.join(fontDir,"DejaVuSans-Bold.ttf"), 18)
        d.text([borderSize, borderSize - nodeRadius - 15 - 18], "A Social Network Diagram for an IRC Channel", font=ifont, fill=self.config['titleColor'])
        d.text([borderSize, aheight + borderSize * 2 - 5 - 50 - 18], self.caption, font=ifont, fill=self.config['titleColor'])
        
        ifont = ImageFont.truetype(os.path.join(fontDir,"DejaVuSans.ttf"), 12)
        d.text([borderSize, aheight+borderSize*2-5-46], "Generated by %s on %s using %s" % (self.config['nick'], self.config['server'], PieInstance.VERSION), font=ifont, fill=self.config['titleColor'])
        d.text([borderSize, aheight+borderSize*2-5-31], "Blue edge thickness and shortness represents strength of relationship", font=ifont, fill=self.config['titleColor'])
        d.text([borderSize, aheight+borderSize*2-5-16], "This frame was drawn at %s" % datetime.now(), font=ifont, fill=self.config['titleColor'])
        
        draw.fromstring(im.tostring())
        
        # Squeeze the graph in a bit nicer
        bwidth = int(width - (borderSize * 0.9) * 3)
        bheight = int(height - (borderSize * 1.2) * 2)
        
        # Draw all edges
        for edge in self.edges.values():
            if edge.weight < edgeThreshold:
                continue
            
            weight = edge.weight
            
            nodeA = edge.source
            nodeB = edge.target
            x1 = int((bwidth * (nodeA.x - self.minX) / (self.maxX - self.minX)) + borderSize)
            y1 = int((bheight * (nodeA.y - self.minY) / (self.maxY - self.minY)) + borderSize)
            x2 = int((bwidth * (nodeB.x - self.minX) / (self.maxX - self.minX)) + borderSize)
            y2 = int((bheight * (nodeB.y - self.minY) / (self.maxY - self.minY)) + borderSize)
            stroke = float(math.log(weight + 1) * 0.5) + 1
            alpha = 102 + int(153 * weight / self.maxWeight)
            edgeColor = self.config['edgeColor']
            color = (edgeColor[0], edgeColor[1], edgeColor[2], alpha)
            if showEdges:
                p = aggdraw.Pen(color, stroke)
                #draw.line([x1, y1, x2, y2], fill=color, width=stroke)
                draw.line([x1, y1, x2, y2], p)
        
        # Draw all nodes
        stroke = 2
        ifont = ImageFont.truetype(os.path.join(fontDir,"DejaVuSans.ttf"), 10)
        p = aggdraw.Pen(self.config['edgeColor'], stroke)
        b = aggdraw.Brush(self.config['nodeColor'])
        for node in nodes:
            x1 = int(bwidth * (node.x - self.minX) / (self.maxX - self.minX)) + borderSize
            y1 = int(bheight * (node.y - self.minY) / (self.maxY - self.minY)) + borderSize
            #draw.ellipse([x1 - nodeRadius, y1 - nodeRadius, x1 + nodeRadius, y1 + nodeRadius], fill=self.config['nodeColor'], outline=self.config['edgeColor'])
            draw.ellipse([x1-nodeRadius, y1-nodeRadius, x1+nodeRadius, y1+nodeRadius], p, b)
            draw.flush()
            d.text((x1+nodeRadius, y1-nodeRadius-10), node.__str__(), fill=self.config['labelColor'], font=ifont)
            draw.fromstring(im.tostring())
        
        draw.flush()
        return im
    
    def makeNextImage(self):
        self.frameCount += 1
        strippedChannel = self.config['server'] + "-" + self.label.lower()[1:]
        
        channelDir = os.path.join(self.config['outputDirectory'], strippedChannel)
        if not os.path.isdir(channelDir):
            os.makedirs(channelDir)
        
        self.doLayout(self.config['springEmbedderIterations'])
        self.calcBounds(self.config['outputWidth'], self.config['outputHeight'])
        
        try:
            im = self.drawImage(self.config['outputWidth'],
                                self.config['outputHeight'],
                                self.config['borderSize'],
                                self.config['nodeRadius'],
                                self.config['edgeThreshold'],
                                self.config['showEdges'])
            
            fn = os.path.join(channelDir, "%s-%08d.png" % (strippedChannel, self.frameCount))
            if self.config['createArchive']:
                im.save(fn)
                self.lastFile = fn
            
            fcurrent = os.path.join(channelDir, "%s-current.png" % strippedChannel)
            if self.config['createCurrent']:
                im.save(fcurrent)
                if not self.config['createArchive']:
                    self.lastFile = fn
            
            if self.config['createRestorePoints']:
                self.writeGraph()
        except Exception, e:
            print "Oh no!: " + str(e)
            raise
        
        self.decay(self.config['temporalDecayAmount'])
    
    def writeGraph(self):
        try:
            strippedChannel = self.config['server'] + "-" + self.label.lower()[1:]
            channelDir = os.path.join(self.config['outputDirectory'], strippedChannel)
            fn = os.path.join(channelDir, strippedChannel + "-restore.dat")
            f = open(fn, "w")
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
            f.close()
        except IOError, e:
            # oh well, i guess we couldn't write?
            pass

class Node:
    def __init__(self, nick):
        self.nick = nick
        self.weight = 0
        self.x = random() * 2
        self.y = random() * 2
        self.fx = 0
        self.fy = 0
    
    def __str__(self):
        return self.nick
    
    def __cmp__(self, other):
        return cmp(self.nick.lower(), other.nick.lower())
    
    def __hash__(self):
        return self.nick.lower().__hash__()

class Edge:
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.weight = 0
    
    def __str__(self):
        s = ""
        if cmp(self.source, self.target) == -1:
            s = str(self.source) + ", " + str(self.target)
        if cmp(self.source, self.target) == 0:
            s = str(self.source) + ", " + str(self.target)
        if cmp(self.source, self.target) == 1:
            s = str(self.target) + ", " + str(self.source)
        return s
    
    def __cmp__(self, other):
        n1 = cmp(self.source, other.source)
        n2 = cmp(self.target, other.target)
        n3 = cmp(self.source, other.target)
        n4 = cmp(self.target, other.source)
        if n1 == 0 and n2 == 0:
            return 0
        elif n3 == 0 and n4 == 0:
            return 0
        else:
            if n1 == -1:
                return -1
            elif n1 == 1:
                return 1
            elif n2 == -1:
                return -1
            elif n2 == 1:
                return 1
            elif n3 == -1:
                return -1
            elif n3 == 1:
                return 1
            elif n4 == -1:
                return -1
            else:
                return 1
            
    
    def __hash__(self):
        return self.source.__hash__() + self.target.__hash__()

split_regex = re.compile("([\\s\\t\\n\\r\\f\\:\\.\\(\\)\\-\\,\\/\\&\\!\\?\"\"<>]|'s)+")

class InferenceHeuristic:
    def __init__(self, graph, config):
        self.graph = graph
        self.config = config
        self.weighting = 0
        className = str(self.__class__.__name__)
        try:
            self.weighting = self.config[className]
        except Exception, e:
            print "Could not find a set weighting for %s: %s" % (className, e)
    
    def __str__(self):
        return str(self.__class__.__name)

class IndirectAddressingInferenceHeuristic(InferenceHeuristic):
    def infer(self, nick, message):
        source = Node(str(nick))
        words = split_regex.split(message)
        for word in words:
            target = Node(str(word))
            if target in self.graph.nodes:
                self.graph.addEdge(source, target, self.weighting)

class DirectAddressingInferenceHeuristic(InferenceHeuristic):
    def infer(self, nick, message):
        source = Node(str(nick))
        words = split_regex.split(message)
        target = Node(str(words[0]))
        if target in self.graph.nodes:
            self.graph.addEdge(source, target, self.weighting)

class AdjacencyInferenceHeuristic(InferenceHeuristic):
    def __init__(self, graph, config):
        InferenceHeuristic.__init__(self, graph, config)
        self.lastNick = None
    
    def infer(self, nick, message):
        if self.lastNick is not None:
            self.graph.addEdge(Node(str(nick)), Node(self.lastNick), self.weighting)
        self.lastNick = str(nick)

class BinarySequenceInferenceHeuristic(InferenceHeuristic):
    def __init__(self, graph, config):
        InferenceHeuristic.__init__(self, graph, config)
        self.nickHistory = []
    
    def infer(self, nick, message):
        self.nickHistory.append(str(nick))
        if len(self.nickHistory) > MIN_SEQ_SIZE:
            self.nickHistory = self.nickHistory[1:]
            uniqueNicks = list(set(self.nickHistory))
            if len(uniqueNicks) == 2:
                self.graph.addEdge(Node(uniqueNicks[0]), Node(uniqueNicks[1]), self.weighting)
                self.nickHistory = []