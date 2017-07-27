import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import importer as imp
import ranker as rk
import decider as dc
import traverser as tr
import printer as pt
import analyser as an
import ls
import gui

names = ["A Walk In The Park",                  #  0
         "Butterflies",                         #  1
         "Connections",                         #  2
         "Fallen branches",                     #  3
         "Fire Fire",                           #  4
         "Naseem - The Pharaohs Attendant",     #  5
         "Notes on an Illegible City",          #  6
         "Seeker of Secrets",                   #  7
         "Six Stories Of Southampton",          #  8
         "The Bournemouth Triangle",            #  9
         "The Destitute and The Alien",         # 10
         "The Pathways of Destiny",             # 11
         "The Tale of Molly DeVito",            # 12
         "The Titanic Criminal In Southampton"] # 13



story_name = names[13]

max_steps = 50



# create/load stuff
story = imp.storyFromJSON(story_name)
paths_per_reading = imp.pathPagesFromJSON("old-logs", story, True, True)

# traverse
sim_store = tr.traverse(story, rk.guess, dc.best, max_steps)
sim_path = [ r.page for r in sim_store ]

# load logs
log_store = an.walk(story, paths_per_reading, max_steps)
log_path = [ r.page for r in log_store ]

# analyse paths
pt.print_sim_log_comparison(sim_path, log_path)
an.path_similarity(story, sim_store, log_store, True)
err = tr.step_predict(story, log_store, rk.guess, True)

stores = tr.traverse_many(story, 100)
an.branching_factor(story, stores, True)
an.distance_travelled(story, stores, True)
an.get_unreachables(story, stores, True)
#gui.visit_proportions(an.most_visited(story, stores), 'tory', story)
#gui.visit_proportions(an.log_most_visited(story, paths_per_reading), 'story', story)
gui.show_info(story, paths_per_reading, stores, sim_store, log_store, err)
