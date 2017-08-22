import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))

import csv
import page as pg

##### exporter ###############
# functions to export a bunch of the program's data structures & outputs to csv.
##############################

def exportPathsToCSV ( stores, filename='mypaths' ):
# export lists of pages
# TODO - untested
# format:
#   path1.page1.id, ..., path1.pagen.id
#                   ...
#   pathn.page1.id, ..., pathn.pagen.id
    with open(filename+'.csv', 'w', newline='w') as csvfile:
        for store in stores:
            path = [ r.page.id for r in store if type(r.page) is pg.Page else '---' ]
            csvfile.writerow(path)

def exportPathToCSV ( store, filename='mypath' ):
# export a list of pages
# TODO - untested
# format:
#   page1.id, ..., pagen.id
    exportPathsToCSV([store], filename)

def exportStoreToCSV ( store, filename='mycache' ):
# export a cache (list of heuristic values)
# TODO - how to represent page + probabilities in csv form, for multiple stores?
# TODO - untested
    with open(filename+'.csv', 'w', newline='w') as csvfile:
        raise NotImplementedError('not dunnit yet!')

def exportCacheToCSV ( cache, filename='mycache' ):
# export a cache (list of heuristic values)
# TODO - untested

    def recurse( row, cache, csvfile ):
    # TODO - very untested
        for key in cache:
            value = cache[key]
            key_name = key.id if type(key) is pg.Page else str(key)

            if type(value) is dict:
                recurse(row+[key_name], value, csvfile)
            else:
                csvfile.writerow(row+[value])

    with open(filename+'.csv', 'w', newline='w') as csvfile:
        recurse([], cache, csvfile)

# TODO - do exportLogreg & exportLinreg need to be separate functions?
def exportLogregToCSV ( logreg, filename='logreg' ):
# export logistic regression parameters (list of heuristic values)
# TODO - untested
# format:
#   weight[0][0], weight[0][1], ... weight[0][n]
#                      ...
#   weight[n][0], weight[n][1], ... weight[n][n]
#
#        bias[0],      bias[1], ...      bias[n]
    with open(filename+'.csv', 'w', newline='w') as csvfile:
        for w in logreg['w']:
            csvfile.writerow(w)
        csvfile.writerow()
        csvfile.writerow(logreg['b'])

def exportLinregToCSV ( linreg, filename='linreg' ):
# export linear regression parameters (list of heuristic values)
# TODO - untested
# format:
#   weight[0], weight[1], ... weight[n]
#
#     bias[0],   bias[1], ...   bias[n]
    with open(filename+'.csv', 'w', newline='w') as csvfile:
        for w in logreg['w']:
            csvfile.writerow(w)
        csvfile.writerow()
        csvfile.writerow(logreg['b'])

def exportNNToCSV ( nn, filename='nn' ):
# export a neural network (list of heuristic values)
# TODO - untested
# format:
#   w1, [                                         ]
#   w1, [     <weight matrix for first layer>     ]
#   w1, [                                         ]
#                   ... repeat to wn ...
#   b1, [      <bias vector for first layer>      ]
#                   ... repeat to bn ...
    with open(filename+'.csv', 'w', newline='w') as csvfile:
        num_layers = len(nn['w'])
        for w, i in zip(nn['w'], range(num_layers)):
            for row in w:
                rowname = 'w'+str(i)
                csvfile.writerow([rowname] + row)
        for b, i in zip(nn['b'], range(num_layers)):
            bname = 'b'+str(i)
            csvfile.writerow([bname] + b)
