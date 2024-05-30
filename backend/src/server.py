import threading
import multiprocessing as mp
import os
import logging
import socket
import json
import time

from backend.src.util import sure_send, recvall 

SERVER_NAME = "example"

logger = logging.getLogger(name=SERVER_NAME)
logging.basicConfig(filename=f"{SERVER_NAME}.log", encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
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


class SocketServer():
    """A Multithreaded Socket Server
    """
    __serve = True
    
    def __init__(self, host=str, port=int, Handler=object):
        """
        Can be supplied with a custom Handler class(has to inherit the BaseHandler class). If no Handler class is suplied, it will default to
        the UniversalHandler
        """
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
    
    def accept_forever(self):
        print(f"Server started awaiting connection...")
        logger.info(f"Server started at {self.host} awaiting connection on port {self.port}")
        
        while self.__serve:
            conn, addr = self.server.accept()
            try:
                Worker = threading.Thread(target=self.serve_connection, args=(conn, addr))
                Worker.start()
            except TimeoutError:
                print("even")
            
    def serve_connection(self, conn, addr):
        __keep_alive = True 
        """Serve a single Connection
        """
        print(f"Connection to {addr} established succesfully in {threading.current_thread().name}")
        logger.info(f"Connection to {addr} established succesfully in {threading.current_thread().name}")
        
        while __keep_alive:
            try:
                h = recvall(conn=conn)
                print("Request recieved")

                #path = r"C:\Users\moritz\Documents\IT\Server-Client\backend\data"
                self.RequestHandler(h, conn, self.server)
                
            except ConnectionResetError:
                logger.warning(f"Connection {addr} has unexpectadly disconnected")
                conn.close()
                break
            
        print(f"{addr} has been severed succesfully")
        logger.warning(f"{addr} has been severed succesfully")

    def get_protocol(self, conn):
        return conn.recv(1024)


#TODO-----------------------------------------------------------------------------------------------------------------------
class BaseHandler:
    def __init__(self, h, conn, server):
        self.h = h
        self.conn = conn
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

class FileTransferHandler(BaseHandler):
    def setup(self):
        path_to_copy = r"C:\Program Files (x86)\Intel"
        self.base_destination_path = r"C:\Users\usename\Documents\IT\Server-Client\backend\data"
        sure_send(conn=self.conn, data=path_to_copy.encode())
        
    def handle(self):
        while True:
            self.request = recvall(conn=self.conn)
            self.request = self.request.split(b":::::")
            
            if self.request[0].decode() == "Folder":
                dest_path = os.path.join(self.base_destination_path, self.request[1].decode())

                os.makedirs(dest_path)
                self.conn.send(b"R")
                print("Confirm send")

            if self.request[0].decode() == "File":
                dest_path = os.path.join(self.base_destination_path, self.request[1].decode())

                with open(file=dest_path, mode="wb+") as file:
                    print("writing...")
                    file.write(self.request[2])
                    print("done writing")

                    self.conn.send(b"R")
                    print("Confirm send")
                
class ChatHandler(BaseHandler):
    def setup(self):
        pass
    
    def handle(self):
        if isinstance(self.h.decode(), str):
            print(self.h)
            return self.h
        else:
            self.conn.send(b"da")


class UniversalHandler():
    """The Universal Handler will attempt to "adapt" to the clients wishes
    
    Based on the request sent by the client it will switch to the coresponding Handler supplied to this class.
    This allows the Universal Handler to Handle every connection in a different way
    """
    def __init__(self, request, conn, server, *args):
        pass
    
    def handle(self):
        pass