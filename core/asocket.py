import socket
import struct
import pickle
import threading
from utils.thread_manager import ThreadManager

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
    
    def recv_msg(self, sock, n) -> bytes:
        chunks = []
        received = 0
        while received < n:
            chunk = sock.recv(n - received)
            if len(chunk) == 0:
                raise BrokenPipeError(f"{threading.current_thread()}:{self.sock.getsockname()}")
            chunks.append(chunk)
            received = received + len(chunk)
        return b''.join(chunks)
    
    def format_recv_msg(self, sock, n) -> object:
        data = self.recv_msg(sock, n)
        obj_len = struct.unpack(self.PACK_FMT, data)[0]
        obj_bytes = self.recv_msg(sock, obj_len)
        obj = pickle.loads(obj_bytes)

        return obj



class AServer(ASocket):
    manager = ThreadManager()
    def __init__(self, host, port, handler_class, timeout:int | None=None):
        self.host = host
        self.port = port
        self.handler = handler_class
        self.terminate = threading.Event()
        
        #self.sock = create_socket(self.host)
        super().__init__(create_socket(self.host))
        self.sock.settimeout(timeout)
        
        try:
            self.sock.bind((host, port))
        except Exception as e:
            print(e)
            
    def activate(self, recieve:bool | None=False):
        if self.sock:
            try:
                self.sock.listen()
                if recieve:
                    comm_port = threading.Thread(target=self.recieve_connections)
                    comm_port.start()
            except OSError as e:
                print(e)
    
    def recieve_connections(self):
        print("Server awaiting connections")
        while not self.terminate.is_set():
            try:
                conn, addr = self.sock.accept()
                worker = threading.Thread(target=self.serve_connection, args=(conn, addr))
                self.manager.start(worker)
            except TimeoutError:
                pass
    
    @manager.thread_loop
    def serve_connection(self, conn, addr):
        try:
            #handler = self.format_recv_msg(conn, self.PACK_SIZE)
            print("START")
            self.handler(conn, addr)
        except ConnectionResetError or TimeoutError or OSError as e:
            print("Closing Connection")
            self.manager.stop(threading.current_thread().name)
            conn.close()
    
    def stop_all(self):
        """
        Shuts down every worker
        """
        self.manager.stop_all()
    
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
        self.conn.connect((self.host, self.port))
        print("Connection Succesfull")
        while True:
            try:
                self.protocol(self.conn, self.addr)
            except ConnectionRefusedError:
                continue
    
    def handle(self):
        pass
