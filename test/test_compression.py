import unittest
from werkzeug.test import Client
from lib.response import Response
from lib.router import Router
from lib.compression import CompressionMiddleware

class CompressionMiddlewareTestCase(unittest.TestCase):

    def test_compression(self):

        router = Router()

        router.pipe()(CompressionMiddleware())
        
        @router.get()
        def index(req, res):
            res.set_data('Index')
            return res

        c = Client(router.build(), Response)

        res = c.get('/', headers={'Accept-Encoding': 'gzip'})
        self.assertEqual(res.headers.get('Content-Encoding'), 'gzip')