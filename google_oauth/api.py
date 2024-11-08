from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from helper import handle_login
app = FastAPI()

class LoginRequest(BaseModel):
    url: str
    username: str
    password: str

class LoginResponse(BaseModel):
    login_code: str
    status: str

@app.post("/api/v1/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    await handle_login(login_request.url, login_request.username, login_request.password)
    return LoginResponse(login_code='test', status='SUCCESS')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)