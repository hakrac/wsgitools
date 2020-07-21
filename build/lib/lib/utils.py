from contextlib import contextmanager
from time import time
import math
from datetime import datetime
import sys

@contextmanager
def time_it(id, fd=sys.stdout):
    start = time()
    yield None
    end = time()
    date = datetime.fromtimestamp(math.floor(end)).isoformat()
    print(f'[{date}]:{id}:{(end-start):06.2f} seconds', file=fd)
