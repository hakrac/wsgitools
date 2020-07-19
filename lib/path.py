import re
from re import escape as e

class Path:

    PATH_CHAR = '\+'
    PATH_STRING = '\*'
    PATH_SEGMENTS = '%'

    def __init__(self, rule, endpoint=False):
        self._rule = rule.strip()
        self.endpoint = endpoint
        self.path_args = {}

        self._rule = re.sub('[\^\$]', '', self._rule)

        if re.match('.*%$', self._rule) is None:
            if re.match('.*/$', self._rule) is None:
                self._rule += '/'

        self._rule = re.sub(self.PATH_CHAR, '\\\\w', self._rule)
        self._rule = re.sub(self.PATH_STRING, '\\\\w+', self._rule)
        self._rule = re.sub(self.PATH_SEGMENTS, '[^\\\\s]*', self._rule)
        self._rule = re.sub(r'<(?P<arg>\w+)>', '(?P<\g<arg>>\\\\w+)', self._rule)

        if re.match('.*\$$', self._rule) is None and endpoint:
            self._rule += '$'

        self.regexpath = re.compile(self._rule)
        
    def abs_to(self, path):
        if not path.endpoint:
            self._rule = path._rule + self._rule
            self._rule = re.sub('/+', '/', self._rule)
            self.regexpath = re.compile(self._rule)

    def match(self, reqpath):
        if not re.match('.*/$', reqpath):
            reqpath += '/'
        return self.regexpath.match(reqpath)

    def __repr__(self):
        return self._rule
