from typing import Dict, List, Optional
from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
import uvicorn
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

import httpx

from settings import settings
from model import User
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user_from_token,
    get_current_user_from_cookie,
)


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")

    async def is_valid(self):
        if not self.username:
            self.errors.append("Username is required")
        if not self.password or not len(self.password) >= 4:
            self.errors.append("A valid password is required")
        if not self.errors:
            return True
        return False


app = FastAPI()


load_dotenv()
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

# app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# Health check endpoint
@app.get("/healthz", status_code=200)
async def root():
    return {"healthy!"}


# --------------------------------------------------------------------------
# Home Page
# --------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    try:
        user = get_current_user_from_cookie(request)
    except:
        user = None
    context = {
        "user": user,
        "request": request,
    }
    print(f"{context}")
    return templates.TemplateResponse("index.html", context)


@app.post("token")
async def login_for_access_token(
    response: Response, form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, str]:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"username": user.username})

    # Set an HttpOnly cookie in the response. `httponly=True` prevents
    # JavaScript from reading the cookie.
    response.set_cookie(
        key=settings.COOKIE_NAME, value=f"Bearer {access_token}", httponly=True
    )
    return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}


# --------------------------------------------------------------------------
# Demo page
# --------------------------------------------------------------------------
@app.get("/demo", response_class=RedirectResponse, status_code=302)
async def demo(request: Request, user: User = Depends(get_current_user_from_token)):
    context = {"user": user, "request": request}
    return RedirectResponse("https://typer.tiangolo.com")


# @app.get("/juiceshop")
# async def tile_request(response: Response):
#     async with httpx.AsyncClient() as client:
#         proxy = await client.get(f"https://google.com")
#     response.body = proxy.content
#     response.status_code = proxy.status_code
#     return response


# @app.get("/juiceshop")
# async def proxy_to_google(request: Request):
#     url = "https://www.google.com"
#     async with httpx.AsyncClient(follow_redirects=True) as client:
#         response = await client.get(url, stream=True)

#     # Forward headers if needed
#     headers = {
#         key: value
#         for key, value in response.headers.items()
#         if key.lower() not in ["content-encoding", "transfer-encoding", "connection"]
#     }

#     return StreamingResponse(
#         response.aiter_raw(),  # Streaming response body
#         status_code=response.status_code,
#         headers=headers,
#         media_type=response.headers.get("content-type", "text/html"),
#     )


client = httpx.AsyncClient(base_url="http://172.125.11.161/")


async def _reverse_proxy(request: Request):
    url = httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))
    rp_req = client.build_request(
        request.method, url, headers=request.headers.raw, content=await request.body()
    )
    rp_resp = await client.send(rp_req, stream=True)
    return StreamingResponse(
        rp_resp.aiter_raw(),
        status_code=rp_resp.status_code,
        headers=rp_resp.headers,
        background=BackgroundTask(rp_resp.aclose),
    )


app.add_route("/demo/{path:path}", _reverse_proxy, ["GET", "POST"])


# --------------------------------------------------------------------------
# Login - GET
# --------------------------------------------------------------------------
@app.get("/auth/login", response_class=HTMLResponse)
async def login_get(request: Request):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("login.html", context)


# --------------------------------------------------------------------------
# Login - POST
# --------------------------------------------------------------------------
@app.post("/auth/login", response_class=HTMLResponse)
async def login_post(request: Request):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            response = RedirectResponse("/", status.HTTP_302_FOUND)
            await login_for_access_token(response=response, form_data=form)
            form.__dict__.update(msg="Login Successful!")
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or Password")
            return templates.TemplateResponse("login.html", form.__dict__)
    return templates.TemplateResponse("login.html", form.__dict__)


def start_server():
    uvicorn.run(
        "app:app",
        port=PORT,
        host=HOST,
        log_level="debug",
        reload=True,
    )


if __name__ == "__main__":
    start_server()
