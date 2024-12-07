import pygame as pg
#Holds all of the macros / constants / settings for the game
WIDTH, HEIGHT = 600, 600
TITLE = "TEST GAME"
TITLE_SERVER = "TEST GAME (Host)"
TITLE_CLIENT = "TEST GAME (Joined)"
BACKGROUND_COLOR = (100, 100, 100)
DEVHOST = "127.0.0.1" #defaults to localhost for testing
PORT = 65432
TILESIZE = 64 #Size of pixels each tile takes on the screen (DOES NOT CARE ABOUT ACTUAL TILE RESOLUTION)
MAPWIDTH, MAPHEIGHT = 4, 4 #Size of the map in tiles
MAP = "./data/map.hex"
OWNERSHIP = "./data/ownership.hex"
TILESET = "./assets/tileset.png"

STATUS_WAITING = "Waiting for Opponent"
STATUS_NOT_BUILT = "Build something!"
STATUS_NOT_FOUGHT = "Is there a settlement you want to fight?"
STATUS_ERROR = "UwU, there's an ewwor"

#Note, this is in milliseconds
ASK_DELAY = 5000
NOCHANGE = [(-1, -1, False), (-1, -1, False)]
FPS = 60