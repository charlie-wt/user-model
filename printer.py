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
    print()

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
            dist = lc.metres(us.lat(), us.lon(), page_loc[0], page_loc[1])
            print("\t", p.name + "\t:\t" + p.id + " -> " + str(dist) + " metres away.")
        else:
            print("\t", p.name + "\t:\t" + p.id + ", which can be accessed from anywhere.")

def print_path ( story, path ):
# print the pages in a path
    print("Path through "+story.name+":")
    for p in path: print(p.name)
    print()

def print_log_paths ( story, paths ):
# print paths per reading, as output by log importer
    print("Paths through "+story.name+", per reading:")
    for r in paths.keys():
        print("reading "+r+":")
        for e in paths[r]:
            print("\t", e.date)
    print()

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
    print()

def print_page_ranking ( pages, probs ):
# print pages & their probabilities. Assumes desired ordering.
    print("Page rankings:")
    for i in range(0, len(pages)):
        percent = int(probs[i] * 100)
        print(pages[i].name, ":", str(percent)+"%")
    print("---")

def print_options ( options, page ):
# similar to print_page_ranking, but takes an options dictionary and deals with
# the end case - for use by functions in analyser.py
    print("Options from "+page.name+":")
    for p in options:
        name = "--End--"
        if type(p) != int: name = p.name
        percent = int(options[p] * 100)
        print(name, ":", str(percent)+"%")
