import logging
import socket
import time
import os


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
        while True:
            raw = input(">>>")
            self.Protocol(raw, self.connection)


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
   
class FFTProtocol(BaseProtocol):
    def setup(self):
        self.ld = len(self.inp.split("\\"))-1
    
    def handle(self):
        self.loop2(self.inp)
    
    def loop2(self, og_path):
        for dir in os.scandir(og_path):
            if dir.is_dir():
                new = dir.path.split("\\")
                
                for i in range(self.ld):
                    del new[0]
                
                self.conn.send(os.path.join(*new).encode())
                time.sleep(.1)
                self.loop2(dir.path)
                
            elif dir.is_file():
                new = dir.path.split("\\")
                
                for i in range(self.ld):
                    del new[0]
                
                self.conn.send(os.path.join(*new).encode())
                time.sleep(.1)
                with open(file=dir, mode="rb") as file:
                    self.conn.sendfile(file)


PORT = 60_000
HOST = "192.168.178.108"

client = Socketclient(HOST, PORT, FFTProtocol)
client.connect()


