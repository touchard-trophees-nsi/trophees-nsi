import pygame
from scripts.math.vector2 import Vector2
from scripts.ui.shapes import Shape


def updatedDrawer(shapes):
    if shapes[0].pos != Vector2(50,50):
        shapes.insert(0,Shape(Vector2(50,50),Vector2(50,50),color=(100,110,10)))