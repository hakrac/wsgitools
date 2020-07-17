from lib.session import SessionManager, User
from lib.response import Response
from werkzeug import redirect
from lib.request import Request
from lib.router import Router
from wsgiref import simple_server

router = Router()
sessionManager = SessionManager('test')

@sessionManager.get_user
def get_user(user_id):
    user = User()
    user.id = user_id
    user.username = 'Hakim'
    user.password = 'passwd'
    return user

@router.pipe()
def handle(next, req, res):
    try:
        return next(req, res)
    except FileNotFoundError:
        res.status_code = 404
        return res

router.pipe()(sessionManager)

@router.get('/signin')
def signin(req:Request, res: Response):
    if sessionManager.user is None:
        user = User()
        user.id = 1
        user.username = 'Hakim'
        user.password = 'passwd'

        sessionManager.signin_user(user)

    res.status_code = 302
    res.headers.add('Location', '/')
    return res

@router.get('/')
def index(req, res):
    if sessionManager.user is None:
        return redirect('/signin')
    
    print(f'{sessionManager.user.username} is logged in')
    res.set_data('Index')
    return res

with simple_server.make_server('', 3000, router.build()) as httpd:
    httpd.serve_forever()
