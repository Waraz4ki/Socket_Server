import os
import threading
import multiprocessing as mp

import hashlib
import logging
import socket


SERVER_NAME = "example"

logger = logging.getLogger(name=SERVER_NAME)
logging.basicConfig(filename=f"{SERVER_NAME}.log", encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    
PORT = 60_000
HOST = "127.0.0.1"

class Socketserver:
    __keep_alive = True
    __safe = True
    
    def __init__(self, host=str, port=int):
        self.host = host
        self.port = port
        
        self.server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.server.bind((host,port))
        self.server.listen()
    
    def serve_forever(self):
        print(f"Server started awaiting connection...")
        logger.info(f"Server started at {self.host} awaiting connection on port {self.port}")
        
        while self.__keep_alive:
            self.conn, self.addr = self.server.accept()
            
            p = mp.Process(target=self.serve_connection, name=f"{self.addr[0]}")
            p.start()
        
    def serve_connection(self):
        connection = True
        
        print(f"Connection to {self.addr} established succesfully")
        logger.info(f"Connection to {self.addr} established succesfully")
        while connection:
            try:
                pass
            except ConnectionResetError:
                logger.warning(f"Connection {self.addr} has unexpectadly disconnected")
                break
        logger.info(f"{self.addr} has disconnected")
            
            
    def stop_connection(self, ip):
        for process in mp.active_children():
            if process.name == ip:
                process.close()


    def stop_all(self):
        pass
    
    
    def shutdown_request(self, requester):
        logger.info(f"{requester} sent a request to shut down server")
        
        
    def shutdown(self):
        """Stop Main Server loop
        
        Must be called on the main Process 
        """
        self.__keep_alive = False
        

if __name__ == "__main__":
    Server = Socketserver(HOST, PORT)
    Server.serve_forever()