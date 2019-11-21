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
blocked = {}
blockLogin = []
login = {}
offline = {}

def listen(s):
    s.listen(1)
    while True:
        connection, address = s.accept()
        #upon successful connection with a client, begin a client thread
        threading.Thread(target = listenToClient,args = (connection,address)).start()

def listenToClient(connection, address):
    global offline
    global login
    username = userAuthentication(connection)
    #attempted implementation for blocking a user for blockDuration seconds after 3 failed attempts:
    split = username.split(' ', 1)
    if split[0] == "blockLogin":
        #print("blocking from login: " + split[1])
        sendStatement(connection, "3 unsuccessful login attempts. Wait "+ str(blockDuration) + " seconds and try again")
        #blockLogin.append(split[1])
        #timer = threading.Timer(blockDuration, listenToClient, args = (connection,address))
    
    #let others know user has logged in, store pertinent user info in global arrays and dictionaries
    broadcast(" has logged in", username)
    login[username]= True
    clients[username] = connection
    times[username] = time.time()
    blocked[username] = []
    if username not in offline:
        offline[username] = []

    #while the client is logged in, first check if there are any offline messages to forward,
    #then continualy check for incoming commands 
    while login[username]:
        for item in offline[username]:
            responseHandler(item, username)
            offline[username].remove(item)
        data = connection.recv(buffer)
        if data:
            responseHandler(data, username)

#specifies that the client should ask for user input upon recieving the message, and imediately send back the user's response.
def sendQuestion(connection, question):
    message = "question " + question
    try:
        connection.send(message.encode('utf-8'))
    except:
        print("connection messed up")

#specifies that the client need only present the message as is
def sendStatement(connection, statement):
    message = "statement " + statement
    try:
        connection.send(message.encode('utf-8'))
    except:
        print("connection messed up")

#handles each type of request the user can have
def responseHandler(data, username):
    #grab global variables that contain all client data
    global login
    global blocked
    global offline
    global times
    global clients
    valid = False
    decoded = data.decode('utf-8')
    if "\n" in decoded:
        decoded = decoded.strip('\n')
    split = decoded.split(' ', 1)
    head = split[0]
    #if it is a command following hthe format [header] + [data]:
    if split[0]!=decoded:
        message = split[1]
        if head == "message":
            valid = True
            split2 = message.split(' ', 1)
            to = split2[0]
            if (to in clients) and (login[to]):
                if username not in blocked[to]:
                    msgcontent = username + ": " + split2[2]
                    sendStatement(clients[to], msgcontent)
                else: 
                    sendStatement(clients[username], "Your message could not be delivered as the recipient has blocked you.")
            elif (to in login) and (not login[to]):
                offline[to].append(data)
            else: 
                sendStatement(clients[username], "Recipient is not a user")
        elif head == "broadcast":
            valid = True
            broadcast(message, username)
        elif head == "whoelsesince":
            valid = True
            whoelsesince(username, int(message))
        elif head == "block":
            valid = True
            if message == username:
                sendStatement(clients[username], "Error. Cannot block self.")
            else:
                sendStatement(clients[username], message + " is blocked")
                blocked[username].append(message)
        elif head == "unblock":
            valid = True
            if message not in blocked[username]:
                sendStatement(clients[username], "Error. " + message + " was not blocked")
            else:
                sendStatement(clients[username], message + " is unblocked")
                blocked[username].remove(message)
    #else if it is single word command
    elif decoded == "whoelse":
        valid = True
        whoelse(username)
    elif decoded == "logout":
        valid = True
        sendStatement(clients[username], "You have logged out.")
        del clients[username]
        del times[username]
        login[username] = False
        broadcast(username + " has logged out")
    elif decoded == "":
        valid = True
        None
    #if the data matched none of the valid commands, let the user know their request was not valid
    if valid == False:
        sendStatement(clients[username], "Error. Invalid command.")

#authenticates the new client
def userAuthentication(connection):
    #retrieves valid username/password pairs from file
    credentials = dictionaryCredentials()
    #counter to keep track of failed login attempts
    fails = 0
    #only asks for username once, since username is how the program identifies blocked clients after 3 failed login
    sendQuestion(connection, "Enter your username:")
    data = connection.recv(buffer)
    if data:
        username = data.decode('utf-8')
        if "\n" in username:
            username = decoded.strip('\n')
    else:
        print("recived message not valid")

    while fails < 3:
        time.sleep(0.1)
        sendQuestion(connection, "Enter your password:")
        data = connection.recv(buffer)
        if data:
            password = data.decode('utf-8')
            if "\n" in password:
                password = decoded.strip('\n')
            password = data.decode('utf-8')
        else:
            print("recived message not valid")
        #check to see if the password matches the username key
        if username in credentials and credentials[username] == password:
            #confirms login to client by returning their username
            message = "username " + username
            connection.send(message.encode('utf-8'))
            return username
        #if incorrect password, or username not in credentials, ask for another password. This is an area for improvement.
        else:
            sendStatement(connection, "Invalid login. Try again.\n")     
            fails += 1
    #if 3 fails, return the keyword "blockLogin" and the username to block
    return "blockLogin " + username

#sends a list of all other online users
def whoelse(username):
    for item in clients:
        if item != username:
            sendStatement(clients[username], item)

#sends a list of all users that have logged in since a certain time
def whoelsesince(username, since):
    timeSince = time.time() - since
    for item in times:
        if (times[item] >= timeSince) & (item != username):
            sendStatement(clients[username], item)

#sends a message to each user in clients, as long as they are not the sender of the message or have blocked the sender 
def broadcast(broadcast, via):
    global blocked
    for item in clients:
        if via in blocked[item]:
            sendStatement(clients[via], "Your message could not be delivered to some recipients.")
        elif item != via:
            sendStatement(clients[item], via + ": " + broadcast)

#for each user in clients, send thier username to connected client
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

def Main():
    #create a socket
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    #bind to the local host
    host = ''
    s.bind((host, port))
    #listen for incoming connections with this socket
    listen(s)

if __name__ == '__main__': 
    Main() 