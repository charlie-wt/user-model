import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import json
import csv
import page as pg

##### exporter ###############
# functions to export a bunch of the program's data structures & outputs to csv.
##############################

def pathsPerReadingToCSV ( ppr, filename='mypaths_per_reading', prnt=False ):
# export a paths per reading dictionary. Not totally useful when the user logs
# exist as well, but there you go.
# format:
#   reading1.id, reading1.page1.id, ..., reading1.pagen.id
#                            ...
#   readingn.id, readingn.page1.id, ..., readingn.pagen.id
    filename = clip_filename(filename, 'csv')
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for r in ppr:
            row = [r]
            for page in ppr[r]:
                row.append(page_id(page))
            writer.writerow(row)

    if prnt: print('wrote paths for', len(ppr), 'reading'+ \
            ('s' if len(ppr) > 1 else ''), 'to', str(filename)+'.csv')

def pathsToCSV ( stores, filename='mypaths', prnt=False ):
# export lists of pages
# format:
#   path1.page1.id, ..., path1.pagen.id
#                   ...
#   pathn.page1.id, ..., pathn.pagen.id
    filename = clip_filename(filename, 'csv')
    if type(stores[0]) is not list:
        stores = [stores]
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for store in stores:
            path = []
            for r in store:
                path.append(page_id(r.page))
            writer.writerow(path)
    if prnt: print('wrote', len(stores), 'path'+ \
                  ('s' if len(stores) > 1 else ''), 'to', str(filename)+'.csv')

def pathToCSV ( store, filename='mypath', prnt=False ):
# export a list of pages
# format:
#   page1.id, ..., pagen.id
    filename = clip_filename(filename, 'csv')
    pathsToCSV(store, filename, prnt=False)
    if prnt: print('wrote path to', str(filename)+'.csv')

def storesToCSV ( stores, story, filename='mystores', prnt=False ):
# export a store (pages in a path, along with probabilities of next page to visit).
# TODO - does it even make sense to try and stuff this into a csv format?
    filename = clip_filename(filename, 'csv')
    if type(stores[0]) is not list:
        stores = [stores]
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['page', 'probability of going to page...'])
        page_probs = []
        for page in story.pages:
            page_probs.append(page_id(page))
        page_probs.append('---quit---')
        writer.writerow([''] + page_probs)
        for store in stores:
            for r in store:
                row = []
                if type(r.page) is pg.Page:
                    row.append(r.page.id)
                else:
                    row.append('---')
                row += ['']*(len(story.pages)+1)
                for page in r.options:
                    if type(page) is pg.Page:
                        idx = page_probs.index(page.id)
                    elif page == 0:
                        idx = page_probs.index('---quit---')
                    else:
                        idx = page_probs.index('---')
                    row[idx+1] = str(r.options[page])
                writer.writerow(row)
            writer.writerow('')
    if prnt: print('wrote', len(stores), 'store'+ \
                   ('s' if len(stores) > 1 else ''), 'to', str(filename)+'.csv')

def storeToCSV ( store, story, filename='mystore', prnt=False ):
    filename = clip_filename(filename, 'csv')
    storesToCSV(store, story, filename, prnt=False)
    if prnt: print('wrote store to', str(filename)+'.csv')

def cacheToCSV ( cache, filename='mycache', prnt=False ):
# export a cache (list of heuristic values)
# format:
#   data_type, page1.id, [page2.id, ..., pagen.id,] value
    from collections import defaultdict
    filename = clip_filename(filename, 'csv')

    def recurse ( row, cache, writer ):
        for key in cache:
            value = cache[key]
            key_name = key.id if type(key) is pg.Page else str(key)

            if type(value) is defaultdict:
                recurse(row + [key_name], value, writer)
            else:
                writer.writerow(row + [key_name, value])

    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        recurse([], cache, writer)

    if prnt: print('wrote cache to', str(filename)+'.csv')

