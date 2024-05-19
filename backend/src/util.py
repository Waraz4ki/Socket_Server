import time

def recvall(conn, buffsize=None) -> bytes:
    package = conn.recv(500_000_000)
    package_size = package.split(b":::")[0]
    package = package.removeprefix(package_size + b":::")
    
    while len(package) != int(package_size):
        package.__add__(conn.recv(500_000_000))
        
    return package


def sure_send(conn, data=bytes):
    if isinstance(data, bytes) is False:
        raise TypeError
    data_len = str(len(data))
    package = f"{data_len}:::{data}"
    package = data_len.encode() + b":::" + data
    
    try:
        conn.sendall(package)
        #time.sleep(2)
    except InterruptedError:
        return "Not everything was send"