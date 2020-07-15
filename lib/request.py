from werkzeug.wrappers import Request as WerkzeugRequest


class Request(WerkzeugRequest):

    path_args = {}
    
    def __setattr__(self, name, value):
        if name != 'environ' and name in self.environ:
            self.environ[name] = value 
        return super().__setattr__(name, value)


    def __getattribute__(self, name):
        if name != 'environ' and name in self.environ:
            return self.environ[name]
        return super().__getattribute__(name)
