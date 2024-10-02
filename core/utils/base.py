from core.asocket import ASocket

class Base():
    def __init__(self, sock:ASocket, addr):
        self.sock = sock
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
    def name(self):
        return self.__class__.__name__
    
    def opposite_name(name):
        if name.endswith("Protocol"):
            raw_name = name.removesuffix("Protocol")
            end_name = f"{raw_name}Handler"
        if name.endswith("Handler"):
            raw_name = name.removesuffix("Handler")
            end_name = f"{raw_name}Protocol"
        
        return end_name
    
    
    #def send_file(self, path:str, buffer:int):
    #    file = open(path, "rb")
    #    
    #    try:
    #        # Send the contents of the file in chunks based on buffer
    #        with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mm:
    #            for i in range(0, mm.size(), buffer):
    #                self.send_msg(mm[i:i+buffer])
    #    except ModuleNotFoundError or ValueError:
    #        print("mmap failed because of emtpy file, or it isn't installed")
    #    except ConnectionResetError:
    #        pass
    #    finally:
    #        file.close()