import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))
import time
import json

import importer as imp
import ls
import reading as rd
import user as us
import decider as dc
import page
import logevent as le



story_name = "Six Stories Of Southampton"

num_steps = 15



def print_visible ( vis, story, us ):
# print the list of visible pages
    for p in vis:
        page_loc = p.getLoc(story)
        if page_loc is not None:
            dist = imp.location.Location.metres(us.lat(), us.lon(), page_loc[0], page_loc[1])
            print("\t", p.name + "\t:\t" + p.id + " -> " + str(dist) + " metres away.")
        else:
            print("\t", p.name + "\t:\t" + p.id + ", which can be accessed from anywhere.")

# create story, reading & user
sto = imp.storyFromJSON(story_name)
reading = rd.Reading("reading-0", sto)
user = us.User("user-0")
print("There are", len(reading.vars), "variables in the story.\n")

# see which pages are visible
visible = page.update_all(sto.pages, sto, reading, user)

# move to a page
print("\n.MOVEMENT.")
for i in range(0, num_steps):
    # move to a new page
    move_to_idx = dc.rand(user, sto, visible)
#    move_to_idx = dc.dist(user, sto, visible)
    visible = user.move(move_to_idx, visible, sto, reading)

    # print stuff
    print("user is now at page '" + user.page().name + "', and is at location (" + str(user.lat()) + ", " + str(user.lon()) + ").")
    print("\tvisible pages:")
    print_visible(visible, sto, user)

    # stop if you can't go anywhere
    if len(visible) == 0: break
    print()


# load logs
print("\n.LOGS.")
logfile = open("json/old-logs.json", 'r')
logs = logfile.read()
logfile.close()
logs_json = json.loads(logs)

events = []
for e in logs_json:
    if e["type"] == "playreadingcard" and e["data"]["storyId"] == sto.id:
        events.append(imp.logEventFromJSON(e))
events.sort(key = lambda e: e.date)

events_per_reading = {}
for e in events:
    if e.data["readingId"] not in events_per_reading:
        events_per_reading[e.data["readingId"]] = [e]
        continue
    if e.id not in events_per_reading[e.data["readingId"]]:
        events_per_reading[e.data["readingId"]].append(e)

print("paths through story, per user:")
for u in events_per_reading.keys():
    print("reading "+u+":")
    for e in events_per_reading[u]:
        print("\t", e.date)
