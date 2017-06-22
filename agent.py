import math
import random
import graph

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
        if start == -1:
            while ( True ):
                idx = math.floor(random.random() * (len(ns)-1))
                if ( len(ns[idx].connections) > 0 ):
                    n = ns[idx]
                    break
        else:
            n = ns[start]
        self.move(n)

def traverse ( agt, fun, high=10 ):
    count = 0
    while ( count < high and len(agt.loc.connections) != 0 ):
        choice = agt.loc.connections[fun(agt.loc, agt.loc.connections)]
        agt.move(choice)
        count += 1
