#Contains code for game server (receiving turn info and sending game states)
import socket
from inc.settings import *

class Server():
    """The server that listens for client requests. Used receive turn requests and give board states"""
    def __init__(self, client):
        """Pass in the client for the same app"""
        print("Server file successfully reached.")
        #Clients we are actively connected to (app's client is automatically setup)
        self.clients = [client.addr]
        #whose turn it is
        self.clientTurn = True #Refers to the client the server shares an application with
        self.turn = 1
        self.built = False 
        self.fought = False
        self.active = False
        self.moves = ["build", "fight"]
        self.mostRecentChange = NOCHANGE #Build, fight
        self.timeoutDelay = ASK_DELAY

    def hasConnection(self):
        """Returns whether the server has an active client connection"""
        return len(self.clients) > 1
    
    def listen(self):
        """Will listen for connections"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((DEVHOST, PORT))
            sock.listen()
            print("Server is listening...")
            #Waits for a connection, then returns connection info when a client reaches it
            c = sock.accept()
            print("Found connection!")
            #If there is no connection after some time, the program freezes
            print(f"connection info: {c}")
            return c
        
    def startUp(self):
        """Starts up the server so it begins listening. IT IS PAUSED WHILE LISTENING"""
        self.active = True #We know this server is active and we are the host.
        print("Server is now started up and waiting for connections!")
        conn, addr = self.listen()
            
        #While there is data, read it to the data variable
        data = conn.recv(1024)
        print(f"addr received: {addr}")

        #We got a new client, send back ack
        self.clients.append(addr[0])
        print(f"Connected by {addr}")
        response = data

        conn.send(response)
        print("Server has stopped listening safely.")
    
    def update(self):
        #Update sends an ACK if a client is asking for a turn request ("?")
        #Else, treat it as a turn submission
        conn, addr = self.listen()
        print("Got a connection in the update step!")
        changed = addr in self.clients
        data = conn.recv(1024)
        if data == b"isMyTurn":
            #If we are able to send this, it is the client's / guest's turn
            #Send over the most recent change
            toSend = []
            for move in self.mostRecentChange:
                x, y, setTo = move
                toSend.append(f"{x}|{y}|{setTo}")
            conn.send(bytes(','.join(toSend), 'utf-8'))
            self.mostRecentChange = NOCHANGE
            return (False, 0)
        elif data:
            #Give both game instances the same turn resolution so ownership maps match
            turn_resolved = self.handleTurn(data.decode('utf-8')) 
            conn.send(bytes(str(self.handleTurn(data.decode('utf-8'))), 'utf-8'))
            return turn_resolved
        else:
            conn.send(bytes("No", 'utf-8'))
            return (False, 0)
    
    def parseData(self, data):
        """ "isMyTurn" is a turn request
            First part is a representation of which part of the move is to be completed (0 for build, 1 for fight).
            The second part of the data denotes the coordinate that is the argument of the move.
            All 0's is a turn request"""
        print(data)
        move, coordx, coordy = data.split('|')
        coordx = int(coordx)
        coordy = int(coordy)
        
        if move not in self.moves:
            raise ValueError(f"Only available moves are {','.join(self.moves)}")

        try:
            coordx + coordy
        except:
            raise TypeError(f"Coords must be a tuple of Int.")

        print(f"Received move : {move}|{coordx}|{coordy}")

        return (move, coordx, coordy)

    def handleTurn(self, data):
        """Assumes we already have a player's connection and the data."""
        #We got data, parse it
        move, pointx, pointy = self.parseData(data)
        point = (pointx, pointy)
        changed = False 
        if move == self.moves[0]:
            #If move is to build a structure, send the point to change if needed
            changed = True
            self.built = True
            self.mostRecentChange[0] = (point[0], point[1], True)
        else: 
            #If move is to fight another player, resolve logic and send the point to change if needed
            changed = True
            self.fought = True
            self.mostRecentChange[1] = (point[0], point[1], False)
            if self.fought and self.built:
                self.clientTurn = not self.clientTurn
                if not self.clientTurn: self.turn+=1
                self.fought = False
                self.built = False
                print("Changed Turn")
        return (changed, point)
                