import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import json
import csv
import page as pg
import analyser as an

##### exporter ###############
# functions to export a bunch of the program's data structures & outputs to csv.
##############################

def paths_per_reading_to_csv ( ppr, filename='mypaths_per_reading', prnt=False ):
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

def paths_to_csv ( stores, filename='mypaths', prnt=False ):
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

def path_to_csv ( store, filename='mypath', prnt=False ):
# export a list of pages
# format:
#   page1.id, ..., pagen.id
    filename = clip_filename(filename, 'csv')
    paths_to_csv(store, filename, prnt=False)
    if prnt: print('wrote path to', str(filename)+'.csv')

def stores_to_csv ( stores, story, filename='mystores', prnt=False ):
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

def store_to_csv ( store, story, filename='mystore', prnt=False ):
    filename = clip_filename(filename, 'csv')
    stores_to_csv(store, story, filename, prnt=False)
    if prnt: print('wrote store to', str(filename)+'.csv')

def cache_to_csv ( cache, filename='mycache', prnt=False ):
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

def regression_to_csv ( reg, filename='myregression', prnt=False ):
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

def logreg_to_csv ( logreg, filename='mylogreg', prnt=False ):
# convenience function, for readibility mostly.
    filename = clip_filename(filename, 'csv')
    regression_to_csv(logreg, filename, prnt=False)
    if prnt: print('wrote logistic regression to', str(filename)+'.csv')
def linreg_to_csv ( linreg, filename='mylinreg', prnt=False ):
# convenience function, for readability mostly.
    filename = clip_filename(filename, 'csv')
    regression_to_csv(linreg, filename, prnt=False)
    if prnt: print('wrote linear regression to', str(filename)+'.csv')

def nn_to_csv ( nn, filename='myNN', prnt=False ):
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

def cache_to_json ( cache, filename='mycache', prnt=False ):
    filename = clip_filename(filename, 'json')
    with open(filename+'.json', 'w', newline='') as jsonfile:
        json.dump(cache, jsonfile, indent=4)
    if prnt: print('wrote cache to', str(filename)+'.json')

def stores_to_json ( stores, filename='mystores', prnt=False ):
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

def store_to_json ( store, filename='mystore', prnt=False ):
    filename = clip_filename(filename, 'json')
    stores_to_json(store, filename, prnt=False)
    if prnt: print('wrote store to', str(filename)+'.json')

def compare_paths_to_csv ( story, store1, store2, filename='path comparison',
                           prnt=False ):
# export the result of analyser.compare_paths to csv
    result = an.compare_paths(story, store1, store2, prnt=False)
    filename = clip_filename(filename, 'csv')
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([result])

    if prnt: print('wrote path comparison to', str(filename)+'.csv')
    return result

def path_similarity_to_csv ( story, store1, store2, filename='path similarity',
                             prnt=False ):
# export the result of analyser.path_similarity to csv
    result = an.path_similarity(story, store1, store2, prnt=False)
    filename = clip_filename(filename, 'csv')
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([result])

    if prnt: print('wrote path similarity to', str(filename)+'.csv')
    return result

def page_visits_to_csv ( story, stores, filename='page visits', prnt=False ):
# export the result of analyser.page_visits to csv
    results = an.page_visits(story, stores, prnt=False)
    filename = clip_filename(filename, 'csv')
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for page in results:
            writer.writerow([page_id(page), results[page]])

    if prnt: print('wrote page visits to', str(filename)+'.csv')
    return results

def most_visited_to_csv ( story, stores, filename='most visited', prnt=False ):
# export the result of analyser.most_visited to csv
    results = an.most_visited(story, stores, prnt=False)
    filename = clip_filename(filename, 'csv')
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for result in results:
            writer.writerow([page_id(result[0]), result[1]])

    if prnt: print('wrote most visited to', str(filename)+'.csv')
    return results

def get_unreachables_to_csv ( story, stores=None, cache=None, filename='get unreachables', prnt=False ):
# export the result of analyser.get_unreachables to csv
    results = an.get_unreachables(story, stores, cache, prnt=False)
    filename = clip_filename(filename, 'csv')
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for result in results:
            writer.writerow(page_id(result))

    if prnt: print('wrote get unreachables to', str(filename)+'.csv')
    return results

def distance_travelled_to_csv ( story, stores, filename='distance travelled', prnt=False ):
# export the result of analyser.distance_travelled to csv
    results = an.distance_travelled(story, stores, prnt=False)
    filename = clip_filename(filename, 'csv')
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for result in results:
            writer.writerow([result])

    if prnt: print('wrote distance travelled to', str(filename)+'.csv')
    return results

def branching_factor_to_csv ( story, stores, filename='branching factor', prnt=False ):
# export the result of analyser.branching_factor to csv
    result = an.branching_factor(story, stores, prnt=False)
    filename = clip_filename(filename, 'csv')
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([result])

    if prnt: print('wrote branching factor to', str(filename)+'.csv')
    return result

def measure_ranker_to_csv ( story, ppr, ranker, cache=None, filename='measure ranker', prnt=False ):
# export the result of analyser.measure_ranker to csv
    results = an.measure_ranker(story, ppr, ranker, cache, prnt=False)
    filename = clip_filename(filename, 'csv')
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(len(results)):
            writer.writerow([i, results[i]])

    if prnt: print('wrote measure ranker to', str(filename)+'.csv')
    return results

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
