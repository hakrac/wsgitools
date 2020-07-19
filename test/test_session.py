import unittest
from werkzeug import redirect
from werkzeug.test import Client, Headers, EnvironBuilder
from lib.router import Router
from lib.response import Response
from lib.session import SessionManager, User

class SessionManagerTestCase(unittest.TestCase):

    def test_init(self):
        router = Router()
        sessionManager = SessionManager('test', '/signin')
        router.pipe()(sessionManager)

    def test_cookie_read(self):
        router = Router()
        sessionManager = SessionManager('test', '/signin', cookie_identifier='SESSION_ID')
        router.pipe()(sessionManager)
        self.user = User()
        self.user.username = 'Bob'
        self.user.password = 'passwd'
        self.user.id = 0

        @sessionManager.get_user
        def get_user(user_id):
            return self.user

        @router.get()
        def index(req, res):
            self.assertEqual(sessionManager.user.id, 0)
            self.assertEqual(sessionManager.user.username, 'Bob')
            res.set_data('Index')
            return res
        
        self.c = Client(router.build(), Response)
        self.c.set_cookie('', 'SESSION_ID', '0')
        res = self.c.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, b'Index')

    def test_restrict(self):
        router = Router()
        sm = SessionManager('test', '/signin', cookie_identifier='SESSION_ID')
        self.user = User()
        self.user.username = 'Bob'
        self.user.password = 'passwd'
        self.user.id = 0

        @sm.get_user
        def get_user(user_id):
            return self.user

        router.pipe()(sm)

        @router.get('/signin')
        def signin(req, res):
            self.c.set_cookie('', 'SESSION_ID', '0')
            return redirect('/')

        @router.get()
        @sm.restrict
        def index(req, res):
            self.assertEqual(sm.user.id, 0)
            self.assertEqual(sm.user.username, 'Bob')
            res.set_data('Index')
            return res
        
        self.c = Client(router.build(), Response)
        res = self.c.get('/',  follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, b'Index')
