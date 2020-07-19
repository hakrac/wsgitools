import unittest
from werkzeug.test import Client, EnvironBuilder
from lib.request import Request
from lib.response import Response
from lib.router import Router, Pipeline, Middleware, RouteTree
from lib.path import Path
from lib.utils import time_it
import time

class PipelineTestCase(unittest.TestCase):
    pass

class RouterTestCase(unittest.TestCase):
    
    def test_index(self):
        self.index_called = False

        def index(req, res):
            self.index_called = True
            res.set_data('Index')
            return res
        
        router = Router()
        router._create_endpoint(index, '/', ['GET'])

        c = Client(router.build(), Response)
        res = c.get('/')
        self.assertTrue(self.index_called)
        self.assertEqual(res.data, b'Index')

    def test_middleware(self):
        self.middleware_called = False
        self.endpoint_called = False
        self.endpoint_a_called = False

        def middleware(req, res, next):
            self.middleware_called = True
            return next(req, res)
        
        def endpoint_a(req, res):
            self.endpoint_a_called = True
            res.set_data('a')
            return res

        def endpoint(req, res):
            self.endpoint_called = True
            res.set_data('Index')
            return res

        router = Router()
        router._create_middleware(middleware, '/', ['GET'])
        router._create_endpoint(endpoint_a, '/a', ['GET'])
        router._create_endpoint(endpoint, '/', ['GET'])

        c = Client(router.build(), Response)
        res = c.get('/')
        self.assertTrue(self.middleware_called)
        self.assertTrue(self.endpoint_called)
        self.assertFalse(self.endpoint_a_called)
        self.assertEqual(res.data, b'Index')

        self.middleware_called = False
        self.endpoint_called = False
        self.endpoint_a_called = False

        c = Client(router._application, Response)
        res = c.get('/a')
        self.assertTrue(self.middleware_called)
        self.assertFalse(self.endpoint_called)
        self.assertTrue(self.endpoint_a_called)
        self.assertEqual(res.data, b'a')

    def test_wildcard(self):
        self.middleware_called = False
        self.endpoint_called = False
        self.endpoint_a_called = False

        def middleware(req, res, next):
            self.middleware_called = True
            return next(req, res)
        
        def endpoint_a(req, res):
            self.endpoint_a_called = True
            res.set_data('a')
            return res

        def endpoint(req, res):
            self.endpoint_called = True
            res.set_data('Index')
            return res

        router = Router()
        router._create_middleware(middleware, '%', ['GET'])
        router._create_endpoint(endpoint_a, '/a', ['GET'])
        router._create_endpoint(endpoint, '/', ['GET'])

        c = Client(router.build(), Response)
        res = c.get('/')
        self.assertTrue(self.middleware_called)
        self.assertTrue(self.endpoint_called)
        self.assertFalse(self.endpoint_a_called)
        self.assertEqual(res.data, b'Index')

        self.middleware_called = False
        self.endpoint_called = False
        self.endpoint_a_called = False

        c = Client(router._application, Response)
        res = c.get('/a')
        self.assertTrue(self.middleware_called)
        self.assertFalse(self.endpoint_called)
        self.assertTrue(self.endpoint_a_called)
        self.assertEqual(res.data, b'a')

    def test_subrouter(self):
        self.middleware_called = False
        self.endpoint_called = False
        self.middleware_a_called = False
        self.endpoint_a_called = False

        def middleware(req, res, next):
            self.middleware_called = True
            return next(req, res)
        
        def endpoint(req, res):
            self.endpoint_called = True
            res.set_data('Index')
            return res

        router = Router()
        router._create_middleware(middleware, '/', ['GET'])
        router._create_endpoint(endpoint, '/', ['GET'])

        def middleware_a(req, res, next):
            self.middleware_a_called = True
            return next(req, res)

        def endpoint_a(req, res):
            self.endpoint_a_called = True
            res.set_data('A')
            return res
        
        router_a = Router()
        router_a._create_middleware(middleware_a, '/b', ['GET'])
        router_a._create_endpoint(endpoint_a, '/b', ['GET'])
        router.mount('/a', router_a)
        

        with self.subTest('test / path'):
            c = Client(router.build(), Response)
            res = c.get('/')
            self.assertTrue(self.middleware_called)
            self.assertTrue(self.endpoint_called)
            self.assertFalse(self.endpoint_a_called)
            self.assertEqual(res.data, b'Index')

        self.middleware_called = False
        self.endpoint_called = False
        self.middleware_a_called = False
        self.endpoint_a_called = False

        with self.subTest('test /a path'):
            c = Client(router._application, Response)
            res = c.get('/a/b')
            self.assertTrue(self.middleware_called)
            self.assertFalse(self.endpoint_called)
            self.assertTrue(self.middleware_a_called)
            self.assertTrue(self.endpoint_a_called)
            self.assertEqual(res.data, b'A')
        
    def test_method(self):
        self.index_get_called = False
        self.index_post_called = False

        def index_get(req, res):
            self.index_get_called = True
            res.set_data('Index_get')
            return res
        
        def index_post(req, res):
            self.index_post_called = True
            res.set_data('Index_post')
            return res
        
        router = Router()
        router._create_endpoint(index_get, '/', ['GET'])
        router._create_endpoint(index_post, '/', ['POST'])
        
        c = Client(router.build(), Response)
        res = c.get('/')
        self.assertTrue(self.index_get_called)
        self.assertFalse(self.index_post_called)
        self.assertEqual(res.data, b'Index_get')

        self.index_get_called = False
        self.index_post_called = False

        res = c.post('/')
        self.assertFalse(self.index_get_called)
        self.assertTrue(self.index_post_called)
        self.assertEqual(res.data, b'Index_post')

    def test_decorators(self):
        self.middleware_called = False
        self.endpoint_called = False
        self.middleware_a_called = False
        self.endpoint_a_called = False

        router = Router()

        @router.pipe()
        def middleware(req, res, next):
            self.middleware_called = True
            return next(req, res)

        @router.pipe('/a')
        def middleware_a(req, res, next):
            self.middleware_a_called = True
            return next(req, res)

        @router.get('/a')
        def index_a(req, res):
            self.endpoint_a_called = True
            res.set_data('Index /a')
            return res
        
        @router.get()
        def index(req, res):
            self.endpoint_called = True
            res.set_data('Index /')
            return res
        

        c = Client(router.build(), Response)
        res = c.get('/')
        self.assertEqual(res.data, b'Index /')
        self.assertTrue(self.middleware_called)
        self.assertTrue(self.endpoint_called)
        self.assertFalse(self.endpoint_a_called)
        self.assertFalse(self.middleware_a_called)

        self.middleware_called = False
        self.endpoint_called = False
        self.middleware_a_called = False
        self.endpoint_a_called = False

        res = c.get('/a')
        self.assertEqual(res.data, b'Index /a')
        self.assertTrue(self.middleware_called)
        self.assertTrue(self.endpoint_a_called)
        self.assertTrue(self.middleware_a_called)
        self.assertFalse(self.endpoint_called)

    
class RouteTreeTestCase(unittest.TestCase):

    def test_nested_tree(self):

        def func(req, res):
            pass

        tree = RouteTree()
        path = Path('path/')
        tree[path] = func

        sub = RouteTree()
        routerpath = Path('sub/')
        tree[routerpath] = sub

        path = Path('path/')
        sub[path] = func

        tree.build_path(Path('/'))

        print(tree)
