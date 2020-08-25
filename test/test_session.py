import unittest
from werkzeug import redirect
from werkzeug.test import Client, Headers, EnvironBuilder
from lib.router import Router
from lib.response import Response
from lib.session import BaseSessionManager, MemorySessionStore, JSONSessionStore
import uuid


class BaseSessionManagerTestCase(unittest.TestCase):

    def test_session(self):
        self.session_id = uuid.uuid4()
        def genId(req):
            return self.session_id.hex

        router = Router()
        sessionManager = BaseSessionManager(genId)

        router.pipe()(sessionManager)

        @router.get()
        def index(req, res):
            if 'alice' in sessionManager.session:
                res.set_data(sessionManager.session['alice'])
            else:
                sessionManager.session['alice'] = 'bob'
                res.set_data('Index')
            return res
        
        c = Client(router.build(), Response)
        res = c.get('/')
        self.assertEqual(res.data, b'Index')
        res = c.get('/')
        self.assertEqual(res.data, b'bob')

        c = Client(router.build(), Response)
        self.session_id = uuid.uuid4()
        res = c.get('/')
        self.assertEqual(res.data, b'Index')
        

class MemorySessionStoreTestCase(unittest.TestCase):

    def test_creation(self):
        store = MemorySessionStore()
        self.assertIsNotNone(store)
        self.assertIsNotNone(store._store)
    
    def test_save(self):
        store = MemorySessionStore()
        store.save('foo', 'bar')
        self.assertIsNotNone(store.get('foo'))
        self.assertEqual(store.get('foo'), 'bar')

    def test_delete(self):
        store = MemorySessionStore()
        store.save('foo', 'bar')
        self.assertIsNotNone(store.get('foo'))
        self.assertEqual(store.get('foo'), 'bar')

        store.delete('foo')
        self.assertIsNone(store.get('foo'))

class JSONSessionStoreTestCase(unittest.TestCase):

    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_creation(self):
        store = JSONSessionStore()
        self.assertIsNotNone(store)
    
    def test_save(self):
        store = JSONSessionStore()
        store.save('foo', 'bar')
        self.assertIsNotNone(store.get('foo'))
        self.assertEqual(store.get('foo'), 'bar')

    def test_delete(self):
        store = JSONSessionStore()
        store.save('foo', 'bar')
        self.assertIsNotNone(store.get('foo'))
        self.assertEqual(store.get('foo'), 'bar')

        store.delete('foo')
        self.assertIsNone(store.get('foo'))