def regressionToCSV ( reg, filename='myregression', prnt=False ):
# export regression parameters (list of heuristic values)
# format:
#   weight[0][0], weight[0][1], ... weight[0][n]
#                      ...
#   weight[n][0], weight[n][1], ... weight[n][n]
#
#        bias[0],      bias[1], ...      bias[n]
    filename = clip_filename(filename, 'csv')
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for w in reg['w']:
            writer.writerow(w)
        writer.writerow('')
        writer.writerow(reg['b'])

    if prnt: print('wrote regression to', str(filename)+'.csv')

def logregToCSV ( logreg, filename='mylogreg', prnt=False ):
# convenience function, for readibility mostly.
    filename = clip_filename(filename, 'csv')
    exportRegressionToCSV(logreg, filename, prnt=False)
    if prnt: print('wrote logistic regression to', str(filename)+'.csv')
def linregToCSV ( linreg, filename='mylinreg', prnt=False ):
# convenience function, for readability mostly.
    filename = clip_filename(filename, 'csv')
    exportLogregToCSV(linreg, filename, prnt=False)
    if prnt: print('wrote linear regression to', str(filename)+'.csv')

def nnToCSV ( nn, filename='myNN', prnt=False ):
# export a neural network (list of weight matrices & bias vectors)
# format:
#   w1, [                                         ]
#   w1, [     <weight matrix for first layer>     ]
#   w1, [                                         ]
#                   ... repeat to wn ...
#   b1, [      <bias vector for first layer>      ]
#                   ... repeat to bn ...
    import numpy as np
    filename = clip_filename(filename, 'csv')
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        num_layers = len(nn['w'])
        for w, i in zip(nn['w'], range(num_layers)):
            for row in w:
                rowname = 'w'+str(i)
                to_export = [ str(n) for n in np.asarray(row) ]
                writer.writerow([rowname] + to_export)
        for b, i in zip(nn['b'], range(num_layers)):
            bname = 'b'+str(i)
            to_export = [ str(n) for n in np.asarray(b) ]
            writer.writerow([bname] + to_export)

    if prnt: print('wrote neural network to', str(filename)+'.csv')

def cacheToJSON ( cache, filename='mycache', prnt=False ):
    filename = clip_filename(filename, 'json')
    with open(filename+'.json', 'w', newline='') as jsonfile:
        json.dump(cache, jsonfile, indent=4)
    if prnt: print('wrote cache to', str(filename)+'.json')

def storesToJSON ( stores, filename='mystores', prnt=False ):
    filename = clip_filename(filename, 'json')
    if type(stores[0]) is not list:
        stores = [stores]
    jsonable = []
    with open(filename+'.json', 'w', newline='') as jsonfile:
        for store in stores:
            one_store_json = []
            for r in store:
                page_name = page_id(r.page)
                options = {}
                for p in r.options:
                    options[page_id(p)] = r.options[p]
                one_store_json.append({ 'page': page_name, 'options': options })
            jsonable.append(one_store_json)
        json.dump(jsonable, jsonfile, indent=4)
    if prnt: print('wrote', len(stores), 'store'+ \
                   ('s' if len(stores) > 1 else ''), 'to', str(filename)+'.json')

def storeToJSON ( store, filename='mystore', prnt=False ):
    filename = clip_filename(filename, 'json')
    storesToJSON(store, filename, prnt=False)
    if prnt: print('wrote store to', str(filename)+'.json')

def clip_filename ( filename, extension ):
# so that it doesn't matter if the user calls their file 'myname' or 'myname.json'
    ext_length = len(extension)+1
    if filename[-ext_length:] == '.'+extension:
        filename = filename[:-ext_length]
    return filename

def page_id ( page ):
# get an identifier for a page, taking into account quitting etc.
    name = '---'
    if type(page) is pg.Page:
        name = page.id
    elif page == 0:
        name = '---quit---'
    return name
