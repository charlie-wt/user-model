import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import importer as imp
import reading as rd
import user as us
import ranker as rk
import decider as dc
import page as pg
import traverser as tr
import printer as pt
import analyser as an
import ls

names = ["A Walk In The Park",                  # 0
         "Butterflies",                         # 1
         "Connections",                         # 2
         "Fallen branches",                     # 3
         "Fire Fire",                           # 4
         "Naseem - The Pharaohs Attendant",     # 5
         "Notes on an Illegible City",          # 6
         "Seeker of Secrets",                   # 7
         "Six Stories Of Southampton",          # 8
         "The Bournemouth Triangle",            # 9
         "The Destitute and The Alien",         # 10
         "The Pathways of Destiny",             # 11
         "The Tale of Molly DeVito",            # 12
         "The Titanic Criminal In Southampton"] # 13



story_name = names[11]

max_steps = 50



# create/load stuff
story = imp.storyFromJSON(story_name)
#reading = rd.Reading("reading-0", story)
#user = us.User("user-0")
paths_per_reading = imp.pathPagesFromJSON("old-logs", story)

# traverse
sim_store = tr.traverse(story, rk.guess, dc.best, max_steps)
sim_path = [ r.page for r in sim_store ]
#tr.reset(story, reading, user)

# load logs
log_store = an.walk(story, paths_per_reading, max_steps)
log_path = [ r.page for r in log_store ]

# analyse paths
an.path_similarity(story, sim_store, log_store, True)
#total_visits = an.page_visits_many(story, 10, 50, True)
#an.get_unreachables(story, True)
#an.distance_travelled(story, log_store, True)
#pt.print_pages(log_path, story)
stores = tr.traverse_many(story)
#an.page_visits(story, stores, True)
an.distance_travelled(story, stores, True)
an.distance_travelled(story, log_store, True)
