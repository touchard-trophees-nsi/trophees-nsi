import copy
from scripts.math.vector2 import Vector2
from scripts.ui.shapes import Shape
defaultShapes = [Shape(Vector2(60,60),Vector2(60,60))]#,Shape(Vector2(120,60),Vector2(60,60))] 
def updatedDrawer(shapes):
    if shapes!= [] and shapes[0].pos != Vector2(60,60):
        shapes.insert(0,Shape(Vector2(60,60),Vector2(60,60),color=(100,110,10)))

def updateDrawer0(shapes):
    if shapes == []:
        return list(defaultShapes)
    else:
        for i in range(len(defaultShapes)):
            isinshapes = False
            for j in range(len(shapes)):
                print(defaultShapes[i] == shapes[j])
                if defaultShapes[i] == shapes[j]:

                    isinshapes = True
            if not isinshapes:
                shapes.append(defaultShapes[i].copy())
                
                print(shapes)

        return shapes

def updateDrawer(shapes):
    if shapes == []:
        return copy.deepcopy(defaultShapes)
    else:
        for i in range(len(defaultShapes)):
            if not defaultShapes[i] in shapes:
                shapes.append(defaultShapes[i].copy())
        return shapes