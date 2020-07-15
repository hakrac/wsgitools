from werkzeug.wrappers import Response as WerkzeugResponse
import json

class Response(WerkzeugResponse):
    '''A werkzeug Response'''

    end = False
    
    def send_html(self, html):
        self.mimetype = 'text/html'
        self.set_data(html)
    
    def send_json(self, obj):
        self.mimetype = 'application/json'
        self.set_data(json.dumps(obj))