from pygame import draw
from scripts.ui.label import Label
from scripts.math.vector2 import Vector2
from scripts.math.camera import camera

# graph
graph_min = 52
graph_max = 2
graph = []

# labels
labels = [Label(Vector2(0,-4), color=(0,255,0)), Label(Vector2(0,9), color=(0,255,0)), Label(Vector2(0,22), color=(0,255,0))]
tooltips = ['fps   ', 'MAXfps','key   ']

# debug log
debug_log = []
debug_labels = []

def dprint(text):
    debug_log.insert(0, str(text))
    debug_labels.append(Label(Vector2(0,camera.h-16), color=(0,255,0)))
    for i in range(len(debug_log)):
        debug_labels[i].position.y = camera.h-16*(i+1)
        debug_labels[i].text = str(debug_log[i])

def dclear(text):
    debug_log = []

def dev_update(*args):
    global graph
    graph.append(args[0])
    graph = graph[-360:]

def dev_update_and_draw(screen, *args):
    '''
    0: current fps, 1: max fps, 2: last pressed key
    '''
    global graph

    for i in range(len(labels)):
        labels[i].text = str(args[i])
        labels[i].draw(screen, tooltips[i]+' '+labels[i].text)

    for i in range(len(graph)-1):
        draw.line(screen, (0,255,0), (100+i*1, (args[1]+10)-graph[i]), (100+(i+1)*1, (args[1]+10)-graph[i+1]))

    for i in range(len(debug_labels[:50])):
        debug_labels[i].draw(screen, debug_labels[i].text)
