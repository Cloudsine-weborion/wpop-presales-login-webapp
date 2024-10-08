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
import asyncio
from datetime import datetime

from settings import settings
from auth import (
    authenticate_user,
    create_access_token,
    get_current_user_from_token,
    get_current_user_from_cookie,
)
from utils import convert_float_to_str, convert_str_to_float


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


class TransferForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.account_number: Optional[str] = None
        # self.routing_number: Optional[str] = None
        self.amount: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.account_number = form.get("accountNumber")
        # self.routing_number = form.get("routingNumber")
        self.amount = form.get("amount")

    async def is_valid(self):
        if not self.account_number:
            self.errors.append("Amount is required")
        # if not self.routing_number:
        #     self.errors.append("Routing number is required")
        if not self.errors:
            return True
        return False


app = FastAPI()


load_dotenv()
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))


original_balance = "33,500.88"

original_transaction = [
    {"description": "Restaurant XYZ", "date": "May 15, 2024", "amount": "-$45.60"},
    {"description": "Grocery Store", "date": "May 14, 2024", "amount": "-$82.35"},
    {
        "description": "Salary Deposit",
        "date": "May 1, 2024",
        "amount": "+$3,500.00",
    },
    {
        "description": "Macdonald",
        "date": "Apr 1, 2024",
        "amount": "-$11.80",
    },
    {
        "description": "Salary Deposit",
        "date": "Apr 1, 2024",
        "amount": "+$3,500.00",
    },
]

# Global state
account_balance = {"balance": original_balance}
recent_transactions = original_transaction.copy()

