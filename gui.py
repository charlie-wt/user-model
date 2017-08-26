import matplotlib as mpl
import matplotlib.pyplot as plt

import analyser as an
import printer as pt
import ls
import cache as ch

'''
gui

functions to display various bits of info in a gui.
'''

def visit_proportions_plot ( ax, story, sim_store=None, ppr=None, sort='' ):
    ''' a bar chart of the proportion of visits to each page. '''
    if sim_store is None and ppr is None: return

    # global info
    width = 0.75 if sim_store is None or ppr is None else 0.35

    # 1 - simulation data
    sim_rects = None
    if sim_store is not None:
        # split data
        if sort == 'story' and story is not None:
            sim_store.sort(key = lambda p : story.pages.index(p[0]))
        names = [ pt.truncate(p[0].name) for p in sim_store ]
        props = [ p[1] for p in sim_store ]

        # chart params
        xs = range(len(sim_store))
        sim_rects = ax.bar(xs, props, width,
                           color='blue',
                           edgecolor='none',
                           tick_label=names)

    # 2 - log data
    log_rects = None
    if ppr is not None:
        log_store = an.log_most_visited(story, ppr)

        # split data
        if sort == 'story' and story is not None:
            log_store.sort(key = lambda p : story.pages.index(p[0]))
        elif sim_store is not None:
            sim_pages = [ p[0] for p in sim_store ]
            log_store.sort(key = lambda p : sim_pages.index(p[0]))
        names = [ pt.truncate(p[0].name) for p in log_store ]
        props = [ p[1] for p in log_store ]

        # chart params
        xs = range(len(log_store))
        if sim_store is not None: xs = [ x + width for x in xs ]
        log_rects = ax.bar(xs, props, width,
                           color='red',
                           edgecolor='none',
                           tick_label=names)

    # optional legend, if both bars present
    if sim_rects is not None and log_rects is not None:
        ax.legend((sim_rects[0], log_rects[0]), ('sim', 'log'))

    # add a red line at y=1.0, and rotate the x labels (page names)
    n = len(sim_store) if sim_store is not None else len(log_store)
    ax.plot(range(-1, n+1), [1]*(n+2), 'r-')
    plt.setp(ax.get_xticklabels(), rotation=90, fontsize=10)

    # title
    ax.set_title('visits to each page per reading', fontsize=15)

    return ax

def visit_proportions ( story, sim_store=None, ppr=None, sort='' ):
    ''' display a window with a bar chart of the proportion of visits to each
    page.
    '''
    # set up window
    mpl.rcParams['toolbar'] = 'none'
    mpl.rcParams['font.family'] = 'serif'
    fig = plt.figure(figsize=(14, 10))
    fig.canvas.set_window_title('visits | ' + story.name)

    # add bar chart
    ax = fig.add_subplot(111)
    visit_proportions_plot(ax, story, sim_store, ppr, sort)

    plt.tight_layout()
    plt.show()

def text_info_plot ( ax, story, ppr=None, stores=None, sim_store=None,
                     ranker=None, cache=None ):
    ''' some basic stats on a story, shown via text. '''
    hide_graph_stuff(ax)
    cells = []
    if cache is None: cache = ch.cache()

    # number of readings
    if ppr is not None:
        count = str(len(ppr))
        cells.append(['number of readings:', count])

    # step ahead prediction accuracy
    if ranker is not None:
        acc = pt.pc(an.measure_ranker(story, ppr, ranker, cache)[0], dec=2)
        cells.append(['step ahead prediction accuracy:', acc])

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
        unreachables = an.get_unreachables(story, stores, cache)
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

    # title
    ax.set_title('basic info', fontsize=15)

    return ax

def text_info ( story, ppr=None, stores=None, sim_store=None, ranker=None,
                cache=None ):
    # basic window stuff
    mpl.rcParams['toolbar'] = 'none'
    mpl.rcParams['font.family'] = 'serif'
    fig = plt.figure(figsize=(8, 3))
    fig.canvas.set_window_title('info | ' + story.name)

    # add text info plot
    ax = fig.add_subplot(111)
    text_info_plot(ax, story, ppr, stores, sim_store, ranker, cache)

    plt.tight_layout()
    plt.show()

def path_comparison_plot ( ax, story, sim_store, log_store ):
    ''' show paths taken by simulation & average log, & edit distance between
    them.
    '''
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

    # title
    ax.set_title('simulated vs. log-based path', fontsize=15)

    return ax

