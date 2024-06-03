import socket
import os

#TODO Used to serialize python objects (like a list or tuple)
import pickle

#TODO USE struct to restrict package len to 4 bytes
import struct

from pathlib import Path
#from util import sure_send, recvall
from util import send_msg, recv_msg, format_recv_msg


PACK_FMT = "!i"
PACK_SIZE = struct.calcsize(PACK_FMT)

class Socketclient:
    def __init__(self, host=str, port=int, Protocol=object):
        self.host = host
        self.port = port
        self.Protocol = Protocol
        
    def connect(self):
        while True:
            try:
                self.connection = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
                self.connection.connect((self.host, self.port))
                self.stay_connected()
            except ConnectionRefusedError:
                print("Failed to connect to address")
    
    def stay_connected(self):     
        while True:
            #raw = input(">>>")
            try:
                self.Protocol(self.connection)
            except ConnectionResetError:
                print("Server was closed")
                self.connection.close()
                break
    
    @property
    def active_protocol_name(self):
        return self.Protocol.protocol_name


class BaseProtocol:
    def __init__(self, conn):
        self.conn = conn
        try:
            send_msg(self.conn, self.protocol_name)
            #sure_send(conn=self.conn, data=self.protocol_name.encode())
            #time.sleep(1)
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
    
class FFT(BaseProtocol):
    def setup(self):
        #self.path_to_copy = recv_msg(self.conn, PACK_SIZE)
        self.path_to_copy = format_recv_msg(self.conn, PACK_SIZE)
        print(self.path_to_copy)
        
    def handle(self):
        self.send_dir(self.path_to_copy)
        pass
    
    def send_dir(self, current_dir):
        for dir in os.scandir(current_dir):
            package = []
            split_dir = dir.path.split("\\")
            
            for i in range(len(self.path_to_copy.split("\\"))-1):
                del split_dir[0]
            path = str(Path.joinpath(Path(*split_dir)))
            print(path)
            package.append(path)
                        
            if dir.is_dir():
                package.insert(0, "Folder")
                send_msg(self.conn, package)
                
                verify_recv = format_recv_msg(self.conn, PACK_SIZE)
                if verify_recv:
                    print("Server Confirmed")
                    self.send_dir(dir.path)
                    continue
            
            if dir.is_file():
                package.insert(0, "File")
                with open(file=dir, mode="rb") as file:
                    package.append(file.read())
                send_msg(self.conn, package)
                
                verify_recv = format_recv_msg(self.conn, PACK_SIZE)
                if verify_recv:
                    print("Server Confirmed")
        
        send_msg(self.conn, "Done")
                    
class ChatProtocol(BaseProtocol):
    def handle(self):
        while True:
            raw = input(">>>")
            send_msg(self.conn, raw)



if __name__ == "__main__":
    PORT = 60_000
    HOST = "192.168.178.108"
    
    client = Socketclient(HOST, PORT, FFT)
    client.connect()
