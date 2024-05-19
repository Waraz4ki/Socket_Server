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
        
        while __keep_alive:
            try:
                request = recvall(conn, 1024)
                
                path = r"C:\Users\moritz\Documents\IT\Server-Client\backend\data"
                self.RequestHandler(request, conn, self.server, path)
                
            except ConnectionResetError:
                logger.warning(f"Connection {addr} has unexpectadly disconnected")
                conn.close()
                break
            
        print(f"{addr} has been severed succesfully")
        logger.warning(f"{addr} has been severed succesfully")
    
    def stop_worker(self):
        pass
        
    def shutdown(self):
        """Stop Main Server loop
        
        Must be called on the main Process 
        """
        self.__serve = False


class BaseHandler:
    def __init__(self, request, conn, server, *args):
        self.request = request
        self.conn = conn
        self.server = server
        self.args = args
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

class FileTransferHandlerNew(BaseHandler):
    def setup(self):
        self.base_destination_path = self.args[0]
        self.r = self.request.split(b":::::")
        
    def handle(self):
        if self.r[0].decode() == "Folder":
            dest_path = os.path.join(self.base_destination_path, self.r[1].decode())
            
            os.makedirs(dest_path)
        
        elif self.r[0].decode() == "File":
            dest_path = os.path.join(self.base_destination_path, self.r[1].decode())
            
            with open(file=dest_path, mode="wb+") as file:
                #print(self.r[2])
                file.write(self.r[2])
                
        print("Sending Confirmation")
        sure_send(self.conn, b"Done")
        #self.conn.send(b"Done")


class ChatHandler(BaseHandler):
    def setup(self):
        pass
    
    def handle(self):
        if isinstance(self.request.decode(), str):
            print(self.request)
            return self.request
        else:
            self.conn.send(b"da")

