import socket, pygame as pg
#Note that this is called EACH FRAME. Don't spam messages here
from inc.settings import *
from .ui import *

class Button(UIElement):
    def __init__(self, x, y, w, h, font, isServer = False):
        UIElement.__init__(self, x, y, w, h, font)
        self.isServer = isServer #Defaults to client-side
        self.add_text(font, "Server" if isServer else "Client", (255, 255, 255))

    def onClick(self, client, server):
        """If we get data from a client, return that we did"""
        if self.isServer:
            print(f"Starting a new server on {DEVHOST}:{PORT}")
            self.set_color((0, 255, 0))
            server.startUp()
            #The rest of this doesn't run
            return False
        else:
            print(f"Sending request to {DEVHOST}:{PORT}")
            self.set_color((255, 0, 0))
            return (client.sendRequest("Hello World") != 0)


class Lobby():
    def __init__(self, server, client, font):
        self.clientButton = Button(0, 0, 100, 50, font, isServer=False)
        self.serverButton = Button(120, 0, 100, 50, font, isServer=True)
        self.server = server
        self.client = client
        self.buttons = pg.sprite.Group([self.serverButton, self.clientButton])
    def update(self):
        """Updates game states. Returns the state if we need to switch."""
        #Check for screen-specific events here
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if pg.Rect.collidepoint(button.rect, pg.mouse.get_pos()):
                        return not button.onClick(self.client, self.server)
        return not self.server.hasConnection()

    def render(self, screen):
        #render the buttons it has to the screen
        self.buttons.draw(screen)

    