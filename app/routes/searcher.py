from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi import Request, Form

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get('/')
def index(request: Request):
    return templates.TemplateResponse(request, status_code=200, name='index.html')

@router.post('/post_data')
def post_data(text=Form()):
    return text
