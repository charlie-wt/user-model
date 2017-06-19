import math

import tkinter as tk
import graph as gr
import agent as ag

class Window (tk.Frame):
    def __init__ ( self, graph ):
        self.top = tk.Tk()
        self.top.geometry("500x500")
        
        tk.Frame.__init__(self, self.top)
        
        self.parent = self.top
        
        self.parent.title("graph")
        self.pack(fill=tk.BOTH, expand=1)
        
        self.graph = Graph(graph, self.top)

    def display ( self ):
        self.top.mainloop()

class Graph:
    def __init__ ( self, graph, parent ):
        # variables
        self.canvsize = 495
        self.canv = tk.Canvas(parent, bg="white", width=str(self.canvsize), height=str(self.canvsize))
        self.ns = []
        self.es = []
        self.highlight = 0
        self.margin = 50
        self.graph = graph

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
                    if i == self.highlight: edge.highlighted = True
                    self.es.append(edge)
                    edge.draw()

        # add nodes
        for i in range(0, len(self.graph)):
            node = self.graph[i]
            self.ns.append(Node(node.lon, node.lat, i, self.canv, self.bounds))
            if i == self.highlight: self.ns[len(self.ns)-1].highlighted = True
            self.ns[len(self.ns)-1].draw()
        
    def redraw ( self ):
        for i in range(0, len(self.es)):
            self.es[i].highlighted = True if i == self.highlight else False
            self.es[i].draw()
        for i in range(0, len(self.ns)):
            self.ns[i].highlighted = True if i == self.highlight else False
            self.ns[i].draw()

def screen ( x, y, bounds ):
# Convert lat/lon coords to screen coords with bounds = ( xmin, xmax, ymin, ymax, canvwidth, canvheight )
    rx = (x - bounds[0]) / (bounds[1] - bounds[0]) if (bounds[1] - bounds[0]) != 0 else 0
    ry = (y - bounds[2]) / (bounds[3] - bounds[2]) if (bounds[3] - bounds[2]) != 0 else 0
    screenX = rx*bounds[4]
    screenY = ry*bounds[5]

    return [ screenX, screenY ]

def dist ( p0, p1 ):
    return math.sqrt((p1[0] - p0[0])**2 + (p1[1] - p0[1])**2)

class Node:
    ncol = "green"
    hcol = "blue"
    tcol = "white"
    highlighted = False
    size = 20

    def __init__ ( self, x, y, label, canv, bounds ):
        self.x = x
        self.y = y
        sc = screen(self.x, self.y, bounds)
        self.sx = sc[0]
        self.sy = sc[1]
        self.label = label
        self.canv = canv
        self.circle = None
        self.text = None
        
    def draw ( self ):
        col = Node.hcol if self.highlighted else Node.ncol
        self.circle = self.canv.create_oval( 
                self.sx-(Node.size/2),
                self.sy-(Node.size/2),
                self.sx+(Node.size/2),
                self.sy+(Node.size/2),
                fill=col)
        self.text = self.canv.create_text(self.sx, self.sy, text=str(self.label), fill=Node.tcol)

class Edge:
    ncol = "black"
    hcol = "blue"
    highlighted = False
    
    def __init__ ( self, n1, n2, canv, bounds ):
        self.n1 = n1
        self.n2 = n2
        self.bounds = bounds
        self.p0 = screen(n1.lon, n1.lat, bounds)
        self.p1 = screen(n2.lon, n2.lat, bounds)
        self.canv = canv
        
    def draw ( self ):
        col = Edge.hcol if self.highlighted else Edge.ncol
        self.line = self.canv.create_line(self.p0[0], self.p0[1], self.p1[0], self.p1[1], fill=col)
        self.text = self.canv.create_text(
                self.p0[0] + (self.p1[0] - self.p0[0])/2,
                self.p0[1] + (self.p1[1] - self.p0[1])/2,
                text=str(round(dist([self.n1.lon, self.n1.lat], [self.n2.lon, self.n2.lat]))),
                fill=col)
