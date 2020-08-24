from werkzeug.utils import redirect, MultiDict
from lib.response import Response
from lib.request import Request
from typing import Optional
from datetime import datetime
from hashlib import sha256, sha1
import functools
import uuid
import os

class BaseStore:
    pass


class MemorySessionStore(BaseStore):
    
    def __init__(self):
        self._store = dict()

    def save(self, id, value):
        self._store[id] = value
    
    def delete(self, id):
        if id in self._store:
            self._store.popitem(id)
    
    def get(self, id):
        if id in self._store:
            return self._store[id]

class FileSessionStore(BaseStore):

    def __init__(self):
        if not FileSessionStore._session_dir_available():
            os.mkdir('session')

    @staticmethod
    def _session_dir_available():
        for entry in os.scandir('.'):
            if entry.is_dir and entry.name == 'session':
                return True
        return False

    def save(self, id, value):
        pass
    
    def delete(self, id):
        pass

    def get(self, id):
        pass

class BaseSessionManager:
    def __init__(
        self,
        generateId,
        cookie_maxage = 3600,
        store = None
    ):
        if store:
            self._store = store
        else:
            self._store = MemorySessionStore()
        self.generateId = generateId

        

    def __call__(self, req, res, next):
        if 'session_id' in req.cookies:
            session_id = str(req.cookies['session_id'])
        else:
            session_id = self.generateId(req)
        self.session = self._store.get(session_id)
        if not self.session:
            self.session = dict()
        result = next(req, res)
        self._store.save(session_id, self.session)
        res.set_cookie('session_id', bytes(session_id, 'utf-8'))
        return result



