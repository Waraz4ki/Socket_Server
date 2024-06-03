from os import path, makedirs

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

#Sliding Window Protocol
class SlidingWindowProtocol(BaseHandler):
    """
    QSocket like checksum at start
    End gets a hash of the file sent to compare if files are the same
    """
    def setup(self):
        pass

class FileTransferHandler(BaseHandler):
    """
    Manages a Transfer rate of about 6.5m/s
    """
    def setup(self):
        path_to_copy = input("Path to Copy: ")
        #path_to_copy = r"C:\Users\moritz\Documents\IT\Server-Client\node_modules"
        self.base_destination_path = r"C:\Users\moritz\Documents\IT\Server-Client\backend\data"
        sure_send(conn=self.conn, data=path_to_copy.encode())
        
    def handle(self):
        while True:
            self.request = recvall(conn=self.conn)
            self.request = self.request.split(b":::::")
            
            if self.request[0].decode() == "Folder":
                dest_path = path.join(self.base_destination_path, self.request[1].decode())
                makedirs(dest_path)
                
                self.conn.send(b"R")
                print("Confirm send")

            if self.request[0].decode() == "File":
                dest_path = path.join(self.base_destination_path, self.request[1].decode())
                
                with open(file=dest_path, mode="wb+") as file:
                    print("writing...")
                    file.write(self.request[2])
                    print("done writing")
                    
                    self.conn.send(b"R")
                    print("Confirm send")
                
class ChatHandler(BaseHandler):
    def handle(self):
        data = recvall(conn=self.conn)
        if isinstance(data.decode(), str):
            print(f"{self.addr}: {data.decode()}")
            return data.decode()
        else:
            self.conn.send(b"da")


class UniversalHandler():
    """The Universal Handler will attempt to "adapt" to the clients wishes
    
    Based on the request sent by the client it will switch to the coresponding Handler supplied to this class.
    This will allow handling of seperate connections in different ways
    """
    def __init__(self, request, conn, server, *args):
        pass
    
    def handle(self):
        pass