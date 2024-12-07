#Important info:
#This is a distributed application LAN game (see presentation)
#I did find how some parts of Python work from online official documentation
# and Geeks for Geeks (the later is listed as a comment where relevant).
#All written code is original.

import pygame as pg
from inc.settings import *
from .lobby import *
from .game import *
from .client import * 
from .server import *

pg.init()

window = pg.display.set_mode((WIDTH, HEIGHT))
pg.display.set_caption(TITLE)

#establish the font things can write text with
font = pg.font.Font(None, 24)

#Whether we have started a game (or are still looking for a game to play)
inLobby = True #For dev on game part, this should set to False

#Setup the client and give it to the server to be setup
client = Client()
#['127.0.0.1, 65432', ('127.0.0.1', 58644)]
server = Server(client)

clock = pg.time.Clock()

#The instance for each state.
lobby = Lobby(server, client, font)
game = Game(server, client, font)

#Game Loop
active = True 
while active:
    window.fill(BACKGROUND_COLOR) #Fill with a basic background color
    #Lobby / game code goes here
    #offloaded to seperate python files

    if inLobby: 
        lobby.render(window)
        inLobby = lobby.update()
        #If we're about to switch into the game
        if not inLobby:
            pg.display.set_caption(TITLE_SERVER) if server.hasConnection() else pg.display.set_caption(TITLE_CLIENT)
    else: 
        game.render(window)
        inLobby = game.update()

    #ALWAYS listen out for quitting the game
    for event in pg.event.get():       
        if event.type == pg.QUIT: 
            active = False
            server.active = False
    
    #All rendering needs to happen before this point
    pg.display.flip()
    #clock.tick(FPS)

print("What's up, danger?")