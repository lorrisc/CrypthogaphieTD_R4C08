import socket
import rsa
from rsa.key import *


class Client:
    def __init__(self, port):
        self.host = socket.gethostname()  # as both code is running on same pc
        self.port = port
        self.client_socket = socket.socket()  # instantiate
        self.bfile = None

        # Generate public and private key for the client
        (self.publicKey, self.privateKey) = rsa.newkeys(512)

    def connect(self):
        self.client_socket.connect(
            (self.host, self.port))  # connect to the server

    def receiveFile(self):
        # receive the size of the file
        expected_size = b""
        while len(expected_size) < 8:
            more_size = self.client_socket.recv(8 - len(expected_size))
            if not more_size:
                raise Exception("Short file length received")
            expected_size += more_size

        # Convert to int, the expected file length
        expected_size = int.from_bytes(expected_size, 'big')

        # Until we've received the expected amount of data, keep receiving
        self.bfile = b""  # Use bytes, not str, to accumulate
        while len(self.bfile) < expected_size:
            buffer = self.client_socket.recv(expected_size - len(self.bfile))
            if not buffer:
                raise Exception("Incomplete file received")
            self.bfile += buffer
        return self.bfile

    def receiveMessage(self):
        return self.client_socket.recv(1024).decode()

    def sendMessage(self, msg: str):
        print("Sending:", msg)
        self.client_socket.send(str.encode(msg))

    def sendMessageWithKeys(self, msg):
        print("Sending binary message ... ")
        self.conn.send(msg)

    def receiveMessageWithKeys(self):
        return self.client_socket.recv(1024)

    def saveFile(self, bytes: b"", filename: str):
        with open(filename, 'wb') as f:
            f.write(self.bfile)

    def close(self):
        if not self.client_socket == None:
            self.client_socket.close()  # close the connection
        else:
            raise Exception(
                "Erreur: la connection a été fermée avant d'être instanciée.")


if __name__ == '__main__':

    client = Client(5000)
    client.connect()


    # RECEIVE PUBLIC KEY FROM THE SERVER
    serverPublicKey = client.receiveMessage()

    SPKey1, SPKey2 = serverPublicKey.split(";")
    SPKey1, SPKey2 = int(SPKey1), int(SPKey2)

    serverPublicKey = PublicKey(SPKey1, SPKey2)


    # SEND PUBLIC KEY TO THE SERVER
    client.sendMessage(str(client.publicKey.n) + ";" + str(client.publicKey.e))


    # RECEIVE MESSAGE FROM THE SERVER
    messageCrypte = client.receiveMessageWithKeys()
    message = rsa.decrypt(messageCrypte, client.privateKey)
    message = message.decode('utf8')
    print("\nMessage received : ", message)


    # RECEIVE FILES LIST FROM THE SERVER
    filesList = client.receiveMessage()
    print("\nBelow is the list of available files :")
    print(filesList)


    # SEND FILE NAME TO THE SERVER
    fileName = input("Choose a file to download :")
    client.sendMessage(fileName)


    # RECEIVE FILE FROM THE SERVER
    try:
        bfile = client.receiveFile()
        client.saveFile(bytes=bfile, filename="output/"+fileName)
        print("File saved at: ", "output/"+fileName)
    except:
        print("Error: File not found on the server")


    client.close()