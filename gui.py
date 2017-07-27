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
    fig = plt.figure(figsize=(8, 4))
    ax = fig.add_subplot(111)
    fig.canvas.set_window_title(story.name)

    # hide axes & ticks
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.tick_params(axis='x', colors='none')
    ax.tick_params(axis='y', colors='none')

    # text
    fig.suptitle("info for "+story.name, fontsize=21)

#    ax.set_facecolor((0.8, 1, 0.8))
    col1 = []
    col2 = []
    # number of readings
    if ppr is not None:
        count = str(len(ppr))
        txt = 'this story has '+count+' logged readings'
        col1.append('number of readings:')
        col2.append(count)

    # sim/log path similarity
    if sim_store is not None and log_store is not None:
        txt = 'similarity of simulated path to log path: '+ \
              pt.pc(an.path_similarity(story, sim_store, log_store))
        col1.append('similarity of simulated path to log path:')
        col2.append(pt.pc(an.path_similarity(story, sim_store, log_store)))

    # step ahead prediction error
    if step_ahead_err is not None:
        err = pt.pc(step_ahead_err, 2)
        txt = 'step ahead prediction error: '+err
        col1.append('step ahead prediction error:')
        col2.append(err)

    if stores is not None:
        # average distance travelled
        dists = an.distance_travelled(story, stores)
        txt = 'average distance travelled: '+ \
              pt.fmt(str(int(sum(dists)/len(dists))),suf='m')
        col1.append('average distance travelled:')
        col2.append(pt.fmt(str(int(sum(dists)/len(dists))),suf='m'))

        # branching factor
        bf = an.branching_factor(story, stores)
        txt = 'average branching factor: '+pt.fmt(bf, 2)
        col1.append('average branching factor:')
        col2.append(pt.fmt(bf, 2))

        # unreachable pages
        names = ''
        unreachables = an.get_unreachables(story, stores)
        if len(unreachables) != 0:
            for p in unreachables:
                names += p.name + '\n '
        else: names = 'none!'
        txt = 'unreachable pages:\n'+names
        col1.append('unreachable pages:')
        col2.append(names)

    cells = []
    for i in range(len(col1)):
        cells.append([col1[i], col2[i]])
    table = ax.table(cellText=cells, cellLoc='center', colWidths=[0.3, 0.15],
                     loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(16)
    table.scale(2, 3)
    for cd in table.properties()['celld']:
        c = table.properties()['celld'][cd]
        c.set_linewidth(0)
        if cd[1] == 1:
            c._loc = 'left'
            c._text.set_color('r')
        else:
            c._loc = 'right'
            c._text.set_color('k')

    plt.show()
