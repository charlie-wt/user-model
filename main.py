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
import traverser as tr



story_name = "Six Stories Of Southampton"

num_steps = 15



# create story, reading & user
sto = imp.storyFromJSON(story_name)
reading = rd.Reading("reading-0", sto)
user = us.User("user-0")
print("There are", len(reading.vars), "variables in the story.\n")

# traverse
tr.traverse(sto, reading, user, dc.rand, num_steps, True)

# load logs
print("\n.LOGS.")
epr = imp.pathsFromJSON(sto, "old-logs")

print("paths through story, per user:")
for u in epr.keys():
    print("reading "+u+":")
    for e in epr[u]:
        print("\t", e.date)
