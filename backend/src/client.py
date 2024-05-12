import logging
import socket
import time
import os
from pathlib import Path


def sure_send(conn, data=bytes):
    if isinstance(data, bytes) is False:
        raise TypeError
    data_len = str(len(data))
    package = f"{data_len}:::{data}"
    package = data_len.encode() + b":::" + data
    
    try:
        print(package)
        conn.sendall(package)
    except InterruptedError:
        return "Not everything was send"


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
            
            if dir.is_dir():
                full_package = f"Folder:::::{package}"
                sure_send(self.conn, full_package.encode())
                
                time.sleep(.5)
                
                self.do(dir.path)
            
            elif dir.is_file():
                with open(file=dir, mode="rb") as file:
                    full_package = b"File:::::" + package.encode() +b":::::"+ file.read()
                    sure_send(self.conn, full_package)
            
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
                
                send_it = str(Path.joinpath(Path(*new)))
                print(f"Folder:{send_it}".encode())
                self.conn.send(f"Folder:{send_it}".encode())
                time.sleep(.35)
                self.loop2(dir.path)
                
            elif dir.is_file():
                new = dir.path.split("\\")
                
                for i in range(self.ld):
                    del new[0]
                
                #print(f"File:{os.path.join(*new)}")
                #self.conn.send(f"File:{os.path.join(*new)}".encode())
                print(f"File:{str(Path.joinpath(Path(*new)))}")
                self.conn.send(f"File:{str(Path.joinpath(Path(*new)))}".encode())
                time.sleep(.35)
                with open(file=dir, mode="rb") as file:
                    self.conn.send(file.read())


PORT = 60_000
HOST = "192.168.178.108"

client = Socketclient(HOST, PORT, FileFolderTransferProtocol)
client.connect()


