import matplotlib as mpl
import matplotlib.pyplot as plt

import analyser as an
import printer as pt
import ls

##### gui ####################
# functions to display various bits of info in a gui.
##############################

def visit_proportions ( data, sort='', story=None ):
# display a bar chart of the proportion of visits to each page
    # set up window
    mpl.rcParams['toolbar'] = 'none'
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111)
    fig.canvas.set_window_title((story.name if story is not None else "visits"))

    # split data
    if sort == 'story' and story is not None:
        data.sort(key = lambda p : story.pages.index(p[0]))
    names = [ p[0].name for p in data ]
    props = [ p[1] for p in data ]

    # chart params
    n = len(data)
    width = 0.75
    rects = ax.bar(range(n), props, width,
                   color='blue',
                   edgecolor='none',
                   tick_label=names)
    ax.plot(range(-1, n+1), [1]*(n+2), 'r-')
    title = "visits to each page per reading" + \
            (" for "+story.name if story is not None else "")
    ax.set_title(title)
    plt.setp(ax.get_xticklabels(), rotation=90, fontsize=10)
    plt.tight_layout()

    plt.show()

def show_info ( story, ppr=None, stores=None, sim_store=None, log_store=None,
                step_ahead_err=None ):
# show a bunch of info as text
    # basic window stuff
    mpl.rcParams['toolbar'] = 'none'
    mpl.rcParams['font.family'] = 'serif'
    fig = plt.figure(figsize=(15, 10))
    fig.canvas.set_window_title(story.name)

    # PART 1 - BASIC INFO
    # set up subplot
    ax = fig.add_subplot(211)
    hide_graph_stuff(ax)

    # text
    fig.suptitle("info for "+story.name, fontsize=21)

#    ax.set_facecolor((0.8, 1, 0.8))
    cells = []
    # number of readings
    if ppr is not None:
        count = str(len(ppr))
        cells.append(['number of readings:', count])

    # sim/log path similarity
#    if sim_store is not None and log_store is not None:
#        cells.append(['similarity of simulated path to log path:',
#                      pt.pc(an.path_similarity(story, sim_store, log_store))])

    # step ahead prediction error
    if step_ahead_err is not None:
        err = pt.pc(step_ahead_err, 2)
        cells.append(['step ahead prediction error:', err])

    if stores is not None:
        # average distance travelled
        dists = an.distance_travelled(story, stores)
        cells.append(['average distance travelled:', 
                     pt.fmt(sum(dists)/len(dists),suf='m')])

        # branching factor
        bf = an.branching_factor(story, stores)
        cells.append(['average branching factor:', pt.fmt(bf, 2)])

        # unreachable pages
        names = ''
        unreachables = an.get_unreachables(story, stores)
        if len(unreachables) != 0:
            for p in unreachables:
                names += p.name + '\n '
        else: names = 'none!'
        cells.append(['unreachable pages:', names])

    # create table
    table = ax.table(cellText=cells,
                     cellLoc='center',
                     colWidths=[0.3, 0.15],
                     loc='center')

    # set size, fontsize, text alignment and font colour for table cells.
    table.auto_set_font_size(False)
    table.set_fontsize(16)
    table.scale(2, 3)
    for loc in table._cells:
        c = table._cells[loc]
        c.set_linewidth(0)
        if loc[1] == 1:
            c._loc = 'left'
            c._text.set_color('r')
        else:
            c._loc = 'right'
            c._text.set_color('k')

    # PART 2 - PATH COMPARISON
    # new subplot, to compare paths
    ax2 = fig.add_subplot(224)
    hide_graph_stuff(ax2)

    # get page names for paths, put in right format for table
    paths = []
    for i in range(max(len(sim_store), len(log_store))):
        sim_page = "---"
        if i < len(sim_store) and sim_store[i].page is not None:
            sim_page = sim_store[i].page.name
        log_page = "---"
        if i < len(log_store) and log_store[i].page is not None:
            log_page = log_store[i].page.name
        paths.append([sim_page, log_page])

    # make table
    col_names = ['sim', 'log']
    paths_table = ax2.table(cellText=paths,
                            cellLoc='center',
                            colLabels=col_names,
                            colWidths=[0.5, 0.5],
                            loc='upper center')
    paths_table.auto_set_font_size(False)
    paths_table.set_fontsize(11)
    paths_table.scale(1.3, 1.5)
    for loc in paths_table._cells:
        c = paths_table._cells[loc]
        c.set_linewidth(0)
        if loc[0] == 0:
            c._text.set_weight('semibold')
            c._text.set_fontsize(16)

    # path similarity label
    ax2.text(0.5, 1.1, "path similarity: "+ \
             pt.pc(an.path_similarity(story, sim_store, log_store)),
             ha='center', fontsize=16)

    # PART 3 - PAGE VISIT PROPORTION GRAPH
    # new subplot, to show visit proportion graph
    ax3 = fig.add_subplot(223)

    # split data
    data = an.most_visited(story, stores)
    sort = 'story'
    if sort == 'story':
        data.sort(key = lambda p : story.pages.index(p[0]))
    names = [ p[0].name for p in data ]
    props = [ p[1] for p in data ]

    # chart params
    n = len(data)
    width = 0.75
    rects = ax3.bar(range(n), props, width,
                    color='blue',
                    edgecolor='none',
                    tick_label=names)
    ax3.plot(range(-1, n+1), [1]*(n+2), 'r-')
    ax3.set_title("visits to each page per reading")
    plt.setp(ax3.get_xticklabels(), rotation=70, fontsize=8)

    plt.show()

def hide_graph_stuff ( ax ):
# remove axes & ticks for a subplot
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.tick_params(axis='x', colors='none')
    ax.tick_params(axis='y', colors='none')
