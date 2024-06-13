import multiprocessing as mp
import os
import logging
import socket
import struct
import pickle
import queue
import socketserver
from concurrent.futures.thread import ThreadPoolExecutor

#! THREADPOLEXECUTER
import threading
#from threading import Thread, Event, Lock, current_thread
from core.src.util import send_msg, recv_msg, format_recv_msg

#! Call a file into pseudo memory and naviate like a list
import mmap

SERVER_NAME = "Git"
LOG_PATH = "./core/logs/" 


logger = logging.getLogger(name=SERVER_NAME)
logging.basicConfig(filename=f"{LOG_PATH}{SERVER_NAME}.log", encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
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
PACK_FMT = "!i"
PACK_SIZE = struct.calcsize(PACK_FMT)

class SocketServer(threading.Thread):
    """A Multithreaded Socket Server
    """
    def __init__(self, host=str, port=int, Handler=object):
        """
        Can be supplied with a custom Handler class(has to inherit the BaseHandler class). If no Handler class is suplied, it will default to
        the UniversalHandler
        """
        self.__serve = True
        self.terminate = threading.Event()
        
        self.host = host
        self.port = port
        self.RequestHandler = Handler or UniversalHandler
        
        if len(host) > 15:
            self.fam = socket.AF_INET6
        else:
            self.fam = socket.AF_INET
    
    def activate(self, block_main_thread=bool):
        """
        Convenience Function\n
        block_main_thread will decide wheter to stop the main thread and deal with the connections or
        to try and execute the connections at the same time
        """
        self.server = socket.socket(family=self.fam, type=socket.SOCK_STREAM)
        if self.server:
            try:
                self.server.bind((self.host, self.port))
                self.server.listen()
            except OSError:
                logger.info(f"Server is already running")
            
            #self.comm_port = threading.Thread(target=self.accept_forever, name="Comm-Port", args=(self.server, self.host, self.port))
            #self.comm_port.start()
    
    def accept_forever(self, sock=socket.socket, host=str, port=int):
        print(f"Server started awaiting connection...")
        logger.info(f"Server started at {host} awaiting connection on port {port}")
        while not self.terminate.is_set():
            conn, addr = sock.accept()
            
            try:
                #! Interpreter shutdown stops new threads
                Worker = threading.Thread(target=self.serve_connection, args=(sock, conn, addr), daemon=True)
                Worker.start()
            except ValueError as e:
                logger.error(f"Something went wrong, when trying to start a thread: {e}")
            except RuntimeError:
                self.accept_forever(sock, host, port)
            
    def serve_connection(self, sock, conn, addr):
        """Serve a single Connection
        """
        print(f"Connection to {addr} established succesfully in {threading.current_thread().name}")
        logger.info(f"Connection to {addr} established succesfully in {threading.current_thread().name}")
        
        while self.__serve:
            try:
                h = format_recv_msg(conn, PACK_SIZE)
                print(h)
                self.RequestHandler(h, conn, addr, sock)
                
            except ConnectionResetError:
                logger.warning(f"Connection {addr} has unexpectedly disconnected")
                conn.close()
                break
        print(f"{addr} has been severed succesfully")
        logger.warning(f"{addr} has been severed succesfully")
    
    def close(self, stdwn_code):
        self.terminate.set()
        self.comm_port.join()
        logger.critical(f"Server has been shutdown with code: {stdwn_code}")


#TODO-----------------------------------------------------------------------------------------------------------------------
class BaseHandler:
    def __init__(self, h, conn, addr, server):
        self.h = h
        self.conn = conn
        self.addr = addr
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

class FFT(BaseHandler):
    def setup(self):
        remote_path = r"C:\Program Files (x86)\Intel"
        self.local_path = r"C:\Users\moritz\Documents\IT\Server-Client\data"
        send_msg(self.conn, remote_path)
    
    def handle(self):
        while True:
            package = format_recv_msg(self.conn, PACK_SIZE)
            
            if package == "Done":
                print("Transfer Done!")
            
            if package[0] == "Folder":
                directory = os.path.join(self.local_path, package[1])
                os.makedirs(directory)
                print(f"Created {directory}")
                
                send_msg(self.conn, "Confirm")
            
            if package[0] == "File":
                directory = os.path.join(self.local_path, package[1])
                
                print(f"Writing File: {directory}")
                with open(directory, mode="wb+") as file:
                    file.write(package[2])
                print(f"Writing done!")
                
                send_msg(self.conn, "Confirm")

#Sliding Window Protocol
class SlidingWindowProtocol(BaseHandler):
    """
    QSocket like checksum at start
    End gets a hash of the file sent to compare if files are the same
    """
    def setup(self):
        pass
    
class ChatHandler(BaseHandler):
    def handle(self):
        while True:
            data = recv_msg(self.conn, PACK_SIZE)
            obj_len = struct.unpack(PACK_FMT, data)[0]
            obj_bytes = recv_msg(self.conn, obj_len)
            obj = pickle.loads(obj_bytes)
            print(obj)


class UniversalHandler():
    """The Universal Handler will attempt to "adapt" to the clients wishes
    
    Based on the request sent by the client it will switch to the coresponding Handler supplied to this class.
    This will allow handling of seperate connections in different ways
    """
    def __init__(self, request, conn, server, *args):
        pass
    
    def handle(self):
        pass