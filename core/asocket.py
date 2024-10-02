import socket
import struct
import pickle
import threading
import logging

from core.utils.thread_manager import ThreadManager
from core.utils.other import compareObjectNameToString

def create_socket(host):
    if len(host) > 15:
        sock_family = socket.AF_INET6
    else:
        sock_family = socket.AF_INET
    return socket.socket(family=sock_family, type=socket.SOCK_STREAM)
    
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',)


class ASocket():
    PACK_FMT = "!i"
    PACK_SIZE = struct.calcsize(PACK_FMT)
    
    DATA_TRANSMISSION = "DATA"
    FINISH_TRANSMISSION = "FINISH"
    
    def __init__(self, sock:socket.socket | None=None):
        if sock:
            self.sock_obj = sock
        else:
            self.sock_obj = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.timeout = self.sock_obj.timeout
    
    def send_msg(self, trans_type:str | None=DATA_TRANSMISSION, obj:object | None=None):
        obj_bytes = pickle.dumps(obj)
        obj_len = struct.pack(ASocket.PACK_FMT, len(obj_bytes))
        
        header = pickle.dumps(trans_type)
        header_len = struct.pack(ASocket.PACK_FMT, len(header))
        
        buffer = b''.join((header_len, header, obj_len, obj_bytes))
        self.sock_obj.sendall(buffer)
        
    def send_msg_to(self, host:str , port:int, obj:object | None=None, trans_type:str | None=DATA_TRANSMISSION):
        obj_bytes = pickle.dumps(obj)
        obj_len = struct.pack(ASocket.PACK_FMT, len(obj_bytes))
        
        header = pickle.dumps(trans_type)
        header_len = struct.pack(ASocket.PACK_FMT, len(header))
        
        buffer = b''.join((header_len, header, obj_len, obj_bytes))
        self.sock_obj.sendto(buffer, (host, port))
    
    def recv_msg(self, n:float | None=PACK_SIZE) -> bytes:
        chunks = []
        received = 0
        while received < n:
            chunk = self.sock_obj.recv(n - received)
            if len(chunk) == 0:
                raise BrokenPipeError(f"{threading.current_thread()}:{self.sock_obj.getsockname()}")
            chunks.append(chunk)
            received = received + len(chunk)
        return b''.join(chunks)
    
    def format_recv_msg(self) -> object:
        serialized_data = self.recv_msg()
        header_len = struct.unpack(self.PACK_FMT, serialized_data)[0]
        serialized_header = self.recv_msg(header_len)
        header = pickle.loads(serialized_header)
        
        serialized_data = self.recv_msg()
        obj_len = struct.unpack(self.PACK_FMT, serialized_data)[0]
        serialized_obj = self.recv_msg(obj_len)
        obj = pickle.loads(serialized_obj)

        return header, obj
    
    def kill(self, how:int | None=socket.SHUT_RDWR):
        self.sock_obj.shutdown(how)
        self.sock_obj.close()


class Connection_Framework(ASocket):
    CONNECTION_SHARE = "SHARE_CONN"
    HANDLER_AUTH_TRANSMISSION = "HANDLER_AUTH"
    
    def __init__(self, sock: socket.socket | None = None):
        super().__init__(sock)
    
    def bind(self, address):
        self.sock_obj.bind(address)
        
    def listen(self, backlog):
        self.sock_obj.listen(backlog)
    
    def accept(self):
        return self.sock_obj.accept()
    
    def connect(self, address):
        self.sock_obj.connect(address)

    
    def format_recv_msg(self) -> object:
        serialized_data = self.recv_msg()
        header_len = struct.unpack(self.PACK_FMT, serialized_data)[0]
        serialized_header = self.recv_msg(header_len)
        header = pickle.loads(serialized_header)
        
        serialized_data = self.recv_msg()
        obj_len = struct.unpack(self.PACK_FMT, serialized_data)[0]
        serialized_obj = self.recv_msg(obj_len)
        obj = pickle.loads(serialized_obj)

        if header == self.HANDLER_AUTH_TRANSMISSION:
            raise ReferenceError(header, obj)
        
        return header, obj

