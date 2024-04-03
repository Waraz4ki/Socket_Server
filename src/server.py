import os
import multiprocessing as mp

import logging
import socket
import json
#from PIL.Image import Image

logger = logging.getLogger(__name__)
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
    
PORT = 60_000
HOST = "127.0.0.1"


class Socketserver:
    def __init__(self, host=str, port=int):
        with socket.socket(socket.AF_INET, type=socket.SOCK_STREAM) as self.server:
            self.server.bind((host, port))
            self.server.listen()
            __keep_alive__ = True
            
            print(f"Server started awaiting connection...")
            logger.info(f"Server started at {host} awaiting connection on port {port}")
            
            while __keep_alive__ is True:
                self.conn, self.addr = self.server.accept()
                
                print(f"Connection from {self.addr}")
                logger.info(f"Connection from {self.addr}")
                
                p = mp.Process(target=self.keep_connection)
                p.start()
    
                                    
    def keep_connection(self):
        print(f"Connection to {self.addr} established succesfully")
        logger.info(f"Connection to {self.addr} established succesfully")
        while True:
            try:
                recieved = self.conn.recv(1026)
                if recieved:
                    print(f"{self.addr[0]} sent: {recieved.decode()}")
                    logger.info(f"{self.addr[0]} sent: {recieved.decode()}")
                else:
                    pass
            except ConnectionResetError:
                logger.warning(f"Connection {self.addr} has unexpectadly disconnected")
                break
                #! Prozess muss hier terminiert werden sobald das geht

if __name__ == "__main__":
    Server = Socketserver(HOST, PORT)