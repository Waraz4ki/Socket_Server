import socket
import struct
import pickle
import threading
from utils.thread_manager import ThreadManager
from utils.other import other


def create_socket(host):
    if len(host) > 15:
        sock_family = socket.AF_INET6
    else:
        sock_family = socket.AF_INET
    return socket.socket(family=sock_family, type=socket.SOCK_STREAM)
    

class ASocket(threading.Thread):
    PACK_FMT = "!i"
    PACK_SIZE = struct.calcsize(PACK_FMT)
    
    def __init__(self, sock):
        self.sock = sock
    
    def send_msg(self, sock, obj:object):
        obj_bytes = pickle.dumps(obj)

        obj_len = struct.pack(ASocket.PACK_FMT, len(obj_bytes))
        buffer = b''.join((obj_len, obj_bytes))
        try:
            sock.sendall(buffer)
            return True
        except InterruptedError:
            return False
    
    def recv_msg(self, sock, n:float | None=PACK_SIZE) -> bytes:
        chunks = []
        received = 0
        while received < n:
            chunk = sock.recv(n - received)
            if len(chunk) == 0:
                raise BrokenPipeError(f"{threading.current_thread()}:{self.sock.getsockname()}")
            chunks.append(chunk)
            received = received + len(chunk)
        return b''.join(chunks)
    
    def format_recv_msg(self, sock) -> object:
        data = self.recv_msg(sock)
        obj_len = struct.unpack(self.PACK_FMT, data)[0]
        obj_bytes = self.recv_msg(sock, obj_len)
        obj = pickle.loads(obj_bytes)

        return obj



class AServer(ASocket):
    manager = ThreadManager()
    def __init__(self, host:str | None=None, port:int | None=None, handler_classes:tuple | None=None, timeout:int | None=5):
        self.host = host
        self.port = port
        self.handlers = handler_classes
        self.terminate = threading.Event()
        
        super().__init__(create_socket(self.host))
        self.sock.settimeout(timeout)
        
        self.sock.bind((self.host, self.port))
            
    def activate(self, recieve:bool | None=False):
        try:
            self.sock.listen()
            if recieve:
                # Spawn new thread to recieve all the incoming connections
                comm_port = threading.Thread(target=self.recieve_connections)
                comm_port.start()
        except Exception as e:
            print(e)
    
    def recieve_connections(self):
        print("Server awaiting connections")
        while not self.terminate.is_set():
            try:
                conn, addr = self.sock.accept()
                # Spawn thread and handle
                worker = threading.Thread(target=self.serve_connection_recursive, args=(conn, addr))
                # Easy to stop newly spawned threads by using ThreadManager
                self.manager.start(worker)
            except TimeoutError:
                continue
        print("Server has been shutdown")
    
    @manager.thread_loop
    def serve_connection_recursive(self, conn, addr):
        """
        Serve a connection
        """
        #print(f"Connection to {addr} has been established")
        try:
            package = self.format_recv_msg(conn)
            recv_handler = package["type"]
            # Check if send handler name is in the tuple given to the AServer Class
            handler = other.compareObjectNameToString(self.handlers, recv_handler)
            if handler:
                handler(conn, addr, package)
            else:
                self.stop_current(conn, addr, f"Frocibly closing connection to {addr}", NotImplementedError)
        # Checks if the connected maschine is still there
        except ConnectionResetError as e:
            self.stop_current(conn, addr, f"{addr} has closed the connection", e)
    
    def stop_current(self, sock, addr, local_msg:object | None="Something went wrong", remote_msg:object | None=Exception):
        """
        Shuts down current worker
        """
        try:
            self.send_msg(sock, remote_msg)
        except ConnectionResetError:
            # If this error is caught, the Connected maschine has closed the connection
            pass
        sock.close()
        print(local_msg)
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
        self.stop_all()
        self.terminate.set()
    
    @property
    def active_workers(self):
        return self.manager.thread_list


class AClient(ASocket):
    def __init__(self, host, port, protocol_class):
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.protocol = protocol_class
        
        self.conn = create_socket(self.host)
        super().__init__(self.conn)
        
    def connect(self):
        print("Attempting to connect")
        self.conn.connect(self.addr)
        print("Connection Succesfull")
    
    def handle(self):
        while True:
            try:
                self.protocol(self.conn, self.addr)
            except ConnectionRefusedError:
                continue
    
    def handle_recursive(self):
        while True:
            package = {
                "type":None,
                "data":None,
            }
            package["type"] = self.protocol.opposite_name(self.protocol.__name__)
            try:
                self.protocol(self.conn, self.addr, package)
            except ConnectionRefusedError:
                pass
