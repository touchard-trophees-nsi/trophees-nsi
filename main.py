# deletion when selection from up to down is 1 too much
# deletion when selection from down to up bug
# optimizing huge amounts of lines
# panel order management depending on last clicked panel
# add numbers highlight, string highlight should be ended with couples ('' or "" and not '" or "')

# DONE : Ctrl-x should copy (and not juste delete)
# DONE : add Ctrl-A
# DONE : selection shouldn't be removed when clicking with the cursor further than the line span
# DONE : maintained arrow press for faster navigation

# MODULES
import pygame, sys
from scripts.cursor import cursor
from scripts.events import update_event, keys, directional_key_update
from scripts.math.vector2 import Vector2, vectorize
from scripts.ui.panel import Panel, TextPanel, OTextPanel
from scripts.ui.label import Label
from scripts.ui.grid import grid

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
panels = [TextPanel(Vector2(0,0), Vector2(500,500)),OTextPanel(Vector2(500,250), Vector2(500,500))]
fpsLabel = Label(Vector2(0,-4), color=(0,255,0))

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

    # ------- maintained key presses ------- #
    for key, values in keys.items():
        if values[0]>0:
            directional_key_update(key, values[1], values[2])
            keys[key][0] += 1

    # ----- panel updates ----- #
    for panel in panels:
        panel.update(panels)

    # ----- drawing ----- #
    grid(61,(20,20,20))
    grid(181,(80,80,80))
    for panel in panels:
        panel.draw(screen)

    fpsLabel.text = str(current_fps)
    fpsLabel.draw(screen, fpsLabel.text)

    # --- screen refreshing ---#
    pygame.display.update()
    clock.tick(MAX_FPS)