def path_comparison ( story, sim_store, log_store ):
    # basic window stuff
    mpl.rcParams['toolbar'] = 'none'
    mpl.rcParams['font.family'] = 'serif'
    fig = plt.figure(figsize=(10, 6))
    fig.canvas.set_window_title('paths | ' + story.name)

    # add path comparison plot
    ax = fig.add_subplot(111)
    path_comparison_plot(ax, story, sim_store, log_store)

    plt.tight_layout()
    plt.show()

def measure_ranker_plot ( ax, story, ppr, ranker, cache=None ):
    ''' plot the frequency of choices in relation to how the ranker ranked
    them.
    '''
    counts = an.measure_ranker(story, ppr, ranker, cache)

    # chart params
    width = 0.5
    xs = range(len(counts))
    rects = ax.bar(xs, counts, width,
                       color='blue',
                       edgecolor='none')

    # add a red line at y=1.0, and rotate the x labels (page names)
    n = len(counts)
    ax.plot(range(-1, n+1), [1]*(n+2), 'r-')
#    plt.setp(ax.get_xticklabels(), rotation=90, fontsize=10)

    plt.xticks(xs)
    ax.set_xlabel('page rankings')
    ax.set_ylabel('times page chosen was given this ranking')

    # title
    ax.set_title('comparison of log choices and ranker preference', fontsize=15)

    return ax

def measure_ranker ( story, ppr, ranker, cache=None ):
    ''' display a window with a bar chart showing a comparison of log choice &
    ranker.
    '''
    # set up window
    mpl.rcParams['toolbar'] = 'none'
    mpl.rcParams['font.family'] = 'serif'
    fig = plt.figure(figsize=(10, 8))
    fig.canvas.set_window_title('ranker | ' + story.name)

    # add bar chart
    ax = fig.add_subplot(111)
    measure_ranker_plot(ax, story, ppr, ranker, cache)

    plt.tight_layout()
    plt.show()

def show_main_three ( story, ppr, stores, sim_store, log_store, ranker,
                      cache=None ):
    # basic window stuff
    mpl.rcParams['toolbar'] = 'none'
    mpl.rcParams['font.family'] = 'serif'
    fig = plt.figure(figsize=(18, 8))
    fig.canvas.set_window_title(story.name)
    fig.suptitle("info for "+story.name, fontsize=21)

    # 1 - visit proportions
    ax1 = fig.add_subplot(131)
    visit_proportions_plot(ax1, story, an.most_visited(story, stores), ppr, 'story')

    # 2 - path comparison
    ax2 = fig.add_subplot(132)
    path_comparison_plot(ax2, story, sim_store, log_store)

    # 3 - ranker accuracy
    ax3 = fig.add_subplot(133)
    measure_ranker_plot(ax3, story, ppr, ranker, cache)
    acc = an.measure_ranker(story, ppr, ranker, cache)[0]
    acc_msg = 'step ahead accuracy: ' + pt.pc(acc, dec=2)
    ax3.text(1.5, -0.15, acc_msg, fontsize=15, ha='center')

    # spacing
    fig.subplots_adjust(wspace=1, top=0.2, bottom=0.0)
    plt.tight_layout()

    plt.show()

def show_all ( story, ppr=None, stores=None, sim_store=None, log_store=None,
               ranker=None, cache=None ):
    if cache is None: cache = ch.cache()
    ''' everything in one window. '''
    # basic window stuff
    mpl.rcParams['toolbar'] = 'none'
    mpl.rcParams['font.family'] = 'serif'
    fig = plt.figure(figsize=(15, 10))
    fig.canvas.set_window_title(story.name)
    fig.suptitle("info for "+story.name, fontsize=21)

    # 1 - text info
    ax1 = fig.add_subplot(221)
    text_info_plot(ax1, story, ppr, stores, sim_store, ranker, cache)

    # 2 - ranker accuracy
    ax2 = fig.add_subplot(222)
    measure_ranker_plot(ax2, story, ppr, ranker, cache)

    # 3 - visit proportions
    ax3 = fig.add_subplot(223)
    visit_proportions_plot(ax3, story, an.most_visited(story, stores), ppr, 'story')

    # 4 - path comparison
    ax4 = fig.add_subplot(224)
    path_comparison_plot(ax4, story, sim_store, log_store)

    # spacing
    fig.subplots_adjust(wspace=1, top=0.5, bottom=0.2)
    plt.tight_layout()

    plt.show()

def hide_graph_stuff ( ax ):
    ''' remove axes & ticks for a subplot. '''
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.tick_params(axis='x', colors='none')
    ax.tick_params(axis='y', colors='none')
