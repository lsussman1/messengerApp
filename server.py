import socket
from socket import *
import threading
import time
import datetime as dt
import sys

#global variables:
port = int(sys.argv[1])
blockDuration = int(sys.argv[2])
timeOut=int(sys.argv[3])
buffer = 4096
clients = {}
times = {}
blockLogin = []

def listen(s):
    s.listen(1)
    while True:
        connection, address = s.accept()
        threading.Thread(target = listenToClient,args = (connection,address)).start()

def listenToClient(connection, address):
    username = userAuthentication(connection)
    #block after 3 fails:
    split = username.split(' ', 1)
    if split[0] == "blockLogin":
        print("blocking " + split[1])
        sendStatement(connection, "3 unsuccessful login attempts. Wait "+ str(blockDuration) + " seconds and try again")
        blockLogin.append(split[1])
        timer = threading.Timer(blockDuration, self.listenToClient, args = (connection,address))
    #let others know user has logged in, store pertinent user info in dictionaries
    broadcast(username + " has logged in")
    clients[username] = connection
    times[username] = time.time()
    #list of users this user has blocked
    blocked = [] 
    #if havent received data for timeout seconds, log out client #NEED TO IMPLEMENT
    while True:
        data = connection.recv(buffer)
        if data:
            responseHandler(data, username, blocked)

def Main():
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    host = ''
    s.bind((host, port))
    listen(s)

def sendQuestion(connection, question):
    message = "question " + question
    connection.send(message.encode('utf-8'))

def sendStatement(connection, statement):
    message = "statement " + statement
    connection.send(message.encode('utf-8'))

def responseHandler(data, username, blocked):
    valid = False
    decoded = data.decode('utf-8')
    if "\n" in decoded:
        decoded = decoded.strip('\n')
    print(decoded)
    split = decoded.split(' ', 1)
    head = split[0]
    if split[0]!=decoded:
        message = split[1]
        if head == "message":
            valid = True
            split2 = message.split(' ', 2)
            via = split2[0]
            print(via)
            to = split2[1]
            print(to)
            if via not in blocked:
                msgcontent = username + ": " + split2[2]
                connection = clients[to]
                sendStatement(connection, msgcontent)
        elif head == "broadcast":
            valid = True
            broadcast(message)
        elif head == "whoelsesince":
            valid = True
            whoelsesince(username, int(message))
        elif head == "block":
            valid = True
            blocked.append(message)
        elif head == "unblock":
            valid = True
            blocked.remove(message)
    elif decoded == "whoelse":
        valid = True
        whoelse(username)
    elif decoded == "logout":
        valid = True
        print("logout")
    elif decoded == "":
        valid = True
        None
    if valid == False:
        sendStatement(clients[username], "Error. Invalid command.")

def userAuthentication(connection):
    credentials = dictionaryCredentials()
    fails = 0
    while fails < 3:
        print("fails: "+str(fails))
        sendQuestion(connection, "Enter your username:")
        data = connection.recv(buffer)
        if data:
            username = data.decode('utf-8')
            print(username)
        else:
            print("recived message not valid")
        sendQuestion(connection, "Enter your password:")
        data = connection.recv(buffer)
        if data:
            password = data.decode('utf-8')
            print(password)
        else:
            print("recived message not valid")
        if username in credentials and credentials[username] == password:
            #sendStatement(connection, "Logged in! :)")
            print("returning: " + username)
            message = "username " + username
            connection.send(message.encode('utf-8'))
            return username
        else:
            sendStatement(connection, "Invalid login. Try again.\n")     
            fails += 1
    print("blockLogin")
    return "blockLogin " + username

def whoelse(username):
    for item in clients:
        if item != username:
            sendStatement(clients[username], item)

def whoelsesince(username, since):
    timeSince = time.time() - since
    for item in times:
        if (times[item] >= timeSince) & (item != username):
            sendStatement(clients[username], item)

def broadcast(broadcast):
    for item in clients:
        sendStatement((clients[item]), broadcast)

def listCurrentUsers(connection):
    for item in clients:
        sendStatement(connection, item)

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