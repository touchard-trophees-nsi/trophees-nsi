import copy
from scripts.math.vector2 import Vector2
from scripts.ui.shapes import Shape

#Liste des formes affichées par défaut
defaultShapes = [Shape(Vector2(60,60),Vector2(60,60)),
                 Shape(Vector2(60,120),Vector2(60,60),color=(100,110,10), form="square"),
                 Shape(Vector2(120,60),Vector2(60,60),color=(100,110,10),form="triangle",direc=1),
                 Shape(Vector2(180,60),Vector2(60,60),color=(100,110,10),form="triangle",direc=2),
                 Shape(Vector2(120,120),Vector2(60,60),color=(100,110,10),form="triangle",direc=3),
                 Shape(Vector2(180,120),color=(100,110,10),form="triangle"),
                 Shape(Vector2(240,60),form="circle"),
                 Shape(Vector2(300,60),form="circle",direc=1),
                 Shape(Vector2(240,120),form="circle",direc=2),
                 Shape(Vector2(300,120),form="circle",direc=3)]

def updateDrawer(shapes):
    if shapes == []:
        return copy.deepcopy(defaultShapes)
    else:
        for i in range(len(defaultShapes)):
            if not defaultShapes[i] in shapes:
                shapes.append(defaultShapes[i].copy())
        return shapes
    