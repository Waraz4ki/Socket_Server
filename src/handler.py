import logging

class Handler:
    def __init__(self) -> None:
        """
        Select preprogrammed handler
        """
    
    def get_handler(self, purpose):
        """Request way to handle sent items
    
        Args:
            conn (socket): socket obj
            addr (_RetAddress): address of the connected machine
    
        Returns a string containing the way to handle the items sent
        """
        handle_methodes = {
            "chat": self.chathandle,
            "coordinates" : self.locationhandle,
        }
        handler = handle_methodes.get(purpose)
        
        return handler
    
    def handle(self, handler, data):
        """
        Run Handle Method
        """
        
        handler(data=data)
    
    def chathandle(self, data):
        print(data)
    
    def locationhandle(self, data):
        print("loc")
