import matplotlib as mpl
import matplotlib.pyplot as plt

def visit_proportions ( data, sort='', story=None ):
# display a bar chart of the proportion of visits to each page
    # set up window
    mpl.rcParams['toolbar'] = 'none'
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111)

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
    if story is not None:
        ax.set_title("proportions of visits to each page for "+story.name)
    else:
        ax.set_title("proportions of visits to each page")
    plt.setp(ax.get_xticklabels(), rotation=90, fontsize=10)
    plt.tight_layout()
    
    plt.show()
