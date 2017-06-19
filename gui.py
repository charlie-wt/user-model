import math

import tkinter as tk
import graph as gr
import agent as ag

class Window (tk.Frame):
    def __init__ ( self ):
        self.top = tk.Tk()
        self.top.geometry("500x500")
        
        tk.Frame.__init__(self, self.top)
        
        self.parent = self.top
        
        self.canv = None
        self.ns = []
        self.es = []
        
        self.parent.title("graph")
        self.pack(fill=tk.BOTH, expand=1)

    def graph ( self, graph ):
    # Draw the nodes & edges that make up the graph
        canvsize = 495
        canv = tk.Canvas(self.top, bg="white", width=str(canvsize), height=str(canvsize))
        canv.pack()

        # get coordinate bounds
        xmin = graph[0].lon
        xmax = graph[0].lon
        ymin = graph[0].lat
        ymax = graph[0].lat

        for n in graph:
            xmin = n.lon if n.lon < xmin else xmin
            xmax = n.lon if n.lon > xmax else xmax
            ymin = n.lon if n.lon < ymin else ymin
            ymax = n.lon if n.lon > ymax else ymax

        margin = 50
        bounds = (xmin-margin, xmax+margin, ymin-margin, ymax+margin, canvsize, canvsize)

        # add edges
        for i in range(0, len(graph)):
            node = graph[i]
            for con in node.connections:
                edge = Edge(node, con, canv, bounds)

                # avoid duplicate edges
                # TODO - necessary? takes up time
                new = True
                for e in self.es:
                    if (e.n1 == edge.n1 and e.n2 == edge.n2) or (e.n1 == edge.n2 and e.n2 == edge.n1):
                        new = False
                if new:
                    self.es.append(Edge(node, con, canv, bounds))

        # add nodes
        for i in range(0, len(graph)):
            node = graph[i]
            self.ns.append(Node(node.lon, node.lat, i, canv, bounds))

    def display ( self ):
        self.top.mainloop()

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
    tcol = "white"
    size = 20

    def __init__ ( self, x, y, label, canv, bounds ):
        self.x = x
        self.y = y
        sc = screen(self.x, self.y, bounds)
        self.sx = sc[0]
        self.sy = sc[1]
        self.label = label
        self.canv = canv
        self.circle = canv.create_oval( 
                self.sx-(Node.size/2),
                self.sy-(Node.size/2),
                self.sx+(Node.size/2),
                self.sy+(Node.size/2),
                fill=Node.ncol)
        self.text = canv.create_text(self.sx, self.sy, text=str(label), fill=Node.tcol)

class Edge:
    ncol="black"
    
    def __init__ ( self, n1, n2, canv, bounds ):
        self.n1 = n1
        self.n2 = n2
        self.bounds = bounds
        self.p0 = screen(n1.lon, n1.lat, bounds)
        self.p1 = screen(n2.lon, n2.lat, bounds)
        self.line = canv.create_line(self.p0[0], self.p0[1], self.p1[0], self.p1[1], fill=Edge.ncol)
        self.text = canv.create_text(
                self.p0[0] + (self.p1[0] - self.p0[0])/2,
                self.p0[1] + (self.p1[1] - self.p0[1])/2,
                text=str(round(dist([n1.lon, n1.lat], [n2.lon, n2.lat]))),
                fill=Edge.ncol)
