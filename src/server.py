import threading
import multiprocessing as mp

import concurrent.futures
#from concurrent.futures import ProcessPoolExecutor

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
        self.Handler = Handler()
    
    def activate(self):
        """Will initiate the server and await connections
        """
        self.server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        
        d = threading.Thread(target=self.serve_forever)
        d.start()
        #self.serve_forever()
    
    def serve_forever(self):
        print(f"Server started awaiting connection...")
        logger.info(f"Server started at {self.host} awaiting connection on port {self.port}")
        
        while self.__serve:
            conn, addr = self.server.accept()
            
            try:
                Worker = threading.Thread(target=self.serve_connection, args=(conn, addr))
                Worker.run()
            except TimeoutError:
                pass
                        
    def serve_connection(self, conn, addr):
        __keep_alive = True
        """Serve a single Connection
        """
        print(f"Connection to {addr} established succesfully in {threading.current_thread().name}")
        logger.info(f"Connection to {addr} established succesfully in {threading.current_thread().name}")
        
        request = conn.recv(1000)
        handler = self.process_handle(request)
        
        if handler is None:
            logger.warning(f"{addr}({threading.Thread.name}) has failed to provide existing handler, severing connection")
            __keep_alive = False
        
        while __keep_alive:
            try:
                raw = conn.recv(120)
                
                try:
                    handler(data=raw)
                except AttributeError:
                    logger.critical(f"{addr} has surpassed first check, severing connection")
                    break
                
            except ConnectionResetError:
                logger.warning(f"Connection {addr} has unexpectadly disconnected")
                break
        logger.warning(f"{addr} has been severed succesfully")
    
    def process_handle(self, request):
        try:
            func = getattr(self.Handler, request.decode())
            return func
            
        except AttributeError:
            #! Kill connection here
            return None
    
    def stop_worker(self, ip):
        for process in mp.active_children():
            if process.name == ip:
                process.close()

    def stop_all(self):
        pass
        
    def shutdown(self):
        """Stop Main Server loop
        
        Must be called on the main Process 
        """
        self.__keep_alive = False
        