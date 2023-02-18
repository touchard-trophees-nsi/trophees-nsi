from cgitb import text
import pygame, sys
from scripts.cursor import cursor
from scripts.ui.widgets.textEntry import TextEntry

def shutdown():
    pygame.quit()
    sys.exit()

def directional_key_update(key, isPressingShift, isPressingCtrl):
    if key=='LEFT':
        cursor.selectedElement.move_cursor(-1, shift=isPressingShift, ctrl=isPressingCtrl)
    elif key=='RIGHT':
        cursor.selectedElement.move_cursor(1, shift=isPressingShift, ctrl=isPressingCtrl)
    elif key=='UP':
        cursor.selectedElement.move_line(-1, shift=isPressingShift)
    elif key=='DOWN':
        cursor.selectedElement.move_line(1, shift=isPressingShift)
    else:
        print('Invalid direcitonal key')

def update_event(event):
    if event.type == pygame.KEYDOWN:
        # ----- APP SHUTDOWN ----- #
        if event.key == pygame.K_ESCAPE:
            shutdown()
        elif event.key == pygame.K_F3:
            return 'IS_DEV = not IS_DEV'
        # ----- ENTRY WRITING SYSTEM ----- #
        if cursor.selectedElement!=None and 'Selectable.TextEntry' in cursor.selectedElement.get_type():
            # Shortcuts
            isPressingShift = True if event.mod & pygame.KMOD_SHIFT>0 else False
            isPressingCtrl = True if event.mod & pygame.KMOD_CTRL>0 else False
            isPressingAlt = True if event.mod & pygame.KMOD_ALT>0 else False
            if isPressingCtrl and event.key==pygame.K_c: cursor.selectedElement.clipboard_copy()
            elif isPressingCtrl and event.key==pygame.K_v: cursor.selectedElement.clipboard_paste()
            # Special Input
            elif event.key == pygame.K_BACKSPACE: cursor.selectedElement.backspace(ctrl=isPressingCtrl)
            elif event.key == pygame.K_RETURN: cursor.selectedElement.add_return()
            # Navigation
            elif event.key == pygame.K_LEFT: directional_key_update('LEFT', isPressingShift, isPressingCtrl)
            elif event.key == pygame.K_RIGHT: directional_key_update('RIGHT', isPressingShift, isPressingCtrl)
            elif event.key == pygame.K_UP: directional_key_update('UP', isPressingShift, isPressingCtrl)
            elif event.key == pygame.K_DOWN: directional_key_update('DOWN', isPressingShift, isPressingCtrl)
            # Text input
            elif event.key == pygame.K_TAB:
                cursor.selectedElement.add_char('TAB', isManual=True)
            else:
                if event.unicode != '':
                    cursor.selectedElement.add_char(event.unicode, isManual=True)

    # --------------------------- #
    elif event.type == pygame.KEYUP:
        pass
    return ''
