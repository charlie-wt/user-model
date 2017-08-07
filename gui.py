import matplotlib as mpl
import matplotlib.pyplot as plt

import analyser as an
import printer as pt
import ls

##### gui ####################
# functions to display various bits of info in a gui.
##############################

def visit_proportions ( sim_data, ppr=None, sort='', story=None ):
# display a window witha bar chart of the proportion of visits to each page
    # set up window
    mpl.rcParams['toolbar'] = 'none'
    mpl.rcParams['font.family'] = 'serif'
    fig = plt.figure(figsize=(14, 10))
    fig.canvas.set_window_title((story.name if story is not None else "visits"))

    ax = fig.add_subplot(111)
    visit_proportions_plot(ax, sim_data, ppr, sort, story)
    title = "visits to each page per reading" + \
            (" for "+story.name if story is not None else "")
    ax.set_title(title)

    plt.tight_layout()
    plt.show()

def visit_proportions_plot ( ax, sim_data=None, ppr=None, sort='', story=None ):
# a bar chart of the proportion of visits to each page
    if sim_data is None and ppr is None: return

    # global info
    width = 0.75 if sim_data is None or ppr is None else 0.35

    # 1 - simulation data
    sim_rects = None
    if sim_data is not None:
        # split data
        if sort == 'story' and story is not None:
            sim_data.sort(key = lambda p : story.pages.index(p[0]))
        names = [ p[0].name for p in sim_data ]
        props = [ p[1] for p in sim_data ]

        # chart params
        xs = range(len(sim_data))
        sim_rects = ax.bar(xs, props, width,
                           color='blue',
                           edgecolor='none',
                           tick_label=names)

    # 2 - log data
    log_rects = None
    if ppr is not None:
        log_data = an.log_most_visited(story, ppr)

        # split data
        if sort == 'story' and story is not None:
            log_data.sort(key = lambda p : story.pages.index(p[0]))
        elif sim_data is not None:
            sim_pages = [ p[0] for p in sim_data ]
            log_data.sort(key = lambda p : sim_pages.index(p[0]))
        names = [ p[0].name for p in log_data ]
        props = [ p[1] for p in log_data ]

        # chart params
        xs = range(len(log_data))
        if sim_data is not None: xs = [ x + width for x in xs ]
        log_rects = ax.bar(xs, props, width,
                           color='red',
                           edgecolor='none',
                           tick_label=names)

    # optional legend, if both bars present
    if sim_rects is not None and log_rects is not None:
        ax.legend((sim_rects[0], log_rects[0]), ('sim', 'log'))

    n = len(sim_data) if sim_data is not None else len(log_data)
    ax.plot(range(-1, n+1), [1]*(n+2), 'r-')
    plt.setp(ax.get_xticklabels(), rotation=90, fontsize=10)

    return ax

def text_info_plot ( ax, story, ppr=None, stores=None, sim_store=None, log_store=None,
                step_ahead_err=None ):
# some basic stats on a story, shown via text
    hide_graph_stuff(ax)

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
        err = pt.pc(1 - step_ahead_err, 2)
        cells.append(['step ahead prediction accuracy:', err])

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
                     cellColours=[['none']*len(cells[0])]*len(cells),
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

def text_info ( story, ppr=None, stores=None, sim_store=None, log_store=None,
                     step_ahead_err=None ):
    # basic window stuff
    mpl.rcParams['toolbar'] = 'none'
    mpl.rcParams['font.family'] = 'serif'
    fig = plt.figure(figsize=(8, 3))
    fig.canvas.set_window_title(story.name)

    ax = fig.add_subplot(111)
    text_info_plot(ax, story, ppr, stores, sim_store, log_store)
    ax.set_title("basic info for "+story.name)

    plt.tight_layout()
    plt.show()

def path_comparison_plot ( ax, story, sim_store, log_store ):
# show paths taken by simulation & average log, & edit distance between them.
    hide_graph_stuff(ax)

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
    paths_table = ax.table(cellText=paths,
                           cellLoc='center',
                           cellColours=[['none']*len(paths[0])]*len(paths),
                           colLabels=col_names,
                           colWidths=[0.5, 0.5],
                           colColours=['none']*len(col_names),
                           loc='center')
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
    ax.text(0.5, 0.9, "path similarity: "+ \
            pt.pc(an.path_similarity(story, sim_store, log_store)),
            ha='center', fontsize=16)

def path_comparison ( story, sim_store, log_store ):
    # basic window stuff
    mpl.rcParams['toolbar'] = 'none'
    mpl.rcParams['font.family'] = 'serif'
    fig = plt.figure(figsize=(10, 10))
    fig.canvas.set_window_title(story.name)

    # new subplot, to compare paths
    ax = fig.add_subplot(111)
    path_comparison_plot(ax, story, sim_store, log_store)
    ax.set_title("simulated vs. log-based path through "+story.name)

    plt.tight_layout()
    plt.show()

def show_all ( story, ppr=None, stores=None, sim_store=None, log_store=None,
               step_ahead_err=None ):
    # basic window stuff
    mpl.rcParams['toolbar'] = 'none'
    mpl.rcParams['font.family'] = 'serif'
    fig = plt.figure(figsize=(15, 10))
    fig.canvas.set_window_title(story.name)
    fig.suptitle("info for "+story.name, fontsize=21)

    # 1 - text info
    ax1 = fig.add_subplot(211)
    text_info_plot(ax1, story, ppr, stores, sim_store, log_store, step_ahead_err)

    # 2 - visit proportions
    ax2 = fig.add_subplot(223)
    visit_proportions_plot(ax2, an.most_visited(story, stores), ppr, 'story', story)

    # 3 - path comparison
    ax3 = fig.add_subplot(224)
    path_comparison_plot(ax3, story, sim_store, log_store)

    plt.tight_layout()
    plt.show()

def hide_graph_stuff ( ax ):
# remove axes & ticks for a subplot
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.tick_params(axis='x', colors='none')
    ax.tick_params(axis='y', colors='none')
