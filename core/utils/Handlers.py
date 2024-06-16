from asocket import ASocket
from os import path, makedirs
import mmap


class BaseHandler(ASocket):
    def __init__(self, sock, addr):
        super().__init__(sock)
        self.addr = addr
        
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
        return self.__class__.__name__.removesuffix("Handler")
    
class ChatHandler(BaseHandler):
    def handle(self):
        while True:
            data = self.format_recv_msg(self.sock, self.PACK_SIZE)
            print(f"{self.addr}: {data}")

class FFTHandler(BaseHandler):
    def setup(self):
        remote_path = input(">>>")
        self.send_msg(self.sock, remote_path)
        self.root_path = r"C:\Users\moritz\Documents\IT\Server-Client\data"
    
    def handle(self):
        while True:
            package = self.format_recv_msg(self.sock, self.PACK_SIZE)
            print(package)
            if package == 200 or package == 404:
                print("Stopping...")
                break
            print(package)
            package_type = package["type"]
            partial_path = package["path"]
            buffer = package["buffer"]
            content_size = package["content_size"]
            
            if package_type == "folder":
                absolute_path = path.join(self.root_path, partial_path)
                makedirs(absolute_path)
                print("e5hj5he")
                self.send_msg(self.sock, True)
            
            if package_type == "file":
                absolute_path = path.join(self.root_path, partial_path)
                
                self.recv_file(absolute_path, "wb+", buffer, content_size)
    
    def recv_file(self, path, mode, buffer, size):
        with open(file=path, mode=mode) as file:
            while True:
                chunck = self.format_recv_msg(self.sock, self.PACK_SIZE)
                if not chunck:
                    break
                file.write(chunck)