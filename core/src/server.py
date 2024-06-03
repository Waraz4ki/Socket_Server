import multiprocessing as mp
import os
import sys
import logging
import socket
import struct
import pickle

from threading import Thread, Event, Lock, current_thread
from core.src.util import send_msg, recv_msg, format_recv_msg

#! Call a file into pseudo memory and naviate like a list
import mmap

SERVER_NAME = "Git"
LOG_PATH = "./core/log" 


logger = logging.getLogger(name=SERVER_NAME)
logging.basicConfig(filename=f"{LOG_PATH}{SERVER_NAME}.log", encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
"""Two Part Server

__________                        ______________
|        |                        |            |
|  Main  |----------------------> |  Comm port | <-------------- Connection
|        |                        |            |
__________                        ______________
   / \
    |
    |
    |
 Command
"""
PACK_FMT = "!i"
PACK_SIZE = struct.calcsize(PACK_FMT)

class SocketServer():
    """A Multithreaded Socket Server
    """
    __serve = True
    
    def __init__(self, host=str, port=int, Handler=object):
        """
        Can be supplied with a custom Handler class(has to inherit the BaseHandler class). If no Handler class is suplied, it will default to
        the UniversalHandler
        """  
        self.terminate = False
        self.host = host
        self.port = port
        if Handler is None:
            self.RequestHandler = UniversalHandler
        else:
            self.RequestHandler = Handler
        
        if len(host) > 15:
            self.fam = socket.AF_INET6
        else:
            self.fam = socket.AF_INET
    
    def activate(self):
        """Will initiate the server and await connections
        """
        with socket.socket(family=self.fam, type=socket.SOCK_STREAM) as self.server:
            if self.server:
                try:
                    self.server.bind((self.host, self.port))
                    self.server.listen()

                except OSError:
                    logger.info(f"Server is already running")
                
                comm_port = mp.Process(target=self.accept_forever)
                comm_port.start()
                
            return self.server
    
    def accept_forever(self):
        print(f"Server started awaiting connection...")
        logger.info(f"Server started at {self.host} awaiting connection on port {self.port}")
        
        while self.__serve:
            conn, addr = self.server.accept()
            try:
                Worker = Thread(target=self.serve_connection, args=(conn, addr))
                Worker.start()
            except TimeoutError:
                print("even")
            
    def serve_connection(self, conn, addr):
        """Serve a single Connection
        """
        print(f"Connection to {addr} established succesfully in {current_thread().name}")
        logger.info(f"Connection to {addr} established succesfully in {current_thread().name}")
        
        while not self.terminate:
            try:
                h = format_recv_msg(conn, PACK_SIZE)
                self.RequestHandler(h, conn, addr, self.server)
                
            except ConnectionResetError:
                logger.warning(f"Connection {addr} has unexpectedly disconnected")
                conn.close()
                break
            
        print(f"{addr} has been severed succesfully")
        logger.warning(f"{addr} has been severed succesfully")


#TODO-----------------------------------------------------------------------------------------------------------------------
class BaseHandler:
    def __init__(self, h, conn, addr, server):
        self.h = h
        self.conn = conn
        self.addr = addr
        self.server = server
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
    def handler_name(self):
        return self.__class__.__name__

class FFT(BaseHandler):
    def setup(self):
        #remote_path = input("Path: ")
        remote_path = r"C:\Program Files (x86)\Intel\PackageManager"
        #self.local_path = input("Destination: ")
        self.local_path = r"C:\Users\moritz\Documents\IT\Server-Client\data"
        send_msg(self.conn, remote_path)
    
    def handle(self):
        while True:
            package = format_recv_msg(self.conn, PACK_SIZE)
            
            if package == "Done":
                print("Transfer Done!")
            
            if package[0] == "Folder":
                directory = os.path.join(self.local_path, package[1])
                os.makedirs(directory)
                print(f"Created {directory}")
                
                send_msg(self.conn, "Confirm")
            
            if package[0] == "File":
                directory = os.path.join(self.local_path, package[1])
                
                print(f"Writing File: {directory}")
                with open(directory, mode="wb+") as file:
                    file.write(package[2])
                print(f"Writing done!")
                
                send_msg(self.conn, "Confirm")

#Sliding Window Protocol
class SlidingWindowProtocol(BaseHandler):
    """
    QSocket like checksum at start
    End gets a hash of the file sent to compare if files are the same
    """
    def setup(self):
        pass
    
class ChatHandler(BaseHandler):
    def handle(self):
        while True:
            data = recv_msg(self.conn, PACK_SIZE)
            obj_len = struct.unpack(PACK_FMT, data)[0]
            obj_bytes = recv_msg(self.conn, obj_len)
            obj = pickle.loads(obj_bytes)
            print(obj)


class UniversalHandler():
    """The Universal Handler will attempt to "adapt" to the clients wishes
    
    Based on the request sent by the client it will switch to the coresponding Handler supplied to this class.
    This will allow handling of seperate connections in different ways
    """
    def __init__(self, request, conn, server, *args):
        pass
    
    def handle(self):
        pass