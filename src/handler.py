import logging

class BaseHandler:
    def __init__(self) -> None:
        """Your Client will need to send forms with the respective function name for now and include no "self" parameter
        """
        pass
        
    def handle(self, handler, data):
        """
        Run Handle Method
        """        
        return handler(data=data)
    
if __name__ == "__main__":
    d = BaseHandler()