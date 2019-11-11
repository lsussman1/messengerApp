from socket import *
import sys

#Server would be running on the same host as Client
IP = sys.argv[1]
port = int(sys.argv[2])
buffer = 1024

def Main(): 
    sock = socket(AF_INET, SOCK_STREAM)
    # connect to server on local computer 
    sock.connect((IP,port)) 
    # message you send to server 
    while True: 
        data = sock.recv(buffer) 
        if data:
            recieveHandler(data, sock)
        # print the received message 
        # here it would be a reverse of sent message 
        #print('Received from the server :',str(data.decode('ascii'))) 
  

    # close the connection 
    socket.close() 
def recieveHandler(data, sock):
    decoded = data.decode('utf-8')
    split = decoded.split(' ', 1)
    head = split[0]
    message = split[1]
    if head == "question":
        response = input(message + " ")
        encoded = response.encode('utf-8')
        sock.sendto(encoded, (IP, port))
    if head == "statement":
        print(message)

if __name__ == '__main__': 
    Main() 