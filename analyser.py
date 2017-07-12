import printer as pt

##### analyser ###############
# various functions to analyse a set of readings of a story.
##############################

def get_path_distribution ( page, ppr, prnt=False ):
# return dictionary of page : proportion of times it was picked from given page.
    options = {}

    for r in ppr:
        if page not in ppr[r]: continue
        idx = ppr[r].index(page)
        if idx == len(ppr[r]) - 1:
            options[0] = options[0] + 1 if 0 in options else 1
        else:
            next_page = ppr[r][idx+1]
            options[next_page] = options[next_page] + 1 if next_page in options else 1

    # normalise
    factor = 1 / sum(options.values())
    for o in options:
        options[o] = options[o] * factor

    # print
    if prnt: pt.print_options(options, page)

    return options

def pick_most_likely ( options ):
# for a dictionary of page : likelihood, return the page with the highest.
    if len(options) == 0: return None

    best = None

    for o in options:
        if best is None or options[o] > options[best]:
            best = o

    return best
