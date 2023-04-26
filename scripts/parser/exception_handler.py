
def handle_exception(e):
    e = str(e)
    if e == 'list.remove(x): x not in list':
        return 'Please use a correct base code structure!'
    return e