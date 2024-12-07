#Contains code for the game client (sending turn info and receiving game states)
from inc.settings import *
import socket

class Client():
    def __init__(self):
        self.server_addr = 0
        self.addr = DEVHOST #Note: Replace this with the address of the actual client.

    def requestUpdate(self):
        """ Asks the outward server whether its the client's turn or not.
            returns if there is any server response"""
        change = self.sendRequest("isMyTurn")
        if change != b"No":
            if change == 0: return NOCHANGE
            change = change.decode('utf-8')
            changes = []
            moves = change.split(',')
            for move in moves:
                c = move.split('|')
                changes.append((int(c[0]), int(c[1]), c[2] == "True"))
            return changes
        else:
            return NOCHANGE

    def sendRequest(self, request):
        """Sends a request to the server. If there is any data, then return it"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect((DEVHOST, PORT))
                self.server_addr = DEVHOST
                sock.sendall(bytes(request, 'utf-8'))
                data = sock.recv(1024)
            except:
                if request == "?": print("Waiting for turn.")
                else: print("Could not connect to friend. Are you sure you have the right IP?")
                return 0
        return data

        