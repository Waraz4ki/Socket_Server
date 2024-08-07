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