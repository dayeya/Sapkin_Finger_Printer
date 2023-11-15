import os
import sys
import pickle
from socket import *
from .syn import SynHandler
from threading import Thread

try: 
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    sys.path.append(parent_dir)
    from common import Document
    
except ModuleNotFoundError as e:
    raise Exception("Check project dir as common was not found.")

ADDRESS = ('localhost', 60000)

class Module(Thread):
    
    UTF = "utf-8"
    BUFSIZE = 1024

    def __init__(self, name: str) -> None:
        """
        Client Module object.
        """
        print(f'{name} Opened a module!')
        self.server_sock = socket(AF_INET, SOCK_STREAM)
        self.server_sock.connect(ADDRESS)
        self.client_sock = socket(AF_INET, SOCK_STREAM)
        
        super().__init__(target=self.send_data)
        
    def end(self) -> None:
        """
        Terminates the Module.
        """
        self.server_sock.close()
        sys.exit(self.join())
    
    def receive(self) -> Document:
        """
        Receives data from the server.
        :return: Document.
        """
        data = self.server_sock.recv(Module.BUFSIZE)
        if not data:
            raise Exception("Connection with the server has timed out.")
        
        # More data to receive.
        if len(data) == Module.BUFSIZE:
            while True:
                try: 
                    data += self.server_sock.recv(Module.BUFSIZE)
                except: 
                    break

        data = pickle.loads(data)
        if not isinstance(data, Document):
            raise Exception("Wasn't given a document, please try again!")

        return data
    
    def log_in(self) -> None:
        # Update server.
        encoded_req: bytes = Document('LOG_IN', self.name).serialize()
        self.server_sock.send(encoded_req)
        
        # Get ACK.
        data = self.receive()
        if data.type != 'ACK': 
            raise Exception("Login was not complete!")
    
    def send_data(self) -> None:
        """
        Handles the clients' communication with the server.
        """
        
        print("[+] Connected to server!\n")
        
        while True:
            request = ''
            client_msg = input("Type: ").upper()

            if client_msg == "STOP":
                break

            elif client_msg == "ALL_USERS":
                request = "ALL_USERS"

            elif client_msg == "SCAN":
                request = "SCAN"

            elif client_msg.startswith("FP"):
                request, client_msg = client_msg.split(' ')
            else:
                request = "MSG"

            encoded_req: bytes = Document(request, client_msg).serialize()
            self.server_sock.send(encoded_req)
            
            data = self.receive()
            print(f"[+] {data.payload}")