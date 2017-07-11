import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import importer as imp
import reading as rd
import user as us
import decider as dc
import page
import traverser as tr
import printer as pt



story_name = "Notes on an Illegible City"

num_steps = 15



# create story, reading & user
sto = imp.storyFromJSON(story_name)
reading = rd.Reading("reading-0", sto)
user = us.User("user-0")

# traverse
path = tr.traverse(sto, reading, user, dc.guess, num_steps, True )
print("--- done ---\n")
pt.print_path(sto, path)

# load logs
#ppr = imp.pathsFromJSON("old-logs", sto)
#print("Found", len(ppr), "readings for", sto.name+".")
#path = []
#for pth in ppr.values():
#    if len(pth) > len(path): path = pth
#pages = page.fromLogEvents(sto, path)
#pt.print_path(sto, pages)
