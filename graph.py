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
            if( (new not in self.connections) and (self not in new.connections) ):
                self.connections.append(new)
            self.gencons(ns, i+1)
        else:
            self.genned = True

def dist ( n1, n2 ):
    return math.sqrt((n2.lat - n1.lat)**2 + (n2.lon - n1.lon)**2)

# Create & fill list of nodes
ns = []
for i in range (0, 10):
    ns.append(Node([]))

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
gengraph(ns, 0)

# Print graph
def printcons ( ns, i ):
    idxs = []
    for n in ns[i].connections:
        idxs.append(ns.index(n))
    print("[", i, "] ->", idxs)

def printgraph ( ns ):
    for i in range (0, len(ns)-1):
        printcons(ns, i)

print("-- GRAPH --")
printgraph(ns)
msg = "Num connections: [ "
for n in ns:
    msg += str(len(n.connections))
    msg += " "
msg += "]"
print("                   0 1 2 3 4 5 6 7 8 9")
print(msg)

# Define agent to travel through graph
class Agent:
    def __init__ ( self, ns=[], start=-1 ):
        self.path = []
        self.loc = None
        self.start(ns, start)

    def move ( self, n ):
        self.loc = n
        self.path.append(self.loc)

    def start ( self, ns, start=-1 ):
        if ( ns == [] ): return
        n = ns[start]
        if start == -1:
            while ( True ):
                idx = math.floor(random.random() * (len(ns)-1))
                if ( len(ns[idx].connections) > 0 ):
                    n = ns[idx]
                    break
        self.move(n)

agt = Agent(ns, 0)

# Traverse the graph randomly until the agent gets stuck or max steps reached
def traverse ( agt, high=10 ):
    count = 0
    while ( count < high and len(agt.loc.connections) != 0 ):
        choices = len(agt.loc.connections)
        choice = agt.loc.connections[math.floor(random.random() * choices)]
        agt.move(choice)
        count += 1
traverse(agt)

# Print path
msg = ""
c = 0
for n in agt.path:
    msg += ( "_" if n == None else str(ns.index(n)))
    if ( c == 10 and len(agt.loc.connections) != 0 ):
        msg += " ... "
    elif ( c != (len(agt.path)-1) ):
        msg += " -> "
    c += 1
print("\n-- PATH --")
print(msg)

d = dist(ns[0], ns[1])
print("dist from (", ns[0].lat, ",", ns[0].lon, ") to (", ns[1].lat, ",", ns[1].lon, ") is", d)
