import logging
import socket
import time
import os

from pathlib import Path
from util import sure_send, recvall


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
    
    
class FileFolderTransferProtocol(BaseProtocol):
    def handle(self):
        self.do(self.inp)
    
    def do(self, som):
        for dir in os.scandir(som):
            new = dir.path.split("\\")
            
            for i in range(len(self.inp.split("\\"))-1):
                del new[0]
                  
            package = str(Path.joinpath(Path(*new)))
            print(package)
            
            if dir.is_dir():
                full_package = f"Folder:::::{package}"
                sure_send(self.conn, full_package.encode())
                
                verify_recv = recvall(self.conn, 100)
                if verify_recv:
                    print("Confirmed")
                    self.do(dir.path)
            
            elif dir.is_file():
                with open(file=dir, mode="rb") as file:
                    full_package = b"File:::::" + package.encode() +b":::::"+ file.read()
                    sure_send(self.conn, full_package)
                
                verify_recv = recvall(self.conn, 100)
                if verify_recv:
                    print("Confirmed")
                    pass


PORT = 60_000
HOST = "192.168.178.108"

client = Socketclient(HOST, PORT, FileFolderTransferProtocol)
client.connect()


