from asocket import ASocket
from os import path, makedirs
import mmap


class BaseHandler(ASocket):
    def __init__(self, sock, addr):
        super().__init__(sock)
        self.addr = addr
        try:
            self.send_msg(sock, self.handler_name)
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
    def handler_name(self):
        return self.__class__.__name__
        #return self.__class__.__name__.removesuffix("Handler")
    
class ChatHandler(BaseHandler):
    def handle(self):
        while True:
            data = self.format_recv_msg(self.sock, self.PACK_SIZE)
            print(f"{self.addr}: {data}")

class FFTHandler(BaseHandler):
    def setup(self):
        remote_path = input(">>>")
        self.send_msg(self.sock, remote_path)
        self.root_path = input(">>>")
        #self.root_path = r"C:\Users\moritz\Documents\IT\Server-Client\data"
    
    def handle(self):
        while True:
            package = self.format_recv_msg(self.sock, self.PACK_SIZE)
            print(package)
            partial_path = package["path"]
            package_type = package["type"]
            name = package["name"]
            try:
                makedirs(path.join(self.root_path, partial_path))
            except FileExistsError:
                pass
            
            if package_type == "folder":
                absolute_path = path.join(self.root_path, partial_path, name)
                makedirs(absolute_path)
                self.send_msg(self.sock, True)
            
            if package_type == "file":
                absolute_path = path.join(self.root_path, partial_path, name)
                self.send_msg(self.sock, True)
                
                with open(file=absolute_path, mode="wb+") as file:
                    while True:
                        #print("LOOP")
                        chunck = self.format_recv_msg(self.sock, self.PACK_SIZE)
                        if chunck == 200 or chunck is None:
                            print("EXIT")
                            break
                        file.write(chunck)
                        