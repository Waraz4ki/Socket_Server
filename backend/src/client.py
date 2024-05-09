import logging
import socket
import time

import os
import json


logger = logging.getLogger(__name__)
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)


class Socketclient:
    def __init__(self, host=str, port=int, Protocol=object):
        self.host = host
        self.port = port
        self.Protocol = Protocol
        
        self.connection = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        
    def connect(self):
        try:
            self.connection.connect((self.host, self.port))
        except ConnectionRefusedError:
            print("No Server is running")
        #self.on_connect(form)
        
        while True:
            raw = input(">>>")
            self.Protocol(raw, self.connection)
    
    #def on_connect(self, form):
    #    self.send_form(form)
    #        
    #def send_form(self, form):
    #    self.connection.send(form)
    #    pass


class BaseProtocol:
    def __init__(self, inp, conn):
        self.inp = inp
        self.conn = conn
        self.setup()
        try:
            self.handle()
        finally:
            self.finish()

    def setup(self):
        pass

    def handle(self):
        pass

    def finish(self):
        pass

class ChatProtocol(BaseProtocol):
    def handle(self):
        self.conn.send(self.inp.encode())
   
class FileTransferProtocol(BaseProtocol):
    def setup(self):
        self.directory = r"C:\Users\moritz\Documents\Powi Script"
    
    def handle(self):
        self.loop(self.directory)
    
    def loop(self, path):
        for dir in os.scandir(path):
            if dir.is_dir():
                print(f"Folder:{dir.name}")
                self.conn.send(b"Folder:"+dir.name.encode())
                
                self.loop(dir.path)
                
            elif dir.is_file():
                print(f"File:{dir.name}")
                self.conn.send(b"File:"+dir.name.encode())
                
                time.sleep(5)
                
                with open(file=dir, mode="rb") as file:
                    self.conn.sendfile(file)


PORT = 60_000
HOST = "192.168.178.108"

client = Socketclient(HOST, PORT, FileTransferProtocol)
client.connect()


