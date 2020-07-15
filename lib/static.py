# import response
# import request
# import io
# import hashlib


# class StaticHandler:

#     def __init__(self, file_stream = None):
#         if file_stream:
#             self.file_stream = file_stream

#     def handle(req: request.Request, res: response.Response):
#         etag = res.get_etag()

#         if etag[0]:
#             # etag given
#             # check etag
#             fd = open('/test', 'r') if not self.file_stream else: self.file_stream
#             data = io.StringIO()
#             line = fd.readline()
#             while line != '':
#                 data.write(line)
#             length = data.tell()
#             f_etag = hashlib.sha1('file' + str(length) + data.getvalue()).hexdigest()
#             print(etag)
#             print(f_etag)
#         else:
#             # no etag given send file
#             fd = open('/test', 'r') if not self.file_stream else: self.file_stream
#             data = io.StringIO()
#             line = fd.readline() 
#             while line != '':
#                 data.write(line)
#             res.set_data(data.getvalue())
#             f_etag = hashlib.sha1('file' + str(length) + data.getvalue()).hexdigest()
#             res.set_etag(f_etag)

            