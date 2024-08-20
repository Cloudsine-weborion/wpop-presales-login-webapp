from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/healthz", status_code=200)
async def root():
    return {"healthy!"}


@app.get("/login", response_class=HTMLResponse)
# async def login_page(request: Request, id: str):
async def login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")
