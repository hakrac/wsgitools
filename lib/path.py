import re

class Path:
    '''
    Path composed out of multiple segments, which can be used for routing.
    '''

    PATH_STAR = '\*'
    PATH_CHAR = '\+'
    PATH_ALL = '%'

    def __init__(self, path, endpoint=False, ignorecase=True):
        self.ignorecase = ignorecase
        self._segments = list(filter(lambda s: len(s) > 0, path.split('/')))
        for i in range(len(self._segments)):
            self._segments[i] = self._segment_to_regex(self._segments[i]) 
        self.endpoint = endpoint

    def concat(self, segments):
        if isinstance(segments, Path):
            segments = segments._segments
        if len(segments) > 0:
            self._segments = segments + self._segments

    def _segment_to_regex(self, segment):
        '''Turns path segment into a regular expression'''
        segment = segment.strip()
        segment = re.sub('[\^\$]', '', segment)
        segment = re.sub(self.PATH_STAR, '.*', segment)
        segment = re.sub(self.PATH_CHAR, '.', segment)
        # embed named regex group for path arguments
        # /hello/<name>/ -> ^/hello/(?P<name>\w+)
        segment = re.sub(r'<(?P<arg>\w+)>', '(?P<\g<arg>>\\\\w+)', segment)
        flags = 0
        if self.ignorecase:
            flags &= re.IGNORECASE
        return re.compile(segment, flags)

    def match(self, path):
        '''Tests this path against a path'''
        path = tuple(filter(lambda s: len(s) > 0, path.split('/')))
        
        if re.compile(self.PATH_ALL) not in self._segments:
            if self.endpoint:
                if len(path) != len(self._segments):
                    return None
            if len(path) < len(self._segments):
                return None

        path_args = {}
        for i in range(len(self._segments)):
            # PATH_ALL matches multiple segments
            if self._segments[i] == re.compile(self.PATH_ALL):
                break
            match = self._segments[i].fullmatch(path[i])
            if match is None:
                return None
            path_args.update(match.groupdict())
        return path_args

    def __repr__(self):
        if self.endpoint:
            return '/' + self._segments.join('/')
        return '/' + self._segments.join('/') + '/'