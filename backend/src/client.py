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
            print("Failed to connect")
        while True:
            raw = input(">>>")
            self.Protocol(self.connection)
    
    @property
    def active_protocol_name(self):
        return self.Protocol.protocol_name


class BaseProtocol:
    def __init__(self, conn):
        self.conn = conn
        try:
            sure_send(conn=self.conn, data=self.protocol_name.encode())
            time.sleep(1)
        except ConnectionError:
            pass
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
    
    @property
    def protocol_name(self):
        return self.__class__.__name__

class FileFolderTransferProtocol(BaseProtocol):
    def setup(self):
        self.inp = recvall(conn=self.conn).decode()
        print(self.inp)
    
    def handle(self):
        self.do(self.inp)
    
    def do(self, som):
        for dir in os.scandir(som):
            print(dir)
            new = dir.path.split("\\")
            
            for i in range(len(self.inp.split("\\"))-1):
                del new[0]
                  
            package = str(Path.joinpath(Path(*new)))
            print(package)
            
            if dir.is_dir():
                full_package = f"Folder:::::{package}"
                sure_send(self.conn, full_package.encode())
                print("Package send")
                
                verify_recv = self.conn.recv(1)
                print(verify_recv)
                if verify_recv.decode() == "R":
                    print("Server has Confirmed")
                    time.sleep(.2)
                    self.do(dir.path)
                    continue
                
            if dir.is_file():
                with open(file=dir, mode="rb") as file:
                    full_package = b"File:::::" + package.encode() +b":::::"+ file.read()
                    sure_send(self.conn, full_package)
                    print("Package send")
                
                
                verify_recv = self.conn.recv(1)
                if verify_recv.decode() == "R":
                    print("Server has Confirmed")
                    time.sleep(.2)
                    pass


class UniversalProtocol():
    def __init__(self) -> None:
        pass



if __name__ == "__main__":
    PORT = 60_000
    HOST = "192.168.178.108"
    
    client = Socketclient(HOST, PORT, FileFolderTransferProtocol)
    client.connect()
