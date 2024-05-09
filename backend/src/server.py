import threading
import multiprocessing as mp
import os

import logging
import socket
import json

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
    __serve = True
    
    def __init__(self, host=str, port=int, Handler=object):
        self.host = host
        self.port = port
        self.RequestHandler = Handler
        if not hasattr(self.RequestHandler, "handle"):
            raise AttributeError
        
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
                
                comm_port = mp.Process(target=self.serve_forever)
                comm_port.start()
    
    def serve_forever(self):
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
        
        #handler = self.process_handle(request)
        
        #if handler is None:
        #    logger.warning(f"{addr}({threading.Thread.name}) has failed to provide existing handler, severing connection")
        #    conn.send(404)
        #    __keep_alive = False
        
        while __keep_alive:
            try:
                request = conn.recv(120)
                if not request:
                    continue
                
                #try:
                self.RequestHandler(request, conn, self.server)
                #except ValueError:
                #    logger.warn(f"ValueError")
                #    conn.close()
                
            except ConnectionResetError:
                logger.warning(f"Connection {addr} has unexpectadly disconnected")
                conn.close()
                break
            
        print(f"{addr} has been severed succesfully")
        logger.warning(f"{addr} has been severed succesfully")
    
    
    def process_handle(self, request):
        try:
            func = getattr(self.RequestHandler, request.decode())
            return func
            
        except AttributeError:
            return None
    
    
    def stop_worker(self):
        pass
        
    def shutdown(self):
        """Stop Main Server loop
        
        Must be called on the main Process 
        """
        self.__serve = False


class BaseHandler:
    def __init__(self, request, conn, server):
        self.request = request
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

class ChatHandler(BaseHandler):
    def setup(self):
        pass
    
    def handle(self):
        if isinstance(self.request.decode(), str):
            print(self.request.decode())
            return self.request
        else:
            self.conn.send(b"da")

class FileTransferHandler(BaseHandler):
    def __init__(self, request, conn, server, destination_path=str):
        self.path = destination_path
        super().__init__(request, conn, server)
    
    if hasattr(socket, "recvmsg"):
        def setup(self):
            self.floder, self.name = self.conn.recvmsg(10, 1000)
    else:
        def setup(self):
            self.floder, self.name = self.request.decode().split(":", 1)
    
    def handle(self):
        if self.floder == "Folder":
            try:
                os.mkdir(path=r""+{self.path}+"\"+{self.name}")
            except PermissionError:
                pass
        elif self.floder == "File":
            try:
                with open(file=self.name, mode="w+") as file:
                    content = self.conn.recv(100000000)
                    file.write(content.decode())
            except PermissionError:
                pass
                    
            
