import socket
from socket import *
import threading
#from thread import *
import time
import datetime as dt
import sys

#global variables:
port = int(sys.argv[1])
blockTime = int(sys.argv[2])
timeout=int(sys.argv[3])
clients = []
#lock = threading.Lock()

#inspiration from https://stackoverflow.com/questions/23828264/how-to-make-a-simple-multithreaded-socket-server-in-python-that-remembers-client
class clientThread(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
    # main thread that listens for other connections
    def listen(self):
        self.socket.listen(1)
        while True:
            connection, address = self.socket.accept()
            threading.Thread(target = self.listenToClient,args = (connection,address)).start()
    #client threads that listen for messages
    def listenToClient(self, connection, address):
        clients.append(address)
        buffer = 1024
        login = False
        while True:
            #sendMessage(connection, "Enter your username:")
            userAuthentication(connection, buffer)
            try:
                data = connection,recv(buffer)
                if data:
                    responseHandler(data)
                else:
                    print("client disconnected")
            except:
                connection.close()
                return False

def Main():
    # would communicate with clients after every second
    UPDATE_INTERVAL= 1
    #run listening thread on localhost:
    clientThread('', port).listen()

def Ask(connection, buffer, question):
    message = "question " + question
    connection.send(message.encode('utf-8'))
    while True:
        data = connection.recv(buffer).decode('utf-8')
        if data:
            return data
def sendStatement(connection, buffer, statement):
    message = "statement" + statement
    connection.send(message.encode('utf-8'))

def responseHandler(data):
    message = data.decode('utf-8')
    head = message.split(' ', 1)[0]

def userAuthentication(connection, buffer):
    credentials = dictionaryCredentials()
    fails = 0
    while True:
        username = Ask(connection, buffer, "Enter your username:")
        if username in credentials:
            password = Ask(connection, buffer,"Enter your password:")
            if credentials[username] == password:
                return True
            else:
                sendStatement(connection, buffer, "Invalid login. Try again.")
        else:
            sendStatement(connection, buffer, "Invalid username. Try again.")
        fails += 1
        #for blocking after 3, implement later


# Returns dictionary with username-password pairs
def dictionaryCredentials():
    d = {}
    credentials = open("credentials.txt", "r+")
    for line in credentials:
        (username, password) = line.split()
        d[username] = password
    return d

if __name__ == '__main__': 
    Main() 