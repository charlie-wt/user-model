import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

from collections import defaultdict

import location as lc
import page as pg
import record as rc
import ls

'''
printer

functions for printing various bits of info, to keep the main code clean.
'''

def print_story ( story, reading=None ):
    ''' print basic story info. '''
    print("'"+story.name+"' is story", story.id, "and contains", len(story.pages), "pages,", len(story.conditions), "conditions,", len(story.functions), "functions", end="")
    if reading is not None:
        print(",", len(story.locations), "locations &", len(reading.vars), "variables.")
    else:
        print(" &", len(story.locations), "locations.")

def print_user_state ( user ):
    ''' print where the user is in the story. '''
    print("user is now at page '"+user.page().name+"',",
          "and is at location ("+str(user.lat())+", "+str(user.lon())+").")

def print_visible ( vis, story, us=None ):
    ''' print the list of visible pages in a story. '''
    print("\tvisible pages:")
    for p in vis:
        page_loc = p.get_loc(story)
        print("\t" + p.id + " : " + p.name, end="")
        if us is not None:
            if page_loc is not None:
                dist = lc.metres(us.loc, page_loc)
                print(" -> " + str(int(dist)) + " metres away.")
            else:
                print(", which can be accessed from anywhere.")
        else:
            print(".")

def print_all_paths ( stores, story=None, print_id=False ):
    ''' print all the paths taken through a story. '''
    if story is not None: print('all', len(stores), 'paths through', story.name+':')
    for path in stores:
        print('---------------------------------------------------')
        print_pages(path, print_id=print_id)

def print_pages ( pages, story=None, print_id=False ):
    ''' print a bunch of pages. '''
    if type(pages[0]) == rc.Record: pages = [ r.page for r in pages ]
    if story is not None: print("path through", story.name+":")
    for p in pages: print((p.id+" : " if print_id else "") + \
                          (p.name if type(p) is pg.Page else "---"))

def print_paths_per_reading ( story, paths_per_reading ):
    ''' print paths per reading, as output by log importer. '''
    ppr = paths_per_reading
    print("Paths through "+story.name+", for", len(ppr), "readings:")
    for r in ppr.keys():
        print("reading "+r+":")
        for p in ppr[r]:
            print("\t", p.id, ":", p.name)

def print_events_per_reading ( story, events_per_reading ):
    ''' print the paths of events taken through a story by a real user. '''
    epr = events_per_reading
    if len(epr) is 0: return
    legacy = False
    for r in epr:
        if "cardId" in epr[r][0].data:
            legacy = True
        break
    page_id = "cardId" if legacy else "pageId"
    page_name = "cardLabel" if legacy else "pageName"

    print("Paths through "+story.name+", for, ", len(epr), "readings:")
    for r in epr:
        print('reading '+r+':')
        for pg in epr[r]:
            page = ls.get(story.pages, pg.data[page_id])
            print(pg.date, ":", pg.data[page_id], ": ", end="")
            if page is not None:
                print(page.name)
            else:
                print(pg.data[page_name], "("+pg.data[page_id]+")", "(NOT FOUND)")

def print_page_ranking ( pages, probs ):
    ''' print pages & their probabilities. Assumes desired ordering. '''
    print("Page rankings:")
    for i in range(len(pages)):
        print(pc(probs[i]), ":", pages[i].name)
    print("---")

def print_options ( options, page ):
    ''' similar to print_page_ranking, but takes an options dictionary and
    deals with the end case - for use by functions in analyser.py.
    '''
    pname = page.name if page is not None else "---"
    print("Options from "+pname+":")
    for p in options:
        name = "--End--"
        if type(p) == pg.Page: name = p.name
        print("\t"+pc(options[p]), ":", name)

def print_store ( store ):
    ''' print the path taken with choice probabilities, via a store (list of
    records).
    '''
    for r in store:
        print_options(r.options, r.page)

def print_walk_full_options ( visible, options, allow_quitting ):
    ''' print visible pages, options taken by users and their intersection
    for use during log traversals).
    '''
    print("popularity of pages:\n\tvisible:")
    for p in visible:
        amount = 0
        for o in options.keys():
            if type(o) != int and o.name == p.name:
                amount = options[o]
                break
        print("\t\t"+p.name, ":", pc(amount))
    if allow_quitting and 0 in options:
        print("\t\t--Quit-- :", pc(options[0]))
    not_allowed = "\tnot visible:" if allow_quitting else "\tnot visible/quit:"
    print(not_allowed)
    for o in options.keys():
        if not allow_quitting and type(o) == int:
            print("\t\t--Quit-- :", pc(options[o]))
        elif o not in visible and type(o) != int:
            print("\t\t"+o.name, pc(options[o]))

def print_sim_log_comparison ( sim_path, log_path ):
    ''' compare the paths taken by a simulation and a log traversal. '''
    if type(sim_path[0]) == rc.Record: sim_path = [ r.page for r in sim_path ]
    if type(log_path[0]) == rc.Record: log_path = [ r.page for r in log_path ]
    print("-------------------------------------------------------------------")
    print("sim                               log")
    print("-------------------------------------------------------------------")
    for i in range(max(len(sim_path), len(log_path))):
        s_name = "---"
        if i < len(sim_path) and sim_path[i] is not None:
            s_name = sim_path[i].name
        l_name = "---"
        if i < len(log_path) and log_path[i] is not None:
            l_name = log_path[i].name

        left_pad = 34 - len(s_name)
        print(s_name + " "*left_pad + l_name)

def print_cache ( cache ):
    ''' print a cache, currently with max depth of two elements between type &
    value.
    '''
    for t in cache:
        for elem in cache[t]:
            if type(cache[t][elem]) is defaultdict:
                for elem2 in cache[t][elem]:
                    print('\t', t, ':', elem, ':', elem2, ':', cache[t][elem][elem2])
            else:
                print('\t', t, ':', elem, ':', cache[t][elem])

def pc ( num, dec=0 ):
    ''' percentify a 0-1 fraction. '''
    if dec > 0: dec += 1
    percent = str(num*100)
    rounded = percent+"%"
    if "." in percent and dec != -1:
        rounded = percent[:percent.index(".")+dec]+"%"
    return " "+rounded if num < 0.1 else rounded

def fmt ( num, dec=0, suf=''):
    ''' round a number to dec decimal places, return string with suf suffix. '''
    if dec > 0: dec += 1
    stnum = str(num)
    rounded = stnum + suf
    if '.' in stnum and dec != -1: rounded = stnum[:stnum.index('.')+dec] + suf
    return rounded

def truncate ( word, length=16, ellipses=True ):
    ''' truncate a word to a certain length. '''
    shortened = word[:length]
    if ellipses and len(word) > length:
        shortened = shortened[:-3] + '...'
    return shortened
