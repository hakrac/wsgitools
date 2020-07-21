from werkzeug import redirect
from lib.response import Response
from lib.request import Request
from typing import Optional
from datetime import datetime
from hashlib import sha256, sha1
import functools

class UserMixin:
    id: int
    username: str
    password: str
    authenticated: bool

class User(UserMixin):
    pass

class SessionManager:
    
    user = None

    def __init__(self, secret, signin_route, cookie_identifier='SESSION', max_age=3600):
        self.salt = sha1(bytes(secret, 'utf-8')).hexdigest()
        self.cookie_id = cookie_identifier
        self.signin_route = signin_route
        self.max_age = max_age

    def __call__(self, req: Request, res: Response, next):
        now = datetime.now()
        # try getting session from cookie
        if self.cookie_id in req.cookies:
            # TODO check expiration date
            user_id = req.cookies[self.cookie_id]
            self.user = self._get_user(user_id)

        result = next(req, res)

        if self.user:
            res.set_cookie(self.cookie_id, str(self.user.id), self.max_age)
        else:
            res.set_cookie(self.cookie_id, '', max_age=now.timestamp())

        self.user = None
        return result

    def signin_user(self, user):
        user.authenticated = True
        self.user = user

    def signout_user(self, user):
        user.authenticated = False    
        self.user = None

    def get_user(self, f):
        self._get_user = f
        return f
    
    def restrict(self, f):
        @functools.wraps(f)
        def wrapper(req, res, next=None):
            if self.user is None:
                return redirect(self.signin_route)
            if next:
                return f(req, res, next)
            return f(req, res)
        return wrapper

