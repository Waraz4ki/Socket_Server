import time

def recvall(conn) -> bytes:
    package = conn.recv(600_000_000)
    package_size = package.split(b":::")[0]
    package = package.removeprefix(package_size + b":::")
    
    print(int(package_size))
    while not len(package) <= int(package_size):
        package.__add__(conn.recv(600_000_000))
    
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