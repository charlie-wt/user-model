import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))
import time

import importer as imp
import ls
import reading as rd
import user as us
import decider as dc
import page

# create story, reading & user
sto = imp.storyFromJSON("Naseem Formatted", [False, False, False, False, True ])
reading = rd.Reading("reading-0", [], sto, "inprogress", time.time())
user = us.User("user-0")

print(len(reading.vars), "variables in the story.\n")

# see which pages are visible
visible = page.update_all(sto.pages, sto, reading, user)

def print_visible ():
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
print_visible()

# move to a page
print("\n.MOVEMENT.")
move_to_idx = dc.rand(None, visible)
visible = user.move(move_to_idx, visible, sto, reading)
print("user is now at page '" + user.page().name + "', and is at location (" + str(user.loc[0]) + ", " + str(user.loc[1]) + ").")
print("active variables:")
for v in reading.vars:
    if v.value is not None:
        print(v.id, "=", v.value)
print()
print_visible()
