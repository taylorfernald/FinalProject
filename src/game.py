import pygame as pg
from inc.settings import *
from .ui import *

class Map():
    def __init__(self, map_path, ownership_path):
        """Fetches the map file and creates a 2d array based off of it"""
        self.map_file = open(map_path, 'r')
        map_string = self.map_file.read()
        self.own_file = open(ownership_path, 'r')
        own_string = self.own_file.read()
        own_bin = bin(int(own_string, 16))[2:].zfill(len(own_string)*4)
        own_split = [(own_bin[i:i+2]) for i in range(0, len(own_bin), 2)]
        self.map_array = []
        self.own_array = []
        for x in range(MAPWIDTH):
            map_row = []
            own_row = []
            for y in range(MAPHEIGHT):
                map_row.append(int(map_string[y*MAPHEIGHT + x]))
                own_row.append(int(own_split[y*MAPHEIGHT + x]))
            self.map_array.append(map_row)
            self.own_array.append(own_row)
        

        self.map_file.close()
        self.own_file.close()
    def getTile(self, x, y):
        """Gets the tile id at a certain coordinate"""
        return self.map_array[x][y]
    def getOwnership(self, x, y):
        """Gets the ownership status of a certain tile. Returns False if that tile happens to be out of bounds"""
        print("Ownership")
        print(x)
        print(y)
        if x < 0 or x >= MAPWIDTH: return False 
        if y < 0 or y >= MAPHEIGHT: return False
        print(self.own_array[x][y])
        return self.own_array[x][y]
    def setOwnership(self, x, y, toSet):
        self.own_array[x][y] = toSet
    def hasAdjacent(self, pos):
        """Checks the ownership map to see if there are any adjacent tiles that are also owned.
            Also there can't be a house where the position is"""
        i, j = pos
        if self.getOwnership(i-1, j): return True 
        elif self.getOwnership(i+1, j): return True 
        elif self.getOwnership(i, j+1): return True 
        elif self.getOwnership(i, j-1): return True
        return False


class SpriteSheet():
    def __init__(self, file):
        """self.image is the entire image"""
        self.image = pg.image.load(file).convert()
    def get_image(self, x, y):
        """Gets the image from the spritesheet, coords are based on tile id & ownership"""
        rect = pg.Rect(x * TILESIZE, y * TILESIZE, TILESIZE, TILESIZE)
        image = pg.Surface(rect.size).convert()
        image.blit(self.image, (0, 0), rect)
        return image

class Tile(pg.sprite.Sprite):
    def __init__(self, x, y, image):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = image
        self.rect = pg.Rect(x, y, TILESIZE, TILESIZE)
    
    def getCoordinates(self):
        """Returns the map coordinates of this tile as a tuple"""
        return (int(self.x / TILESIZE), int(self.y / TILESIZE))

    def onClick(self):
        print(f"Hi from {self.getCoordinates()}!")
    
class HUD(UIElement):
    def __init__(self, font):
        UIElement.__init__(self, 0, HEIGHT * 2 / 3 , WIDTH, HEIGHT / 3, font)
        self.color = (255, 255, 255)
        self.set_color(self.color)
    def fill(self):
        self.image.fill(self.color)
    
