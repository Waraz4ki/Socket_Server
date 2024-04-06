import os
import threading
import multiprocessing as mp

import hashlib
import logging
import socket
import socketserver
import json

SERVER_NAME = "example"

logger = logging.getLogger(name=SERVER_NAME)
logging.basicConfig(filename=f"{SERVER_NAME}.log", encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    
PORT = 60_000
HOST = "127.0.0.1"

class Socketserver:
    __keep_alive = True
    __safe = True
    
    def __init__(self, host=str, port=int):
        try:
            with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as self.server:
                self.server.bind((host, port))
                self.server.listen()

                print(f"Server started awaiting connection...")
                logger.info(f"Server started at {host} awaiting connection on port {port}")

                while self.__keep_alive:
                    self.conn, self.addr = self.server.accept()

                    print(f"Connection from {self.addr}")
                    logger.info(f"Connection from {self.addr}")

                    p = mp.Process(target=self.serve_connection, name=f"{self.addr[0]}")
                    p.start()
                    
        except Exception:
            self.__keep_alive = True
            self.server.close()
            logger.warning(f"Server has encountered unexpected error {Exception}")
    

    def serve_connection(self):
        self.__sever_connection_request = False
        
        print(f"Connection to {self.addr} established succesfully")
        logger.info(f"Connection to {self.addr} established succesfully")
        while self.__safe:
            try:
                pass
            except ConnectionResetError:
                logger.warning(f"Connection {self.addr} has unexpectadly disconnected")
                break
            
    
#    def verify_connection(self):
#        try:
#            pwrd = hashlib.sha256(self.server.recv(1026), usedforsecurity=True)
#            if pwrd == hashlib.sha256(PAS, usedforsecurity=True):
#                self.__safe__ = True
#        except:
#            pass
    
        
    def sever_connection(self):
        for process in mp.active_children():
            print(process)
        
        ##return self.__sever_connection_request

    def sever_all(self):
        self.__safe = False
    
    
    def shutdown(self):
        """Stop Main Server loop
        
        Must be called on the main Process 
        """
        self.__keep_alive = False
        
         
    
if __name__ == "__main__":
    Server = Socketserver(HOST, PORT)