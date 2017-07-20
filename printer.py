import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import location as lc
import ls

##### printer ################
# functions for printing various bits of info, to keep the main code clean.
##############################

def print_story ( story, reading=None ):
# print basic story info
    print("'"+story.name+"' is story", story.id, "and contains", len(story.pages), "pages,", len(story.conditions), "conditions,", len(story.functions), "functions", end="")
    if reading is not None:
        print(",", len(story.locations), "locations &", len(reading.vars), "variables.")
    else:
        print(" &", len(story.locations), "locations.")

def print_user_state ( user ):
# print where the user is in the story
    print("user is now at page '"+user.page().name+"',",
          "and is at location ("+str(user.lat())+", "+str(user.lon())+").")

def print_visible ( vis, story, us ):
# print the list of visible pages in a story
    print("\tvisible pages:")
    for p in vis:
        page_loc = p.getLoc(story)
        if page_loc is not None:
#            dist = lc.metres(us.lat(), us.lon(), page_loc[0], page_loc[1])
            dist = lc.metres(us.loc, page_loc)
            print("\t" + p.id + " : " + p.name + " -> " + str(dist) + " metres away.")
        else:
            print("\t" + p.id + " : " + p.name + ", which can be accessed from anywhere.")

def print_pages ( pages, print_id=False, story=None ):
# print a bunch of pages
    if story is not None: print("path through", story.name+":")
    for p in pages: print((p.id+" : " if print_id else "") + p.name)

def print_log_paths ( story, paths ):
# print paths per reading, as output by log importer
    print("Paths through "+story.name+", per reading:")
    for r in paths.keys():
        print("reading "+r+":")
        for e in paths[r]:
            print("\t", e.date)

def print_event_path ( story, path ):
# print the path of events taken through a story by a real user
    if len(path) is 0: return

    print("Path taken by user through "+story.name+":")
    for pg in path:
        page = ls.get(story.pages, pg.data["cardId"])
        print(pg.date, ":", pg.data["cardId"], ": ", end="")
        if page is not None:
            print(page.name)
        else:
            print(pg.data["cardLabel"], "("+pg.data["cardId"]+")", "(NOT FOUND)")

def print_page_ranking ( pages, probs ):
# print pages & their probabilities. Assumes desired ordering.
    print("Page rankings:")
    for i in range(len(pages)):
        print(pc(probs[i]), ":", pages[i].name)
    print("---")

def print_options ( options, page ):
# similar to print_page_ranking, but takes an options dictionary and deals with
# the end case - for use by functions in analyser.py
    print("Options from "+page.name+":")
    for p in options:
        name = "--End--"
        if type(p) != int: name = p.name
        print(pc(options[p]), ":", name)

def pc ( num ):
# percentify a 0-1 fraction
    p = str(int(num*100))+"%"
    return " "+p if num < 0.1 else p

def print_walk_full_options ( visible, options ):
# print visible pages, options taken by users and their intersection (for use
# during analysis walks).
    print("popularity of pages:\n\tvisible:")
    for p in visible:
        amount = 0
        for o in options.keys():
            if type(o) != int and o.name == p.name:
                amount = options[o]
                break
        print("\t\t"+p.name, ":", pc(amount))
    print("\tnot visible/quit:")
    for o in options.keys():
        if type(o) == int:
            print("\t\t--Quit-- :", pc(options[o]))
        elif o not in visible:
            print("\t\t"+o.name, pc(options[o]))

def print_sim_log_comparison ( sim_path, log_path ):
# compare the paths taken by a simulation, and an analysis walk
    print("-------------------------------------------------------------------")
    print("sim                               log")
    print("-------------------------------------------------------------------")
    for i in range(max(len(sim_path), len(log_path))):
        s_name = sim_path[i].name if i < len(sim_path) else "---"
        l_name = log_path[i].name if i < len(log_path) else "---"

        left_pad = 34 - len(s_name)
        print(s_name + " "*left_pad + l_name)
