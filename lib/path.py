import re

class Path:

    def __init__(self, rule, endpoint=False):
        self.rule = rule.strip()
        self.endpoint = endpoint
        self.path_args = {}

        self.rule = re.sub('[\^\$]', '', self.rule)
        self.rule = re.sub(r'<(?P<arg>\w+)>', '(?P<\g<arg>>\\\\w+)', self.rule)

        if re.match('.*/$', self.rule) is None:
            self.rule += '/'

        if re.match('.*\$$', self.rule) is None and endpoint:
            self.rule += '$'

    def abs_to(self, path):
        if not path.endpoint:
            self.rule = path.rule + self.rule
            self.rule = re.sub('/+', '/', self.rule)

    def match(self, reqpath):
        if not re.match('.*/$', reqpath):
            reqpath += '/'
        return re.match(self.rule, reqpath)

    def __repr__(self):
        return self.rule
