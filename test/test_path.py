import unittest
from lib.path import Path


class PathTestCase(unittest.TestCase):
    
    def test_endpoint_path(self):
        path = Path('/', endpoint=True)
        self.assertIsNotNone(path.match('/'))
        
        path = Path('/abc', endpoint=True)
        self.assertIsNotNone(path.match('/abc'))
        self.assertIsNone(path.match('/a'))
        self.assertIsNone(path.match('/abcd'))

        path = Path('/abc/def', endpoint=True)
        self.assertIsNotNone(path.match('/abc/def'))
        self.assertIsNone(path.match('/abc/d'))
    
    def test_index_middleware_path(self):
        path = Path('/', endpoint=False)
        self.assertIsNotNone(path.match('/'))
        self.assertIsNotNone(path.match('/abc'))
        self.assertIsNotNone(path.match('/abc/def'))

    def test_absolute(self):
        rootpath = Path('/root/')
        subpath = Path('/sub/')
        subpath.abs_to(rootpath)
        self.assertIsNotNone(subpath.match('/root/sub'))
        self.assertIsNotNone(subpath.match('/root/sub/abc'))
        self.assertIsNone(subpath.match('/root'))
        
    
    def test_argument_path(self):
        with self.subTest('single path argument'):
            path = Path('/hello/<name>')

            match = path.match('/hello/bob')
            self.assertIsNotNone(match)
            args = match.groupdict()
            self.assertTrue('name' in args)
            self.assertEqual('bob', args['name'])
            
            match = path.match('/hello/bob/anderson')
            self.assertIsNotNone(match)
            args = match.groupdict()
            self.assertTrue('name' in args)
            self.assertEqual('bob', args['name'])

            match = path.match('/bob')
            self.assertIsNone(match)
        
        with self.subTest('multiple path arguments'):
            path = Path('/<name>/<foo>/<bar>')

            match = path.match('/bob/foo/bar')
            self.assertIsNotNone(match)
            args = match.groupdict()
            self.assertTrue('name' in args)
            self.assertTrue('foo' in args)
            self.assertTrue('bar' in args)
            self.assertEqual(args['name'], 'bob')
            self.assertEqual(args['foo'], 'foo')
            self.assertEqual(args['bar'], 'bar')

            match = path.match('/bob')
            self.assertIsNone(match)


