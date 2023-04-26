# TO-DO

# LATER: add suport for syntax highlighting when horizontally scrolling (strings & comments)
# LATER: selection highlight can't be drawn further than the panel boundaries
# LATER: add numbers highlight, string highlight should be ended with couples ('' or "" and not '" or "')

# MODULES
import pygame, sys
from scripts.cursor import cursor
from scripts.events import update_event, keys, key_update
from scripts.math.vector2 import Vector2, vectorize
from scripts.math.camera import camera
from scripts.ui.panel import TextPanel, TopNavPanel, update_panel_buttons
from scripts.ui.grid import grid
from scripts.components.shapes import update_shape_dragging
from scripts.components.PCB import PCB
from scripts.components.CPU import CPU
from scripts.components.microcontroller import Microcontroller
from scripts.components.videochip import VideoChip
from scripts.components.screen import Screen
from scripts.dev import dev_update_and_draw, dev_update, dprint
from scripts.parser.pseudocode import get_game_state, get_code, update_code
from scripts.parser.user_print import user_print,dynamic_labels
from scripts.parser.exception_handler import handle_exception

IS_DEV = False
MAX_FPS = 60

# pygame setup
pygame.init()
pygame.display.init()
pygame.mixer.init()
pygame.display.set_caption('Micro Gadgets')
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
#pygame.mouse.set_visible(0)

# variables
panels = [TextPanel(Vector2(0,0), Vector2(500,500)), TopNavPanel(Vector2(camera.w_2-80, 0), Vector2(160, 40))]
shapes = [Screen(Vector2(800,900)),VideoChip(Vector2(900,100)),Microcontroller(Vector2(700,700)),CPU(Vector2(600,600)), PCB(Vector2(0,0))]
lastPressed = None
oldGameState = False

# MAIN LOGIC
while True:
    # --- frame init --- #
    screen.fill((0,0,0))
    cursor.pos = vectorize(pygame.mouse.get_pos())
    currentFps = round(clock.get_fps(),1)
    dev_update(currentFps, MAX_FPS)

    # ----- instance updates ----- #
    cursor.update()

    try:
        if get_game_state() and oldGameState==False: # >>update loop
            # >>start execution
            user_print('Successfully executed code!')
            exec(get_code()[0])
        elif get_game_state() and oldGameState==True:                                         
            exec(get_code()[1])
        elif not get_game_state() and oldGameState==True:
            user_print('Terminated code!')
            exec(get_code()[2])
    except Exception as e:
        user_print(handle_exception(e))
    oldGameState = get_game_state()

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
                IS_DEV = not IS_DEV #False if IS_DEV==False else True
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
    update_shape_dragging(shapes)
    #updateDrawer(shapes)

    # ----- panel updates ----- #
    update_panel_buttons(panels, shapes)
    for panel in panels:
        panel.update(panels, shapes)

    # ----- drawing ----- #
    grid(61,(20,20,20))
    grid(181,(80,80,80))

    for shape in shapes:
        shape.draw(screen)
    for panel in panels:
        panel.draw(screen)
    for label in dynamic_labels:
        label.draw(screen, label.text)
        if label.color == (0,0,0): dynamic_labels.remove(label)

    if IS_DEV==True:
        dev_update_and_draw(screen, currentFps, MAX_FPS, lastPressed)

    # --- screen refreshing ---#
    pygame.display.update()
    clock.tick(MAX_FPS)