app.mount("/auth/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# Health check endpoint
@app.get("/healthz", status_code=200)
async def root():
    return {"healthy!"}


# --------------------------------------------------------------------------
# Home Page - GET
# --------------------------------------------------------------------------
@app.get("/auth/cpanel", response_class=HTMLResponse)
async def index(request: Request):
    try:
        user = get_current_user_from_cookie(request)
    except:
        user = None
    context = {
        "user": user,
        "request": request,
    }
    # print(f"{context}")
    return templates.TemplateResponse("index.html", context)


# --------------------------------------------------------------------------
# Modal Pop up - GET
# --------------------------------------------------------------------------
@app.get("/auth/modal", response_class=HTMLResponse)
async def auth_modal(request: Request):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("modal.html", context)


# --------------------------------------------------------------------------
# SQLI Page - GET
# --------------------------------------------------------------------------
@app.get("/auth/sqli", response_class=HTMLResponse)
async def auth_sqli(request: Request):
    try:
        user = get_current_user_from_cookie(request)
    except:
        user = None
    context = {
        "user": user,
        "request": request,
    }
    return templates.TemplateResponse("sqli.html", context)


# --------------------------------------------------------------------------
# CSRF Page - GET
# --------------------------------------------------------------------------
@app.get("/auth/csrf", response_class=HTMLResponse)
async def auth_csrf(request: Request):
    try:
        user = get_current_user_from_cookie(request)
    except:
        user = None
    context = {
        "user": user,
        "request": request,
    }
    return templates.TemplateResponse("csrf.html", context)


# --------------------------------------------------------------------------
# Webshell Page - GET
# --------------------------------------------------------------------------
@app.get("/auth/webshell", response_class=HTMLResponse)
async def auth_webshell(request: Request):
    try:
        user = get_current_user_from_cookie(request)
    except:
        user = None
    context = {
        "user": user,
        "request": request,
    }
    return templates.TemplateResponse("webshell.html", context)


# --------------------------------------------------------------------------
# XSS Page - GET
# --------------------------------------------------------------------------
@app.get("/auth/xss", response_class=HTMLResponse)
async def auth_xss(request: Request):
    try:
        user = get_current_user_from_cookie(request)
    except:
        user = None
    context = {
        "user": user,
        "request": request,
    }
    return templates.TemplateResponse("xss.html", context)


# --------------------------------------------------------------------------
# Bank Page - GET
# --------------------------------------------------------------------------
@app.get("/auth/bank", response_class=HTMLResponse)
async def auth_bank(request: Request):
    # account_balance["balance"] = "7800.88"
    # try:
    #     user = get_current_user_from_cookie(request)
    # except:
    #     user = None
    context = {
        # "user": user,
        "request": request,
        "transactions": recent_transactions,
        "balance": account_balance["balance"],
    }
    return templates.TemplateResponse("bank.html", context)


# --------------------------------------------------------------------------
# Bank Transfer Page - GET
# --------------------------------------------------------------------------
@app.get("/auth/bank/transfer", response_class=HTMLResponse)
async def auth_bank_transfer(request: Request):
    # try:
    #     user = get_current_user_from_cookie(request)
    # except:
    #     user = None
    context = {"request": request, "balance": account_balance["balance"]}
    return templates.TemplateResponse("bank-transfer.html", context)


# --------------------------------------------------------------------------
# Bank Transfer Page - POST
# --------------------------------------------------------------------------
@app.post("/auth/bank/transfer", response_class=HTMLResponse)
async def auth_bank_transfer_post(request: Request):
    form = TransferForm(request)
    await form.load_data()

    if await form.is_valid():
        try:
            # user = get_current_user_from_cookie(request)
            current_balance = convert_str_to_float(account_balance["balance"])

            transfer_amt = convert_str_to_float(form.__dict__.get("amount"))
            new_balance = current_balance - transfer_amt
            account_balance["balance"] = convert_float_to_str(new_balance)
            account_number = form.__dict__.get("account_number")

            today = datetime.today()
            formatted_date = today.strftime("%B %d, %Y")

            new_transaction = {
                "description": f"Fund transfer to Account Number {account_number}",
                "date": formatted_date,
                "amount": f"-${transfer_amt:,.2f}",
            }

            recent_transactions.insert(0, new_transaction)

            # Redirect response upon submission and include the transfer amount in the url
            # return RedirectResponse(
            #     f"/auth/bank?transfer_amount={transfer_amt:.2f}", status.HTTP_302_FOUND
            # )
            return RedirectResponse(f"/auth/bank", status.HTTP_302_FOUND)

        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Transfer Unsuccessful!")
            return templates.TemplateResponse("bank-transfer.html", form.__dict__)
    return templates.TemplateResponse("bank-transfer.html", form.__dict__)


# --------------------------------------------------------------------------
# Bank Page Reset - GET
# --------------------------------------------------------------------------
@app.get("/auth/bank/reset", response_class=HTMLResponse)
async def auth_bank_reset(request: Request):
    try:
        user = get_current_user_from_cookie(request)
    except:
        user = None

    global account_balance, recent_transactions

    original_balance = "33,500.88"

    if user:

        account_balance = {"balance": original_balance}

        recent_transactions = [
            {
                "description": "Restaurant XYZ",
                "date": "May 15, 2024",
                "amount": "-$45.60",
            },
            {
                "description": "Grocery Store",
                "date": "May 14, 2024",
                "amount": "-$82.35",
            },
            {
                "description": "Salary Deposit",
                "date": "May 1, 2024",
                "amount": "+$3,500.00",
            },
            {
                "description": "Macdonald",
                "date": "Apr 1, 2024",
                "amount": "-$11.80",
            },
            {
                "description": "Salary Deposit",
                "date": "Apr 1, 2024",
                "amount": "+$3,500.00",
            },
        ]
        return RedirectResponse("/auth/cpanel", status.HTTP_302_FOUND)
    else:
        return RedirectResponse("/auth/login", status.HTTP_302_FOUND)


@app.get("/nginx-auth")
async def nginx_auth(request: Request):
    try:
        user = get_current_user_from_cookie(request)
    except:
        user = None
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    else:
        return 200


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
            response = RedirectResponse("/auth/cpanel", status.HTTP_302_FOUND)
            await login_for_access_token(response=response, form_data=form)
            form.__dict__.update(msg="Login Successful!")
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or Password")
            return templates.TemplateResponse("login.html", form.__dict__)
    return templates.TemplateResponse("login.html", form.__dict__)


def dev_server():
    uvicorn.run("app:app", port=PORT, host=HOST, log_level="debug", reload=True)


def start_server():
    uvicorn.run("app:app", port=PORT, host=HOST, log_level="debug", workers=1)


if __name__ == "__main__":
    # create and access a new asyncio event loop
    loop = asyncio.new_event_loop()
    loop.run_until_complete(start_server())
