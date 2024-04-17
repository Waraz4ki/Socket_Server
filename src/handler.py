import logging

class Handler:
    def __init__(self, purpose) -> None:
        """
        Select preprogrammed handler
        """
        
        handletypes = {
            "chat": self.chathandle,
            "coordinates" : self.locationhandle,
        }
        self.handle = handletypes.get(purpose)
    
    def init(self, data):
        """ 
        Execute Handler
        """
        self.handle(data=data)
    
    def chathandle(self, data):
        print(data)
    
    def locationhandle(self, data):
        print("loc")
