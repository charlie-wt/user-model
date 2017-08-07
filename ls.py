from collections import defaultdict

##### ls #####################
# a few simple functions to help with manipulating lists.
##############################

def get ( ls, id ):
    for item in ls:
        if item.id == id: return item
    return None

def index ( ls, id ):
    for i in range(len(ls)):
        if ls[i].id == id: return i
    return None

def save ( ls, item ):
    idx = index(ls, item.id)
    if idx is not None:
        ls[idx] = item
        return
    ls.append(item)

def count ( ls, id ):
    count = 0
    for item in ls:
        if item.id == id: count += 1
    return count

# a dictionary that automatically creates keys if they don't exist, deeply
auto_dict = lambda: defaultdict(auto_dict)
