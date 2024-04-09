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

"""Two Part Server
On execution, main component will create seperate process which is supposed to act as the com port.
Com port will recieve connections and such....

Main part will handle certaint commands like conneciton kill or such
Connections are Threaded

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



class Socketserver:
    __keep_alive = True
    
    def __init__(self, host=str, port=int):
        self.host = host
        self.port = port
        
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as self.server:
            self.server.bind((host,port))
            self.server.listen()
            
            mp.Process(target=self.serve_forever, name="Comm-port").start()

    def serve_forever(self):
        print(f"Server started awaiting connection...")
        logger.info(f"Server started at {self.host} awaiting connection on port {self.port}")
        
        while self.__keep_alive:
            self.conn, self.addr = self.server.accept()
            
            t = (self.conn, self.addr)
            
            con = threading.Thread(target=self.serve_connection, args=(self.conn, self.addr))
            con.start()
            
    def serve_connection(self, conn, addr):
        print(f"Connection to {addr} established succesfully")
        logger.info(f"Connection to {addr} established succesfully")
        while True:
            try:
                raw = conn.recv(12312)
                print(f"{threading.currentThread().getName()}: {raw}")
            except ConnectionResetError:
                logger.warning(f"Connection {addr} has unexpectadly disconnected")
                break            
            
    def stop_connection(self, ip):
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
        

if __name__ == "__main__":
    Server = Socketserver(HOST, PORT)