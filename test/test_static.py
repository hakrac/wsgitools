import unittest
import os
from werkzeug.test import Client
from lib.router import Router
from lib.response import Response
from lib.static import StaticMiddleware


class StaticMiddlewareTestCase(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(os.getcwd(), 'text.txt'), 'w') as fd:
            fd.write('Test data')
    
    def tearDown(self):
        os.remove(os.path.join(os.getcwd(), 'text.txt'))

    def test_search_file(self):
        exists = StaticMiddleware.search_file(os.path.join(os.getcwd(), 'text.txt'))
        self.assertTrue(exists)
        exists = StaticMiddleware.search_file(os.path.join(os.getcwd(), 'text'))
        self.assertFalse(exists)

    def test_path_sanitisation(self):
        path = '/root/sub.txt/'
        filename, ext = StaticMiddleware.sanitize_filepath(path)
        self.assertEqual(filename, 'root/sub')
        self.assertEqual(ext, '.txt')

        path = '/root/sub/'
        result = StaticMiddleware.sanitize_filepath(path)
        self.assertIsNone(result)

    def test_static_file(self):
        router = Router()
        router.pipe('/data')(StaticMiddleware(dir=os.getcwd()))

        @router.get()
        def index(req, res):
            res.set_data('Index')
            return res
        
        c = Client(router.build(), Response)
        res = c.get('/data/text.txt')
        self.assertEqual(res.data, b'Test data')
