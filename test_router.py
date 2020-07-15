from lib.router import Router
from lib.utils import time_it
from lib.response import Response
from werkzeug import Client
from flask import Flask
import copy
import hashlib
import os
import sys
import psutil

process = psutil.Process(os.getpid())

with open('./log.txt', 'w+') as fd:
    
    mem = process.memory_info().rss

    app = Flask(__name__)
    with time_it('create 30000 routes with flask', fd=fd):
        for i in range(30000):
            def route():
                return str(i)
            route.__name__ = copy.copy(str(i))

            app.route('/' + str(i))(route)

    c = Client(app.wsgi_app, Response)
    with time_it('call route from flask', fd=fd):
        res = c.get('/25000')
        print(res.data)
        # assert res.data == b'900 route'
    
    new_mem = process.memory_info().rss 
    print(new_mem - mem)
    mem = new_mem
    




    router = Router()
    with time_it('create 30000 routes wsgitools router', fd=fd):
        for i in range(30000):
            route_desc = copy.copy(str(i) + ' route')
            @router.get(rule=str(i))
            def route(req, res):
                res.set_data(route_desc)
                return res 
    
    router.build()

    sys.setrecursionlimit(31000)
    c = Client(router.application, Response)
    with time_it('call route from wsgitools.router', fd=fd):
        res = c.get('/22000')
        print(res.data)
        # assert res.data == b'900 route'
    
    new_mem = process.memory_info().rss 
    print(new_mem - mem)
    mem = new_mem

    