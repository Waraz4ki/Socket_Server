import threading
import multiprocessing as mp

import logging
import socket
import json

#from handler import Serverhandler

SERVER_NAME = "example"

logger = logging.getLogger(name=SERVER_NAME)
logging.basicConfig(filename=f"{SERVER_NAME}.log", encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    
PORT = 60_000
HOST = "192.168.178.108"

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
    __keep_alive = True
    
    def __init__(self, host=str, port=int, Handler=object):
        self.host = host
        self.port = port
        self.Handler = Handler

        self.server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        
        Comm_port = mp.Process(target=self.serve_forever, name="Comm-port")
        Comm_port.start()

    def serve_forever(self):
        print(f"Server started awaiting connection...")
        logger.info(f"Server started at {self.host} awaiting connection on port {self.port}")
        
        while self.__keep_alive:
            conn, addr = self.server.accept()
            
            Worker = threading.Thread(target=self.serve_connection, args=(conn, addr))
            Worker.start()
            
    def serve_connection(self, conn, addr):
        """Serve a single Connection
        """
        print(f"Connection to {addr} established succesfully in {threading.current_thread()}")
        logger.info(f"Connection to {addr} established succesfully in {threading.current_thread()}")
        
        request = conn.recv(1000)
        handler = self.process_handle(request)
        
        while True:
            try:
                raw = conn.recv(120)
                self.handle_request(raw, handler)
                
            except ConnectionResetError:
                logger.warning(f"Connection {addr} has unexpectadly disconnected")
                break
    
    def process_handle(self, request):
        try:
            func = getattr(self.Handler, request.decode())
            return func
            
        except AttributeError:
            #! Kill connection here
            print("efau")
            return None
    
    def handle_request(self, raw, handler):
        handler(data=raw)
        
    def stop_worker(self, ip):
        for process in mp.active_children():
            if process.name == ip:
                process.close()

    def stop_all(self):
        mp.active_children()[0].terminate()
        logger.info(f"Comm Port has succesfully been terminated...")
        
        mp.Process(target=self.serve_forever, name="Comm-port").start()
        
    def shutdown(self):
        """Stop Main Server loop
        
        Must be called on the main Process 
        """
        self.__keep_alive = False
        