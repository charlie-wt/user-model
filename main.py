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
import printer as pt



story_name = "Six Stories Of Southampton"

num_steps = 15



# create story, reading & user
sto = imp.storyFromJSON(story_name)
reading = rd.Reading("reading-0", sto)
user = us.User("user-0")

# traverse
path = tr.traverse(sto, reading, user, dc.rand, num_steps )
pt.print_path(sto, path)

# load logs
epr = imp.pathsFromJSON(sto, "old-logs")
pt.print_log_paths(sto, epr)
