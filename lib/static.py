import os
import mimetypes
import re
from lib.middleware import Middleware


class StaticMiddleware(Middleware):

    def __init__(self, dir):
        self.dir = dir
        mimetypes.init()

    @staticmethod
    def search_file(path):
        if os.path.exists(path) and os.path.isfile(path):
            return True
        return False

    @staticmethod
    def mimetype_by_ext(ext):
        if ext in mimetypes.types_map:
            return mimetypes.types_map[ext]

    @staticmethod
    def sanitize_filepath(path):
        path = re.sub('/$', '', path)
        path = re.sub('^/', '', path)

        match = re.match('(?P<filename>.+)(?P<ext>\.\w+)$', path)
        if match:
            filepath = match.groupdict()['filename']
            ext = match.groupdict()['ext']
            return filepath, ext

    def __call__(self, req, res, next):
        path = req.environ['SCRIPT_NAME']
        filepath, ext = StaticMiddleware.sanitize_filepath(path)
        exists = StaticMiddleware.search_file(os.path.join(os.getcwd(), filepath + ext))
        if exists:
            with open(filepath + ext, 'r') as fd:
                mimetype = StaticMiddleware.mimetype_by_ext(ext)
                if mimetype:
                    res.content_type = mimetype
                res.set_data(fd.read())
                return res
        return next(req, res)

    