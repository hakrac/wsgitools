from werkzeug import Request, Response
from wsgiref import simple_server
import re
import functools
import copy

if __name__ == '__main__':
    from lib.path import Path
    from lib.response import Response
    from lib.request import Request
else:
    from .path import Path
    from .response import Response
    from .request import Request

class Middleware:
    def __init__(self, handler, path, methods, is_endpoint=True):
        self.handler = handler
        self.path = Path(path, endpoint=is_endpoint)
        self.is_endpoint = is_endpoint
        self.methods = methods
    
    def __call__(self, next, req, res):
        if self.is_endpoint:
            return self.handler(req, res)
        return self.handler(next, req, res)

class Pipeline(Middleware):

    def __init__(self, stack, path):
        self.stack = stack
        self._i = 0
        self.end = False
        super().__init__(self.handler, path, ['GET', 'POST', 'DELETE', 'PUT'], is_endpoint=False)
    
    def build(self):
        for middleware in self.stack:
            # make middleware path absolute
            middleware.path.concat(self.path)
            if isinstance(middleware, Pipeline):
                middleware.build()

    def run_next(self, req, res):
        try:
            next = self.stack[self._i]
        except IndexError:
            return self.file_not_found(req, res)
        self._i += 1

        if self.method in next.methods:
            match = next.path.match(req.PATH_INFO)
            if match is not None:
                if match:
                    req.path_args.update(match)
                if next.is_endpoint:
                    return next.handler(req, res)
                return next.handler(self.run_next, req, res)

        return self.run_next(req, res)

    def file_not_found(self, req, res):
        # file was not found in pipeline
        if self.next:
            return self.next(req, res)

    def handler(self, next, req, res):
        self._i = 0
        self.next = next
        self.method = req.REQUEST_METHOD
        return self.run_next(req, res)

class Router:
    '''Builder of routing pipelines'''
    def __init__(self, root='/'):
        self.components = []
        self.root = root
        self._is_build = False

    def build(self):
        self.pipeline = Pipeline(self.components, self.root)
        self.pipeline.build()
        self._is_build = True

    def application(self, environ, start_response):
        '''handle request for this router'''
        if not self._is_build:
            self.build()
        req = Request(environ)
        res = Response()
        def end(req, res):
            raise FileNotFoundError
        return self.pipeline.handler(end, req, res)(environ, start_response)

    def __call__(self, environ, start_response):
        return self.application(environ, start_response)

    def mount(self, rule, router):
        handler = Pipeline(router.components, rule)
        self.components.append(handler)
        self._is_build = False

    def _create_endpoint(self, handler, rule, methods):
        endpoint = Middleware(handler, rule, methods, True)
        self.components.append(endpoint)
        self._is_build = False

    def _create_middleware(self, handler, rule, methods):
        middleware = Middleware(handler, rule, methods, False)
        self.components.append(middleware)
        self._is_build = False
    
    def pipe(self, rule='%', methods=['GET']):
        def create_wrapper(f):
            self._create_middleware(f, rule, methods)
        return create_wrapper

    def get(self, rule='%'):
        def create_wrapper(f):
            self._create_endpoint(f, rule, ['GET'])
        return create_wrapper
    
    def post(self, rule='%'):
        def create_wrapper(f):
            self._create_endpoint(f, rule, ['POST'])
        return create_wrapper

    def delete(self, rule='%'):
        def create_wrapper(f):
            self._create_endpoint(f, rule, ['DELETE'])
        return create_wrapper
    
    def put(self, rule='%'):
        def create_wrapper(f):
            self._create_endpoint(f, rule, ['PUT'])
        return create_wrapper
