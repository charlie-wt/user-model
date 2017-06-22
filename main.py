import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))
import time

import importer as imp
import ls
import reading as rd
import user as us

# create story
sto = imp.storyFromJSON("Fallen branches", [False, False, True, True, True ])

# create reading
reading = rd.Reading("reading-0", [], sto.id, "inprogress", time.time())

# create 'user'
user = us.User("user-0")

# see which pages are visible
visible = []
for p in sto.pages:
    p.update( reading.vars, sto.conditions, sto.locations, user.loc )
    if p.visible: visible.append(p)

print("Visible pages:")
for p in visible:
    print(p.name + "\t:\t" + p.id)
