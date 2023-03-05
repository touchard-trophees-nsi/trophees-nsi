# MODULES
import pygame, sys
from scripts.cursor import cursor
from scripts.events import update_event
from scripts.math.vector2 import Vector2, vectorize
from scripts.ui.panel import Panel, TextPanel
from scripts.ui.grid import grid
from scripts.ui.shapes import Shape
from scripts.ui.shapesDrawer import updatedDrawer

IS_DEV = False
MAX_FPS = 60

# pygame setup
pygame.init()
pygame.display.init()
pygame.mixer.init()
pygame.display.set_caption('game')
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
#pygame.mouse.set_visible(0)

# variables
panels = [TextPanel(Vector2(0,0), Vector2(500,500))]
shapes = [Shape(Vector2(50,50),Vector2(60,60))]

# MAIN LOGIC
while True:
    # --- frame init --- #
    screen.fill((0,0,0))
    cursor.pos = vectorize(pygame.mouse.get_pos())
    current_fps = round(clock.get_fps(),1)
    
    # ----- instance updates ----- #
    cursor.update()

    # ------- event handler ------- #
    for event in pygame.event.get():
        # KEY INPUTS
        exec(update_event(event)) 
        # MOUSE INPUTS
        cursor.isClicking -= 1 if cursor.isClicking > 0 else 0
        cursor.isReleasing -= 1 if cursor.isReleasing > 0 else 0
        if event.type == pygame.MOUSEBUTTONUP:
            cursor.isReleasing = 2
            cursor.set_eventType(0)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            cursor.isClicking = 2
            cursor.set_eventType(event.button)

            # SCROLLING
            if event.button==4: # scroll up
                if 'Selectable.TextEntry' in cursor.selectedElement.get_type() and cursor.selectedElement.displayedLines[0]>0:
                    cursor.selectedElement.displayedLines[0]-=1
                    cursor.selectedElement.displayedLines[1]-=1
            elif event.button==5: # scroll down
                if 'Selectable.TextEntry' in cursor.selectedElement.get_type() and cursor.selectedElement.displayedLines[0]<len(cursor.selectedElement.content)-1:
                    cursor.selectedElement.displayedLines[0]+=1
                    cursor.selectedElement.displayedLines[1]+=1
    
    # ----- panel updates ----- #
    for panel in panels:
        panel.update(panels)

    # ----- shape updates ----- #
    for shape in shapes:
        shape.update(shapes)

    updatedDrawer(shapes)
    
    # ----- drawing ----- #
    grid(61,(20,20,20))
    grid(181,(80,80,80))
    for shape in shapes:
        shape.draw(screen)

    for panel in panels:
        panel.draw(screen)

    # --- screen refreshing ---#
    pygame.display.update()
    clock.tick(MAX_FPS)
