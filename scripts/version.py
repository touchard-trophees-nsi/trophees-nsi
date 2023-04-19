from pygame.version import PygameVersion, vernum

PYGAME_VERSION = vernum
PYGAME_IS_MODERN_VERSION = print(vernum >= PygameVersion(2,0,1))

if not PYGAME_IS_MODERN_VERSION:
    print(f'''--- ATTENTION ---
Votre version de pygame est obsolète ({str(PYGAME_VERSION)}).
La stabilité de l'application ne peut être garantie (fonctionnalités indisponibles ou crashs réccurents)
Veuillez mettre à jour pygame pour la version 2.0.1 ou plus (https://pypi.org/project/pygame/)
-----------------''')
