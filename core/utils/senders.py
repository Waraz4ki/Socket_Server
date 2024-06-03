from pathlib import Path
import os

class BaseProtocol:
    def __init__(self, conn):
        self.conn = conn
        try:
            sure_send(conn=self.conn, data=self.protocol_name.encode())
            #time.sleep(1)
        except ConnectionError:
            pass
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
    def protocol_name(self):
        return self.__class__.__name__

class ChatProtocol(BaseProtocol):
    def handle(self):
        raw = input(">>>")
        sure_send(conn=self.conn, data=raw.encode())
    
class FileFolderTransferProtocol(BaseProtocol):
    def setup(self):
        self.path_to_copy = recvall(conn=self.conn).decode()
        print(self.path_to_copy)
    
    def handle(self):
        self.do(self.path_to_copy)
    
    def do(self, current_dir):
        for dir in os.scandir(current_dir):
            new = dir.path.split("\\")
            
            for i in range(len(self.path_to_copy.split("\\"))-1):
                del new[0]
                  
            package = str(Path.joinpath(Path(*new)))
            print(package)
            
            if dir.is_dir():
                full_package = f"Folder:::::{package}"
                sure_send(self.conn, full_package.encode())
                print("Package send")
                
                verify_recv = self.conn.recv(1)
                if verify_recv.decode() == "R":
                    print("Server Confirmed")
                    self.do(dir.path)
                    continue
                
            if dir.is_file():
                with open(file=dir, mode="rb") as file:
                    full_package = b"File:::::" + package.encode() +b":::::"+ file.read()
                    sure_send(self.conn, full_package)
                    print("Package send")
                
                verify_recv = self.conn.recv(1)
                if verify_recv.decode() == "R":
                    print("Server Confirmed")
                    pass