class Game():
    def __init__(self, server, client, font):
        #Get the spritesheet
        self.sprites = SpriteSheet(TILESET)
        #Get the map information
        self.loaded_map = Map(MAP, OWNERSHIP)
        #Make a group of tiles
        self.tiles = pg.sprite.Group()
        #Makes the tiles and sets them to the correct x and y coordinate
        for i in range(MAPWIDTH):
            for j in range(MAPHEIGHT):
                self.tiles.add(Tile(i * TILESIZE, j * TILESIZE, 
                                    self.sprites.get_image(self.loaded_map.getTile(i, j), self.loaded_map.getOwnership(i, j))))
        #Variables for UI
        self.resources = 99
        self.turn = 1 #TURN COUNTING STARTS WITH 1!!!!!!
        #Makes the hud
        self.font = font
        self.hud = HUD(font)
        self.hud.add_text(font, f"Resources: {self.resources}", (0, 0, 0), 10, 10)
        self.hud.add_text(font, f"Turn: {self.turn}", (0, 0, 0), 10, 30)
        self.status = ""

        self.server = server
        self.server
        self.client = client
        
        #Turn info
        self.isTurn = False
        self.built = False
        self.fought = False

        self.timer = ASK_DELAY
    def setOwnership(self, x, y, toSet):
        #Sets the tile to the appropriate ownership status.
        #Updates the ownership map too
        self.loaded_map.setOwnership(x, y, toSet)
        tiles = self.tiles.sprites()
        tiles[x*MAPWIDTH + y].image = self.sprites.get_image(self.loaded_map.getTile(x, y), self.loaded_map.getOwnership(x, y))
    def getStatus(self, isTurn):
        """Returns the string that matches what's actively going on"""
        #It's not the player's turn.
        if not isTurn:
            return STATUS_WAITING
        #It's their turn, but they haven't built anything.
        elif not self.built:
            return STATUS_NOT_BUILT
        #They've built, but they haven't fought yet.
        elif not self.fought:
            return STATUS_NOT_FOUGHT
        #Default / error case
        else:
            return STATUS_ERROR
    def setStatus(self, status):
        if status != self.status:
            self.status = status
    def update(self):
        """Updates game states. Returns the state if we need to switch."""
        if self.server.hasConnection():
            #print("Host update")
            self.isTurn = self.server.clientTurn
            self.setStatus(self.getStatus(self.isTurn))
            if not self.isTurn:
                #The host listens out for the guest's turn
                changed, point = self.server.update()
                print("Host is done listening!")
                if changed:
                    x, y = point
                    self.setOwnership(x, y, not self.server.clientTurn)
                    self.turn = self.server.turn
        else:
            #Ask if its our turn yet, ASSUMING ENOUGH TIME HAS PASSED TO NOT CLOG THE NETWORK
            if not self.timer and not self.isTurn:
                self.timer = ASK_DELAY
                change = self.client.requestUpdate()
                #If there was an actual change, then it is our turn and we need to update our screen.
                if change != NOCHANGE:
                    self.isTurn = True
                    build = change[0]
                    fight = change[1]
                    self.setOwnership(build[0], build[1], build[2])
                    self.setOwnership(fight[0], fight[1], fight[2])
            else:
                self.timer -= 1

            self.setStatus(self.getStatus(self.isTurn))

        #Check for screen-specific events here
        #if self.server.hasConnection(): print("screen-specific")
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN and self.isTurn:
                for tile in self.tiles:
                    if pg.Rect.collidepoint(tile.rect, pg.mouse.get_pos()) and self.loaded_map.hasAdjacent(tile.getCoordinates()):
                        #Resolve either building or fighting
                        coords = tile.getCoordinates()
                        if not self.built and not self.loaded_map.getOwnership(coords[0], coords[1]):
                            #Send the signal to build. Only flip the bit once we get ACK
                            answer = self.sendMove("build", tile.getCoordinates())
                            self.built = answer[0]
                            #Set ownership with the second part
                            self.setOwnership(answer[1][0], answer[1][1], True)
                        elif not self.fought:
                            answer = self.sendMove("fight", tile.getCoordinates())
                            self.fought = answer[0]
                            #Set ownership
                            self.setOwnership(answer[1][0], answer[1][1], False)

                            if self.fought and self.built:
                                self.isTurn = not self.isTurn
                                self.turn+=1

                        #Possibly reset the flags
                        if not self.isTurn:
                            self.built = False
                            self.fought = False
                            #Change the status before this screen freezes
                            self.setStatus(self.getStatus(False))
                        #Tile can do something to visually acknowledge the click.        
                        tile.onClick()
                        break; #break out of the for loop
        return False
    def sendMove(self, move, coords):
        """This and sendFight request a turn through the client / game to the server.
            Returns if we get an ACK from the server."""
        #Whether we are the host application or not.
        coordx, coordy = coords
        request = f"{move}|{coordx}|{coordy}"
        if self.server.active: return self.server.handleTurn(request)
        else:
            #We get the membership information in bytes.
            #Convert this to the actual values we need (Bool, (Int, Int)) 
            ret = self.client.sendRequest(request).decode('utf-8')
            ret = ret.replace('(', '')
            ret = ret.replace(')', '')
            ret = ret.split(',')
            ret[0] = ret[0] == "True"
            ret[1] = int(ret[1])
            ret[2] = int(ret[2])
            return (ret[0], (ret[1], ret[2]))

    def render(self, surface):
        self.tiles.draw(surface)
        self.hud.fill()
        #Draw the hud
        #Add the status text to the hud
        self.hud.add_text(self.font, f"Status: {self.status}    |   Turn: {self.turn}", (0, 0, 0), 10, 60)
        surface.blit(self.hud.image, (self.hud.x, self.hud.y))