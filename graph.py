import random
import math

# Define node class
class Node:
    def __init__ ( self, connections, lat=None, lon=None ):
        self.connections = connections
        self.genned = False
        self.lat = ((random.random()*180)-90  if lat == None else lat)
        self.lon = ((random.random()*360)-180 if lon == None else lon)

    def gencons ( self, ns, i=0 ):
        if ( self.genned ): return
        chance = max(0, 0.75 - (i/20))
        if ( random.random() < chance):
            new = ns[math.floor(random.random() * (len(ns)-1))]
            if ( (new not in self.connections) and (self not in new.connections) ):
                self.connections.append(new)
            self.gencons(ns, i+1)
        else:
            self.genned = True

def dist ( n1, n2 ):
    return math.sqrt((n2.lat - n1.lat)**2 + (n2.lon - n1.lon)**2)

# Define edges of graph
def gengraph (ns, start=-1, i=0):
    if ( start != -1 ):
        while ( len(ns[start].connections) == 0 ):
            ns[start].genned = False
            ns[start].gencons(ns)
        gengraph(ns, -1, i)
    else:
        ns[i].gencons(ns)

        for n in ns[i].connections:
            if not n.genned:
                gengraph(ns, start, ns.index(n))

# Print graph
def printcons ( ns, i ):
    idxs = []
    for n in ns[i].connections:
        idxs.append(ns.index(n))
    print("[", i, "] ->", idxs)

def printgraph ( ns ):
    for i in range (0, len(ns)-1):
        printcons(ns, i)
