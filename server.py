import socket
import rsa
from rsa.key import *
import os


class Server:
    def __init__(self, port):
        # get the hostname
        host = socket.gethostname()
        self.server_socket = socket.socket()  # get instance
        # look closely. The bind() function takes tuple as argument
        # bind host address and port together
        self.server_socket.bind((host, port))
        self.conn = None

        # Generate public and private key for the server
        (self.publicKey, self.privateKey) = rsa.newkeys(512)

    def waitForConnection(self):
        # configure how many client the server can listen simultaneously
        self.server_socket.listen(2)
        self.conn, address = self.server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))

    def sendMessage(self, msg: str):
        print("Sending:", msg)
        self.conn.send(str.encode(msg))

    def receiveMessage(self):
        return self.conn.recv(1024).decode()

    def sendMessageWithKeys(self, msg):
        print("Sending binary message ... ")
        self.conn.send(msg)

    def receiveMessageWithKeys(self):
        return self.client_socket.recv(1024)

    def sendFile(self, filename: str):
        print("Sending:", filename)
        with open(filename, 'rb') as f:
            raw = f.read()
        # Send actual length ahead of data, with fixed byteorder and size
        self.conn.sendall(len(raw).to_bytes(8, 'big'))
        self.conn.send(raw)  # send data to the client

    def close(self):
        if not self.conn == None:
            self.conn.close()  # close the connection
        else:
            raise Exception(
                "Erreur: la connection a été fermée avant d'être instanciée.")


if __name__ == '__main__':

    server = Server(5000)
    server.waitForConnection()


    # SEND PUBLIC KEY TO THE CLIENT
    server.sendMessage(str(server.publicKey.n) + ";" + str(server.publicKey.e))


    # RECEIVE PUBLIC KEY FROM THE CLIENT
    clientPublicKey = server.receiveMessage()

    CPKey1, CPKey2 = clientPublicKey.split(";")
    CPKey1, CPKey2 = int(CPKey1), int(CPKey2)

    clientPublicKey = PublicKey(CPKey1, CPKey2)


    # SEND MESSAGE TO THE CLIENT
    message = "C'est facile"

    message = message.encode('utf8')
    encryptMessage = rsa.encrypt(message, clientPublicKey)
    server.sendMessageWithKeys(encryptMessage)


    # GET AND SEND FILES LIST TO THE CLIENT
    folderPath = "input"
    filesStrList = ""
    for filename in os.listdir(folderPath):
        filesStrList = filesStrList + "\n" + filename

    server.sendMessage(filesStrList)


    # SEND ASK FILE TO THE CLIENT
    try:
        path = "input/"+ server.receiveMessage()
        server.sendFile(filename=path)
    except:
        print("Client file not found")


    server.close()