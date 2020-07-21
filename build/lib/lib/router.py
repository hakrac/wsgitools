import re
import functools
import copy
if __name__ == '__main__':
    from lib.middleware import Middleware
    from lib.path import Path
    from lib.response import Response
    from lib.request import Request
else:
    from .middleware import Middleware
    from .path import Path
    from .response import Response
    from .request import Request

class Pipeline:
    '''Represents the execution pipeline of handlers'''
    def __init__(self, stack):
        self.stack = stack
        self._i = 0
    
    def run_next(self, req, res):
        try:
            path, next = self.stack[self._i]
        except IndexError:
            return self.file_not_found(req, res)
        self._i += 1

        req.path_args = path.path_args

        if path.endpoint:
            return next.handler(req, res)
        return next.handler(req, res, self.run_next)

    def file_not_found(self, req, res):
        # file was not found in pipeline
        raise FileNotFoundError

    def handler(self, req, res):
        self._i = 0
        return self.run_next(req, res)

class RouteTree(dict):
    '''Holds all routes with their handlers and builds a pipeline for a given request'''
    def build_pipeline(self, req):
        stack = []
        end_found = self.build_stack(req, stack)
        if end_found:
            # endpoint was not found
            pass
        return Pipeline(stack)

    def build_path(self, root):
        for path, node in self.items():
            path.abs_to(root)
            if isinstance(node, RouteTree):
                node.build_path(path)

    def build_stack(self, req, stack):
        for path, node in self.items():
            match = path.match(req.PATH_INFO)
            if match is not None:
                if isinstance(node, RouteTree):
                    end = node.build_stack(req, stack)
                    if end:
                        return end
                else:
                    if req.REQUEST_METHOD in node.methods:
                        if match:
                            path.path_args = match
                        stack.append((path, node))
                        if path.endpoint:
                            return True

class Router:
    '''Builder of RouteTree'''
    def __init__(self, root='/'):
        self.tree = RouteTree()
        self.components = []
        self.root = Path(root)

    def build(self):
        self.tree.build_path(self.root)
        return self._application

    def _application(self, environ, start_response):
        '''handle request for this router'''
        req = Request(environ)
        res = Response()
        pipeline = self.tree.build_pipeline(req)
        return pipeline.handler(req, res)(environ, start_response)
        
    def mount(self, rule, router):
        path = Path(rule, endpoint=False)
        if path in self.tree:
            raise IndexError(f'{path} cannot be used twice')
        self.tree[path] = router.tree

    def _create_endpoint(self, handler, rule, methods):
        path = Path(rule, endpoint=True)
        self.tree[path] = Middleware(handler, methods)

    def _create_middleware(self, handler, rule, methods):
        path = Path(rule)
        self.tree[path] = Middleware(handler, methods)

    def pipe(self, rule='%', methods=['GET']):
        def create_wrapper(f):
            self._create_middleware(f, rule, methods)
            return f
        return create_wrapper
    
    def get(self, rule='%'):
        def create_wrapper(f):
            self._create_endpoint(f, rule, ['GET'])
            return f
        return create_wrapper
    
    def post(self, rule='%'):
        def create_wrapper(f):
            self._create_endpoint(f, rule, ['POST'])
            return f
        return create_wrapper

    def delete(self, rule='%'):
        def create_wrapper(f):
            self._create_endpoint(f, rule, ['DELETE'])
            return f
        return create_wrapper
    
    def put(self, rule='%'):
        def create_wrapper(f):
            self._create_endpoint(f, rule, ['PUT'])
            return f
        return create_wrapper
