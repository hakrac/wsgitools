
class Middleware:
    def __init__(self, handler, methods):
        self.handler = handler
        self.methods = methods