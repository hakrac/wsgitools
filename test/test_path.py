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

        rootpath = Path('/')
        subpath = Path('%')
        subpath.abs_to(rootpath)
        self.assertIsNotNone(subpath.match('/'))
        self.assertIsNotNone(subpath.match('/abc'))
        self.assertIsNotNone(subpath.match('/abc/def'))
            
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

    def test_wildcards_path(self):

        with self.subTest('test wildcard char'):
            path = Path('/h+llo')
            self.assertIsNotNone(path.match('/hello'))
            self.assertIsNotNone(path.match('/hallo'))
            self.assertIsNone(path.match('/haello'))
        
        with self.subTest('test wildcard string'):
            path = Path('/*/world')
            self.assertIsNotNone(path.match('/hello/world'))
            self.assertIsNotNone(path.match('/hell/world'))
            self.assertIsNone(path.match('/world'))
            self.assertIsNone(path.match('/hello/nice/world'))
            
            path = Path('/*o/world')
            self.assertIsNotNone(path.match('/hello/world'))
            self.assertIsNotNone(path.match('/foo/world'))
            self.assertIsNone(path.match('/hell/world'))

        with self.subTest('test wildcard segments'):
            path = Path('/%/world')
            self.assertIsNotNone(path.match('/hello/world'))
            self.assertIsNotNone(path.match('/hell/world'))
            self.assertIsNotNone(path.match('/hello/nice/world'))
            self.assertIsNone(path.match('/world'))

            path = Path('%')
            self.assertIsNotNone(path.match('/'))
            self.assertIsNotNone(path.match('/a1/b1'))
            self.assertIsNotNone(path.match('/a/b/c'))
            self.assertIsNotNone(path.match('/a/'))
            self.assertIsNotNone(path.match('/a1'))


