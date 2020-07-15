import unittest
from werkzeug.test import Client, EnvironBuilder
from lib.request import Request
from lib.response import Response
from lib.router import Router, Pipeline, Middleware
from lib.path import Path
from lib.utils import time_it
import time

class PipelineTestCase(unittest.TestCase):

    def test_index(self):
        def index(req, res):
            res.set_data('Index')
            return res

        middlewares = [Middleware(index, '/one', ['GET'])]
        pipeline = Pipeline(middlewares, '/index')
        pipeline.build()

        self.assertEqual(middlewares[0].path._segments[0].pattern, 'index')
        self.assertEqual(middlewares[0].path._segments[1].pattern, 'one')


        req = Request(EnvironBuilder('/index/one', method='GET').get_environ())
        res = Response()

        def next(req, res):
            return res
        res = pipeline.handler(next, req, res)
        self.assertEqual(res.data, b'Index')
    
    def test_route(self):
        self.index_called = False
        self.route_endpoint_called = False

        def index(next, req, res):
            self.index_called = True
            return next(req, res)
        
        def route(req, res):
            self.route_endpoint_called = True
            res.set_data('Route')
            return res
        
        middlewares = [
            Middleware(index, '/', ['GET'], is_endpoint=False), 
            Middleware(route, '/route', ['GET'], is_endpoint=True)
        ]

        pipeline = Pipeline(middlewares, '/')
        req = Request(EnvironBuilder('/route', method='GET').get_environ())
        res = Response()

        def next(req, res):
            return res

        res = pipeline.handler(next, req, res)
        self.assertTrue(self.index_called)
        self.assertTrue(self.route_endpoint_called)
        self.assertEqual(res.data, b'Route')

    def test_routes(self):
        self.index_called = False
        self.index_endpoint_called = False
        self.route_endpoint_called = False

        def index(next, req, res):
            self.index_called = True
            return next(req, res)
        
        def index_endpoint(req, res):
            self.index_endpoint_called = True
            res.set_data('Index')
            return res
        
        def route(req, res):
            self.route_endpoint_called = True
            res.set_data('Route')
            return res
        
        middlewares = [
            Middleware(index, '/', ['GET'], is_endpoint=False),
            Middleware(route, '/route', ['GET'], is_endpoint=True),
            Middleware(index_endpoint, '/', ['GET'], is_endpoint=True)
        ]
        pipeline = Pipeline(middlewares, '/')

        req = Request(EnvironBuilder('/', method='GET').get_environ())
        res = Response()
        
        def next(req, res):
            return res
        res = pipeline.handler(next, req, res)

        self.assertTrue(self.index_called)
        self.assertTrue(self.index_endpoint_called)
        self.assertFalse(self.route_endpoint_called)
        self.assertEqual(res.data, b'Index')

        self.index_called = False
        self.index_endpoint_called = False
        self.route_endpoint_called = False

        req = Request(EnvironBuilder('/route', method='GET').get_environ())
        res = Response()

        def next(req, res):
            return res

        res = pipeline.handler(next, req, res)
        self.assertTrue(self.index_called)
        self.assertFalse(self.index_endpoint_called)
        self.assertTrue(self.route_endpoint_called)

