import gzip

class CompressionMiddleware:

    def __init__(self, compression_alogrithm = 'gzip'):
        pass

    def __call__(self, req, res, next):
        res = next(req, res)
        if 'gzip' in req.accept_encodings:
            # compress outgoing data
            data = res.data
            data = gzip.compress(data)
            res.set_data(data)

            res.headers.add('Content-Encoding', 'gzip')
        return res
