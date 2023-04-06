# TO-DO

# LATER: add suport for syntax highlighting when horizontally scrolling (strings & comments)
# LATER: selection highlight can't be drawn further than the panel boundaries
# LATER: add numbers highlight, string highlight should be ended with couples ('' or "" and not '" or "')

# DONE : panel order management depending on last clicked panel
# DONE : add maintained key press support for all keys, including BACKSPACE and RETURN
# DONE : Ctrl-x should copy (and not juste delete)
# DONE : add Ctrl-A
# DONE : selection shouldn't be removed when clicking with the cursor further than the line span
# DONE : maintained arrow press for faster navigation
# DONE : huge optimization for ColoredLabel class
# DONE : optimizing huge amounts of lines
# DONE : cursor can't be drawn further than the panel boundaries

# MODULES
import pygame, sys
from scripts.cursor import cursor
from scripts.events import update_event, keys, key_update
from scripts.math.vector2 import Vector2, vectorize
from scripts.math.camera import camera
from scripts.ui.panel import Panel, TextPanel, TopNavPanel
from scripts.ui.label import Label
from scripts.ui.grid import grid
from scripts.ui.shapesDrawer import updateDrawer
from scripts.dev import dev_update_and_draw, dev_update
from scripts.version import PYGAME_VERSION

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
panels = [TextPanel(Vector2(0,0), Vector2(500,500)), TopNavPanel(Vector2(camera.w_2-80, 0), Vector2(160, 40))]
fpsLabel = Label(Vector2(0,-4), color=(0,255,0))
shapes = []
lastPressed = None

# MAIN LOGIC
while True:
    # --- frame init --- #
    screen.fill((0,0,0))
    cursor.pos = vectorize(pygame.mouse.get_pos())
    currentFps = round(clock.get_fps(),1)
    dev_update(currentFps, MAX_FPS)

    # ----- instance updates ----- #
    cursor.update()

    # ------- event handler ------- #
    for event in pygame.event.get():
        # KEY INPUTS
        update_event(event)

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
                    cursor.selectedElement.update_labels()
            elif event.button==5: # scroll down
                if 'Selectable.TextEntry' in cursor.selectedElement.get_type() and cursor.selectedElement.displayedLines[0]<len(cursor.selectedElement.content)-1:
                    cursor.selectedElement.displayedLines[0]+=1
                    cursor.selectedElement.displayedLines[1]+=1
                    cursor.selectedElement.update_labels()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                print(IS_DEV, IS_DEV==False, IS_DEV==True)
                IS_DEV = False if IS_DEV==False else True
            lastPressed = event.unicode
        elif event.type == pygame.KEYUP:
            lastPressed = None

    # ------- maintained key presses ------- #
    for key, values in keys.items():
        if values[0]>0:
            key_update(key, values[1], values[2])
            keys[key][0] += 1

    # ----- shape updates ----- #
    for shape in shapes:
        shape.update(shapes)
    shapes = updateDrawer(shapes)

    # ----- panel updates ----- #
    for panel in panels:
        panel.update(panels)

    # ----- drawing ----- #
    grid(61,(20,20,20))
    grid(181,(80,80,80))
    for panel in panels:
        panel.draw(screen)
    for shape in shapes:
        shape.draw(screen)

    if IS_DEV==True:
        dev_update_and_draw(screen, currentFps, MAX_FPS, lastPressed)

    # --- screen refreshing ---#
    pygame.display.update()
    clock.tick(MAX_FPS)