class RouterTestCase(unittest.TestCase):
    
    def test_router(self):
        self.index_called = False
        self.index_endpoint_called = False
        self.sub_endpoint_called = False

        def index(next, req, res):
            self.index_called = True
            req.environ['index_called'] = True
            return next(req, res)
        
        def index_endpoint(req, res):
            self.index_endpoint_called = True
            res.set_data('Index')
            return res
        
        def sub(req, res):
            self.sub_endpoint_called = True
            res.set_data('Sub')
            return res
        
        subrouter = Router()
        subrouter.components = [
            Middleware(sub, '/', ['GET'], is_endpoint=True)
        ]

        router = Router()
        router.components = [
            Middleware(index, '/', ['GET'], is_endpoint=False),
            Middleware(index_endpoint, '/', ['GET'], is_endpoint=True),
        ]
        router.mount('/sub', subrouter)
        router.build()

        env = EnvironBuilder('/', method='GET').get_environ()
        req = Request(env)
        res = Response()

        def end(req, res):
            return res
        res = router.pipeline.handler(end, req, res)
        self.assertTrue(self.index_called)
        self.assertTrue(self.index_endpoint_called)
        self.assertFalse(self.sub_endpoint_called)
        self.assertEqual(res.data, b'Index')

        self.index_called = False
        self.index_endpoint_called = False
        self.sub_endpoint_called = False

        env = EnvironBuilder('/sub', method='GET').get_environ()
        req = Request(env)
        res = Response()

        def end(req, res):
            return res
        res = router.pipeline.handler(end, req, res)
        self.assertTrue(self.index_called)
        self.assertFalse(self.index_endpoint_called)
        self.assertTrue(self.sub_endpoint_called)
        self.assertEqual(res.data, b'Sub')

    def test_routers(self):
        self.index_called = False
        self.index_endpoint_called = False
        self.route_endpoint_called = False
        self.route2_endpoint_called = False


        def index(next, req, res):
            self.index_called = True
            return next(req, res)
        
        def index_endpoint(req, res):
            self.index_endpoint_called = True
            res.set_data('Index')
            return res
        
        def route(req, res):
            self.route_endpoint_called = True
            res.set_data('Route')
            return res
        
        router = Router()
        router.components = [
            Middleware(route, '/route', ['GET'])
        ]

        def route_2(req, res):
            self.route2_endpoint_called = True
            res.set_data('Route 2')
            return res
        
        router2 = Router()
        router2.components = [
            Middleware(route_2, '/route', ['GET']),
            Pipeline(router.components, '/router')
        ]

        middlewares = [
            Middleware(index, '/', ['GET'], is_endpoint=False),
            Pipeline(router2.components, '/router'),
            Middleware(index_endpoint, '/', ['GET'], is_endpoint=True)
        ]
        pipeline = Pipeline(middlewares, '/')
        pipeline.build()

        req = Request(EnvironBuilder('/', method='GET').get_environ())
        res = Response()
        def end(req, res):
            return res
        res = pipeline.handler(end, req, res)
        
        self.assertTrue(self.index_called)
        self.assertTrue(self.index_endpoint_called)
        self.assertFalse(self.route_endpoint_called)
        self.assertFalse(self.route2_endpoint_called)
        self.assertEqual(res.data, b'Index')
        
        self.index_called = False
        self.index_endpoint_called = False
        self.route_endpoint_called = False
        self.route2_endpoint_called = False
        req = Request(EnvironBuilder('/router/router/route', method='GET').get_environ())
        res = Response()
        def end(req, res):
            return res
        res = pipeline.handler(end, req, res)
        
        self.assertTrue(self.index_called)
        self.assertFalse(self.index_endpoint_called)
        self.assertTrue(self.route_endpoint_called)
        self.assertFalse(self.route2_endpoint_called)
        self.assertEqual(res.data, b'Route')

        self.index_called = False
        self.index_endpoint_called = False
        self.route_endpoint_called = False
        self.route2_endpoint_called = False
        req = Request(EnvironBuilder('/router/route', method='GET').get_environ())
        res = Response()
        def end(req, res):
            return res
        res = pipeline.handler(end, req, res)
        
        self.assertTrue(self.index_called)
        self.assertFalse(self.index_endpoint_called)
        self.assertFalse(self.route_endpoint_called)
        self.assertTrue(self.route2_endpoint_called)
        self.assertEqual(res.data, b'Route 2')

    def test_decorator(self):
        self.index_called = False
        self.index_endpoint_called = False
        self.sub_endpoint_called = False

        router = Router()

        @router.pipe()
        def index(next, req, res):
            self.index_called = True
            req.environ['index_called'] = True
            return next(req, res)
        
        @router.get()
        def index_endpoint(req, res):
            self.index_endpoint_called = True
            res.set_data('Index')
            return res

        router.build()
        self.assertTrue(router._is_build)

        c = Client(router, Response)
        res = c.get('/test')
        self.assertTrue(self.index_called)
        self.assertTrue(self.index_endpoint_called)
        self.assertEqual(res.data, b'Index')

class PathTestCase(unittest.TestCase):
    
    def test_segment_regex_conversion(self):
       path = Path('/root/sub', endpoint=True)
       self.assertEqual(path._segments[0].pattern, 'root')
       self.assertEqual(path._segments[1].pattern, 'sub')
       self.assertIsNotNone(path.match('/root/sub'))
    
    def test_args(self):
        path = Path('/root/<name>', endpoint=False)
        self.assertEqual(path._segments[0].pattern, 'root')
        self.assertEqual(path._segments[1].pattern, '(?P<name>\w+)')
        self.assertIsNotNone(path.match('/root/bob'))
        self.assertTrue('name' in path.match('/root/bob'))
        self.assertEqual(path.match('/root/bob')['name'], 'bob')
    
    def test_middleware(self):
        path = Path('/root/sub', endpoint=False)
        self.assertIsNotNone(path.match('/root/sub/sub'))

    def test_wildcards(self):

        with self.subTest('wildcard star'):
            path = Path('/*/sub', endpoint=True)
            self.assertEqual(path._segments[0].pattern, '.*')
            self.assertEqual(path._segments[1].pattern, 'sub')
            self.assertIsNotNone(path.match('/abc/sub'))

        with self.subTest('wildcard char'):
            path = Path('/+/sub', endpoint=True)
            self.assertEqual(path._segments[0].pattern, '.')
            self.assertEqual(path._segments[1].pattern, 'sub')
            self.assertIsNotNone(path.match('/a/sub'))
            self.assertIsNone(path.match('/ab/sub'))

        with self.subTest('wildcard all'):
            path = Path('/hello/%')
            self.assertEqual(path._segments[0].pattern, 'hello')
            self.assertEqual(path._segments[1].pattern, '%')
            self.assertIsNotNone(path.match('/hello/world/abc'))
            self.assertIsNone(path.match('/world/abc'))

    def test_time(self):
        pass
        # with open('./log.txt', 'w+') as fd:
        #     with time_it('test', fd=fd):
        #         time.sleep(1.0)
