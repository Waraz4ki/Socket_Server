import threading
import multiprocessing as mp

import logging
import socket

from handler import Handler

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

class Socketserver:
    __keep_alive = True
    
    def __init__(self, host=str, port=int):
        self.host = host
        self.port = port

        self.server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.server.bind((host,port))
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

        Args:
            conn (_type_): _description_
            addr (_type_): _description_
        """
        print(f"Connection to {addr} established succesfully in {threading.current_thread()}")
        logger.info(f"Connection to {addr} established succesfully in {threading.current_thread()}")
        
        handler = self.get_handler(conn=conn, addr=addr)
        h = Handler(purpose=handler)
        
        while True:
            try:
                raw = conn.recv(12312)
                h.init(raw.decode())
                
            except ConnectionResetError:
                logger.warning(f"Connection {addr} has unexpectadly disconnected")
                break            
    
    def get_handler(self, conn, addr):
        """Request way to handle sent items

        Args:
            conn (socket): socket obj
            addr (_RetAddress): address of the connected machine

        Returns a string containing the way to handle the items sent
        """
        conn.send(b"Gime")
        handler = conn.recv(75).decode()
        
        return handler
    
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
        

if __name__ == "__main__":
    Server = Socketserver(HOST, PORT)