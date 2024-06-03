import struct
import pickle
from mmap import mmap
from multiprocessing import current_process

def recvallOLD(conn) -> bytes:
    package = conn.recv(600_000_000)
    package_size = package.split(b":::")[0]
    package = package.removeprefix(package_size + b":::")
    
    #! What happens if to much data
    while int(package_size) > len(package):
        chunk = conn.recv(600_000_000)
        package = package + chunk
        
    return package

def sure_send(conn, data=bytes):
    """
    Returns True if transmission was succesfull and returns False if transmission failed
    """
    if isinstance(data, bytes) is False:
        raise TypeError
    data_len = str(len(data))
    package = f"{data_len}:::{data}"
    package = data_len.encode() + b":::" + data
    
    try:
        conn.sendall(package)
        return True
    except InterruptedError:
        return False


def recv_msg(sock, n):
    PACK_FMT = "!i"
    PACK_SIZE = struct.calcsize(PACK_FMT)
    chunks = []
    received = 0
    while received < n:
        chunk = sock.recv(n - received)
        if len(chunk) == 0:
            raise BrokenPipeError("{}:{} [{}] Remote socket closed, Local {}, Remote {}".format(current_process().pid, sock.getsockname(), sock.getpeername()))
        chunks.append(chunk)
        received = received + len(chunk)
    return b''.join(chunks)

def send_msg(sock, obj):
    PACK_FMT = "!i"
    PACK_SIZE = struct.calcsize(PACK_FMT)
    
    obj_bytes = pickle.dumps(obj)
        
    obj_len = struct.pack(PACK_FMT, len(obj_bytes))
    buffer = b''.join((obj_len, obj_bytes))
    try:
        sock.sendall(buffer)
        return True
    except InterruptedError:
        return False


def format_recv_msg(sock, n):
    PACK_FMT = "!i"
    PACK_SIZE = struct.calcsize(PACK_FMT)
    
    data = recv_msg(sock, PACK_SIZE)
    obj_len = struct.unpack(PACK_FMT, data)[0]
    obj_bytes = recv_msg(sock, obj_len)
    obj = pickle.loads(obj_bytes)
    
    return obj