class AServer():
    manager = ThreadManager()
    
    def __init__(self, sock:Connection_Framework, host:str, port:int, handler_classes:tuple | None=None):
        self.sock = sock
        self.host = host
        self.port = port
        self.handlers = handler_classes
        
        self.terminate = threading.Event()
        self.connections = []
        
        self.sock.bind((self.host, self.port))
     
    def activate(self, recieve:bool | None=False, backlog:int | None=0):
        self.sock.listen(backlog)
        if not recieve:
            return
        # Spawn new thread to recieve all the incoming connections
        comm_port = threading.Thread(target=self.recieve_connections)
        comm_port.start()
    
    def recieve_connections(self):
        logging.info("Server awaiting connections")
        while not self.terminate.is_set():
            try:
                conn, addr = self.sock.accept()
                # Spawn thread and handle
                worker = threading.Thread(target=self.setup_connection, args=(conn, addr))
                # Easy to stop newly spawned threads by using ThreadManager
                self.manager.start(worker)
            except TimeoutError:
                continue
        logging.info("Server has been shutdown")
        logging.debug("Server has been shutdown")
    
    def setup_connection(self, conn:socket.socket, addr):
        self.connections.append(addr)
        sock = ASocket(conn)
        
        logging.info(f"Connection established to {addr}")
        logging.debug(f"Connection established to {addr}")
        header, recv_handler = sock.format_recv_msg()
        # Check if send handler name is in the tuple given to the AServer Class
        handler = compareObjectNameToString(self.handlers, recv_handler)
        if not handler or header != self.sock.HANDLER_AUTH_TRANSMISSION:
            self.stop_current_worker(sock, f"Frocibly closing connection to {addr}: Specified handler does not exist")
            
        self.serve_connection(sock, addr, handler)
    
    @manager.thread_loop
    def serve_connection(self, sock:Connection_Framework, addr, handler):
        """
        Serve a connection
        """
        
        try:
            handler(sock, addr)
        # Checks if the connected maschine is still there  
        except ConnectionResetError:
            self.stop_current_worker(sock, f"{addr} has closed the connection")
    
    def transfer_connection(self, remote_host, remote_port, conn:Connection_Framework):
        logging.info("Transfering connection...")
        conn.send_msg(self.sock.HANDLER_AUTH_TRANSMISSION, (remote_host, remote_port))
        logging.info("Success!")
    
    def stop_current_worker(self, sock:ASocket, local_msg:object | None="Something went wrong", how:int | None=socket.SHUT_RDWR):
        """
        Shuts down current worker
        """
        sock.kill(how)
        logging.warn(local_msg)
        self.manager.stop_current() # Stops current worker
    
    def stop_worker(self, worker):
        """
        Shuts down a single connection
        """
        self.manager.stop(worker)
    
    def stop_all(self):
        """
        Shuts down every worker
        """
        self.manager.stop_all()
    
    def shudown(self):
        """
        Shuts down entire server
        """
        logging.info("Shutting down server...")
        logging.debug("Shutting down server...")
        self.stop_all()
        self.terminate.set()
        self.sock.kill()

class AClient():
    def __init__(self, sock:Connection_Framework, host, port, protocol_class):
        self.sock = sock
        self.host = host
        self.port = port
        self.protocol = protocol_class
        
    def connect(self):
        logging.info("Attempting to connect...")
        self.sock.connect((self.host, self.port))
        logging.info("Connection Succesfull!")
        
    def reconnect(self):
        logging.warning("Reconnecting...")
        while True:
            try:
                self.sock.connect((self.host, self.port))
            except ConnectionRefusedError:
                logging.error("Connection was refused...")
        
    def change_connection(self, host, port):
        self.disconnect()
        
        self.host = host
        self.port = port
        
        logging.info("Changing connection...")
        self.sock.connect((self.host, self.port))
        logging.info("Change succesfull!")
    
    def setup(self):
        self.sock.send_msg(self.sock.HANDLER_AUTH_TRANSMISSION, self.protocol.opposite_name(self.protocol.__name__))
        
    def handle(self):
        while True:
            try:
                self.protocol(self.sock, self.host)
            
            except ReferenceError as transfer_data:
                print("wda")
                print(transfer_data.args[1])
                transfer_header = transfer_data.args[0]
                transfer_content = transfer_data.args[1]
                self.change_connection(transfer_content[0], transfer_content[1])
            
            except ConnectionResetError:
                self.reconnect()
            except ConnectionRefusedError:
                continue
    
    def disconnect(self):
        """
        Close current socket and create a new one\n
        New socket is directly applied to local socket
        """
        self.sock.sock_obj.close()
        self.sock = Connection_Framework()