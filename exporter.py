import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import csv
import page as pg

##### exporter ###############
# functions to export a bunch of the program's data structures & outputs to csv.
##############################

def exportPathsPerReadingToCSV ( ppr, filename='mypaths_per_reading', prnt=False ):
# export a paths per reading dictionary. Not totally useful when the user logs
# exist as well, but there you go.
# format:
#   reading1.id, reading1.page1.id, ..., reading1.pagen.id
#                            ...
#   readingn.id, readingn.page1.id, ..., readingn.pagen.id
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for r in ppr:
            row = [r]
            for page in ppr[r]:
                page_name = '---'
                if type(page) is pg.Page:
                    page_name = page.id
                elif page == 0:
                    page_name = '---quit---'
                row.append(page_name)
            writer.writerow(row)

    if prnt: print('wrote paths for', len(ppr), 'reading'+ \
            ('s ' if len(ppr) > 1 else ' ')+'to', str(filename)+'.csv')

def exportPathsToCSV ( stores, filename='mypaths', prnt=False ):
# export lists of pages
# format:
#   path1.page1.id, ..., path1.pagen.id
#                   ...
#   pathn.page1.id, ..., pathn.pagen.id
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for store in stores:
            path = []
            for r in store:
                if type(r.page) is pg.Page:
                    path.append(r.page.id)
                else:
                    path.append('---')
            writer.writerow(path)
    if prnt: print('wrote', len(stores), 'path'+ \
                  ('s ' if len(stores) > 1 else ' ')+'to', str(filename)+'.csv')

def exportPathToCSV ( store, filename='mypath', prnt=False ):
# export a list of pages
# format:
#   page1.id, ..., pagen.id
    exportPathsToCSV([store], filename, prnt=False)
    if prnt: print('wrote path to', str(filename)+'.csv')

def exportStoreToCSV ( story, store, filename='mystore', prnt=False ):
# export a store (pages in a path, along with probabilities of next page to visit).
# TODO - does it even make sense to try and stuff this into a csv format?
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['page', 'probability of going to page...'])
        page_probs = []
        for page in story.pages:
            if type(page) is pg.Page:
                page_probs.append(page.id)
            else:
                page_probs.append('---')
        page_probs.append('---quit---')
        writer.writerow([''] + page_probs)
        for r in store:
            row = []
            if type(r.page) is pg.Page:
                row.append(r.page.id)
            else:
                row.append('---')
            row += ['0']*(len(story.pages)+1)
            for page in r.options:
                if type(page) is pg.Page:
                    idx = page_probs.index(page.id)
                elif page == 0:
                    idx = page_probs.index('---quit---')
                else:
                    idx = page_probs.index('---')
                row[idx+1] = str(r.options[page])
            writer.writerow(row)
    if prnt: print('wrote store to', str(filename)+'.csv')

def exportCacheToCSV ( cache, filename='mycache', prnt=False ):
# export a cache (list of heuristic values)
# format:
#   data_type, page1.id, [page2.id, ..., pagen.id,] value
    from collections import defaultdict

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

# TODO - do exportLogreg & exportLinreg need to be separate functions?
def exportLogregToCSV ( logreg, filename='mylogreg', prnt=False ):
# export logistic regression parameters (list of heuristic values)
# format:
#   weight[0][0], weight[0][1], ... weight[0][n]
#                      ...
#   weight[n][0], weight[n][1], ... weight[n][n]
#
#        bias[0],      bias[1], ...      bias[n]
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for w in logreg['w']:
            writer.writerow(w)
        writer.writerow('')
        writer.writerow(logreg['b'])

    if prnt: print('wrote logistic regression to', str(filename)+'.csv')

def exportLinregToCSV ( linreg, filename='mylinreg', prnt=False ):
# export linear regression parameters (list of heuristic values)
# format:
#   weight[0], weight[1], ... weight[n]
#
#     bias[0],   bias[1], ...   bias[n]
    with open(filename+'.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for w in linreg['w']:
            writer.writerow(w)
        writer.writerow('')
        writer.writerow(linreg['b'])

    if prnt: print('wrote linear regression to', str(filename)+'.csv')

def exportNNToCSV ( nn, filename='myNN', prnt=False ):
# export a neural network (list of heuristic values)
# format:
#   w1, [                                         ]
#   w1, [     <weight matrix for first layer>     ]
#   w1, [                                         ]
#                   ... repeat to wn ...
#   b1, [      <bias vector for first layer>      ]
#                   ... repeat to bn ...
    import numpy as np
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
