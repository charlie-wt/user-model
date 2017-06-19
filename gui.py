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
        
        self.initUI()
    
    def initUI ( self ):
        self.parent.title("graph")
        self.pack(fill=tk.BOTH, expand=1)

    def graph ( self, graph ):
        canvsize = 495
        canv = tk.Canvas(self.top, bg="white", width=str(canvsize), height=str(canvsize))
        canv.pack()

        ns = []

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

        for i in range(0, len(graph)):
            node = graph[i]
            ns.append(Node(node.lon, node.lat, i, canv, bounds))

    def display ( self ):
        self.top.mainloop()

class Node:

    col = "green"
    size = 20

    def __init__ ( self, x, y, label, canv, bounds=() ):
        self.x = x
        self.y = y
        self.sx = x
        self.sy = y
        self.label = label
        self.canv = canv

        if ( len(bounds) == 6 ):
            self.updateSC(bounds)

        self.circle = canv.create_oval( 
                self.sx-(Node.size/2),
                self.sy-(Node.size/2),
                self.sx+(Node.size/2),
                self.sy+(Node.size/2),
                fill=Node.col)

    def updateSC ( self, bounds ):
        sc = self.screen(bounds)
        self.sx = sc[0]
        self.sy = sc[1]

    def screen ( self, bounds ):
        rx = (self.x - bounds[0]) / (bounds[1] - bounds[0]) if (bounds[1] - bounds[0]) != 0 else 0
        ry = (self.y - bounds[2]) / (bounds[3] - bounds[2]) if (bounds[3] - bounds[2]) != 0 else 0
        screenX = rx*bounds[4]
        screenY = ry*bounds[5]

        return [ screenX, screenY ]

class Edge:
    def __init__ ( self, n1, n2 ):
        self.n1 = n1
        self.n2 = n2
