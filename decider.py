import sys, os
sys.path.append(os.path.join(sys.path[0], "models"))
import location as l
import page

import heuristics as hs
import printer as pt

import ls
import math
import random

'''
decider

take a probability distribution of pages (as output from a ranker function) and
use one of these functions to choose a page - output as an index in the list of
visible pages.
'''

prnt = False

def best ( pages, options ):
    ''' simply choose the option with the highest likelihood. '''
    by_prob = sorted(options, key = lambda o : options[o])

    if prnt: pt.print_page_ranking(by_prob, sorted(options.values()))
    return pages.index(by_prob[-1])

def rand ( pages, options ):
    ''' choose via a random number. '''
    probs = sorted(options.values())
    by_prob = sorted(options, key = lambda o : options[o])

    choice = random.random()
    acc = 0

    if prnt:
        print("choice:", choice, "->")
        pt.print_page_ranking(by_prob, probs)

    for i in range(len(by_prob)):
        acc = acc + probs[i]
        if choice < acc:
            return pages.index(by_prob[i])

    if prnt: print("!rand fell through!")
    return pages.index(by_prob[len(by_prob)-1])
