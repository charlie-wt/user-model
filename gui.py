import math

import tkinter as tk
import graph as gr
import agent as ag

class Window (tk.Frame):
    def __init__ ( self, graph, agt ):
        self.top = tk.Tk()
        self.top.geometry("500x500")
        
        tk.Frame.__init__(self, self.top)
        
        self.parent = self.top
        
        self.parent.title("graph")
        self.pack(fill=tk.BOTH, expand=1)
        
        self.graph = Graph(graph, agt, self.top)
        self.focus_set()
        self.bind("<Key>", self.graph.key)
    

    def display ( self ):
        self.top.mainloop()

class Graph:
    def __init__ ( self, graph, agt, parent ):
        # variables
        self.canvsize = 495
        self.canv = tk.Canvas(parent, bg="white", width=str(self.canvsize), height=str(self.canvsize))
        self.ns = []
        self.es = []
        self.progress = 0
        self.current = 0
        self.margin = 50
        self.graph = graph
        self.agt = agt

        self.canv.pack()

        # get coordinate bounds
        xmin = self.graph[0].lon
        xmax = self.graph[0].lon
        ymin = self.graph[0].lat
        ymax = self.graph[0].lat

        for n in graph:
            xmin = n.lon if n.lon < xmin else xmin
            xmax = n.lon if n.lon > xmax else xmax
            ymin = n.lon if n.lon < ymin else ymin
            ymax = n.lon if n.lon > ymax else ymax

        self.bounds = (
                xmin-self.margin,
                xmax+self.margin,
                ymin-self.margin,
                ymax+self.margin,
                self.canvsize,
                self.canvsize)

        # generate graph
        self.gen()

    def gen ( self ):
    # Draw the nodes & edges that make up the graph
        # add edges
        for i in range(0, len(self.graph)):
            node = self.graph[i]
            for con in node.connections:
                edge = Edge(node, con, self.canv, self.bounds)

                # avoid duplicate edges
                # TODO - necessary? takes up time
                new = True
                for e in self.es:
                    if (e.n1 == edge.n1 and e.n2 == edge.n2) or (e.n1 == edge.n2 and e.n2 == edge.n1):
                        new = False
                if new:
                    self.es.append(edge)
                    edge.draw()

        # add nodes
        for i in range(0, len(self.graph)):
            node = self.graph[i]
            self.ns.append(Node(node, i, self.canv, self.bounds))
            if i == self.current: self.ns[len(self.ns)-1].highlighted = True
            self.ns[len(self.ns)-1].draw()
        
    def redraw ( self ):
        # edges
        for i in range(0, len(self.es)):
            # hightlighthing
            if self.es[i].n1 in self.agt.path[0:self.progress] and self.es[i].n2 in self.agt.path[0:self.progress+1]:
                self.es[i].history = True
            else:
                self.es[i].history = False

            # draw edge
            self.es[i].draw()

        # nodes
        for i in range(0, len(self.ns)):
            # highlighting
            self.ns[i].highlighted = True if i == self.current else False

            if self.ns[i].node in self.agt.path[0:self.progress]:
                self.ns[i].history = True
            else:
                self.ns[i].history = False

            # draw node
            self.ns[i].draw()

    def key ( self, event ):
    # step forward/backward through the pathfinding
        if event.keysym == "Left":
            self.progress = max(self.progress - 1, 0)
            self.current = self.graph.index(self.agt.path[self.progress])
            self.redraw()
            return
        if event.keysym == "Right":
            self.progress = min(self.progress + 1, len(self.agt.path)-1)
            self.current = self.graph.index(self.agt.path[self.progress])
            self.redraw()
            return

def screen ( x, y, bounds ):
# Convert lat/lon coords to screen coords with bounds = ( xmin, xmax, ymin, ymax, canvwidth, canvheight )
    rx = (x - bounds[0]) / (bounds[1] - bounds[0]) if (bounds[1] - bounds[0]) != 0 else 0
    ry = (y - bounds[2]) / (bounds[3] - bounds[2]) if (bounds[3] - bounds[2]) != 0 else 0
    screenX = rx*bounds[4]
    screenY = ry*bounds[5]

    return [ screenX, screenY ]

def dist ( p0, p1 ):
# distance between two points
    return math.sqrt((p1[0] - p0[0])**2 + (p1[1] - p0[1])**2)

class Node:
# stuff needed to draw a node of the graph
    default_col = "green"
    history_col = "blue"
    highlight_col = "red"
    text_col = "white"
    history = False
    highlighted = False
    size = 20

    def __init__ ( self, node, label, canv, bounds ):
        self.node = node
        self.x = node.lon
        self.y = node.lat
        self.screen_coords = screen(self.x, self.y, bounds)
        self.label = label
        self.canv = canv
        self.circle = None
        self.text = None
        
    def draw ( self ):
        col = Node.default_col
        if self.highlighted: col = Node.highlight_col
        elif self.history: col = Node.history_col
        self.circle = self.canv.create_oval( 
                self.screen_coords[0]-(Node.size/2),
                self.screen_coords[1]-(Node.size/2),
                self.screen_coords[0]+(Node.size/2),
                self.screen_coords[1]+(Node.size/2),
                fill=col)
        self.text = self.canv.create_text(
                self.screen_coords[0],
                self.screen_coords[1],
                text=str(self.label),
                fill=Node.text_col)

class Edge:
# stuff needed to draw an edge of the graph
    default_col = "black"
    history_col = "blue"
    history = False
    
    def __init__ ( self, n1, n2, canv, bounds ):
        self.n1 = n1
        self.n2 = n2
        self.bounds = bounds
        self.p0 = screen(n1.lon, n1.lat, bounds)
        self.p1 = screen(n2.lon, n2.lat, bounds)
        self.canv = canv
        
    def draw ( self ):
        col = Edge.history_col if self.history else Edge.default_col
        self.line = self.canv.create_line(self.p0[0], self.p0[1], self.p1[0], self.p1[1], fill=col)
        self.text = self.canv.create_text(
                self.p0[0] + (self.p1[0] - self.p0[0])/2,
                self.p0[1] + (self.p1[1] - self.p0[1])/2,
                text=str(round(dist([self.n1.lon, self.n1.lat], [self.n2.lon, self.n2.lat]))),
                fill=col)
