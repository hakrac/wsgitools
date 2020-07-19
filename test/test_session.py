import unittest
from lib.router import Router
from lib.session import SessionManager

class SessionManagerTestCase(unittest.TestCase):

    def test_init(self):
        router = Router()
        sessionManager = SessionManager('test', '/signin')
        router.pipe()(sessionManager)
