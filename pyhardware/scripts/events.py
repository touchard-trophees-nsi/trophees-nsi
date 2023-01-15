from cgitb import text
import pygame, sys
from scripts.cursor import cursor
from scripts.ui.widgets.textEntry import TextEntry

def shutdown():
    pygame.quit()
    sys.exit()

def update_event(event):
    if event.type == pygame.KEYDOWN:
        # ----- APP SHUTDOWN ----- #
        if event.key == pygame.K_ESCAPE:
            shutdown()
        elif event.key == pygame.K_F3:
            return 'IS_DEV = not IS_DEV'
        # ----- ENTRY WRITING SYSTEM ----- #
        if cursor.selectedElement!=None and 'Selectable.TextEntry' in cursor.selectedElement.get_type():
            if event.key == pygame.K_BACKSPACE: cursor.selectedElement.backspace()
            elif event.key == pygame.K_RETURN: cursor.selectedElement.add_return()
            # Navigation
            elif event.key == pygame.K_LEFT: cursor.selectedElement.move_cursor(-1) ; cursor.selectedElement.clear_selection()
            elif event.key == pygame.K_RIGHT: cursor.selectedElement.move_cursor(1) ; cursor.selectedElement.clear_selection()
            elif event.key == pygame.K_UP: cursor.selectedElement.move_line(-1) ; cursor.selectedElement.clear_selection() 
            elif event.key == pygame.K_DOWN: cursor.selectedElement.move_line(1) ; cursor.selectedElement.clear_selection()
            # Text input
            elif event.key == pygame.K_TAB:
                cursor.selectedElement.add_char('TAB')
            else:
                if event.unicode != '':
                    cursor.selectedElement.add_char(event.unicode)

    # --------------------------- #
    elif event.type == pygame.KEYUP:
        pass
    return ''