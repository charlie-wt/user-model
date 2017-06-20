import graph as gr
import agent as ag
import decide as dc
import gui

# Create nodes
ns = []
for i in range (0, 10):
    ns.append(gr.Node([]))

# Link edges to make graph
gr.gengraph(ns, 0)

# Print graph info
print("-- GRAPH --")
gr.printgraph(ns)
msg = "Num connections: [ "
for n in ns:
    msg += str(len(n.connections))
    msg += " "
msg += "]"
print("                   0 1 2 3 4 5 6 7 8 9")
print(msg)

# Create agent
agt = ag.Agent(ns, 0)

# Traverse graph
ag.traverse(agt, dc.distance)

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

print("\n-- GUI --")
window = gui.Window(ns, agt)
window.display()
