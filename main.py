import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))
import time

import importer as imp
import ls
import reading as rd
import user as us

# create story, reading & user
sto = imp.storyFromJSON("Fire Fire", [False, False, True, True, True ])
reading = rd.Reading("reading-0", [], sto.id, "inprogress", time.time())
user = us.User("user-0")

print(user.loc)

# see which pages are visible
visible = []
for p in sto.pages:
    p.update( reading.vars, sto.conditions, sto.locations, user.loc )
    if p.visible: visible.append(p)

print(".VISIBLE PAGES.")
for p in visible:
    printed = False
    for cond_id in p.conditions:
        cond = ls.get(sto.conditions, cond_id)
        if cond.type == "location":
            page_loc = ls.get(sto.locations, cond.location)
            dist = imp.location.Location.metres(user.loc[0], user.loc[1], page_loc.lat, page_loc.lon)
            print(p.name + "\t:\t" + p.id + " -> " + str(dist) + " metres away.")
            printed = True
            break
    if not printed: print(p.name + "\t:\t" + p.id + ", which can be accessed from anywhere.")
