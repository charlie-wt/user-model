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
    print("\n")


# load logs
logfile = open("json/old-logs.json", 'r')
logs = logfile.read()
logfile.close()
logs_json = json.loads(logs)
print("num logs:", len(logs_json))

evnt = imp.logEventFromJSON(logs_json[0])
print("Loaded log event", evnt.id, ":\n\tuser:", evnt.user, "\n\tdate:", evnt.date, "\n\ttype:", evnt.type, "\n\tdata:", evnt.data)

print()
count = 0
types = set()
for e in logs_json:
    if "data" not in e:
        count += 1
        types.add(e["type"])
print(count, "events have no data, with types:", types)

count = 0
types = set()
for e in logs_json:
    if "data" in e and "storyId" not in e["data"]:
        count += 1
        types.add(e["type"])
print(count, "event datas have no story ID, with types:", types)

events = []
for e in logs_json:
#    if "data" in e and "storyId" in e["data"] and e["data"]["storyId"] == sto.id:
    if e["type"] == "playreadingcard" and e["data"]["storyId"] == sto.id:
        events.append(imp.logEventFromJSON(e))
events.sort(key = lambda e: e.date)

# TODO - might want to do this per reading, not per user
print()
events_per_user = {}
for e in events:
    if e.user not in events_per_user:
        events_per_user[e.user] = [e]
        continue
    if e.id not in events_per_user[e.user]:
        events_per_user[e.user].append(e)

for u in events_per_user.keys():
    print("user", u)
    for e in events_per_user[u]:
        print("\t", e.date)
