from asocket import ASocket

class Base(ASocket):
    def __init__(self, sock, addr):
        super().__init__(sock)
        self.addr = addr
        #try:
        #    self.send_msg(sock, self.handler_name)
        #except ConnectionError:
        #    pass
        
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
            end_name = f"{raw_name}Protocl"
        
        return end_name