def get ( ls, id ):
    for item in ls:
        if item.id == id: return item
    return None

def index ( ls, id ):
    for i in range (0, len(ls.data)):
        if ls.data[i].id == id: return i
    return None

def save ( ls, item ):
    idx = ls.index(item.id)
    if idx is not None:
        ls[i] = item
        return
    ls.append(item)
