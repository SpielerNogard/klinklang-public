import datetime
from typing import Optional, Any

from fastapi import FastAPI, Response
from pydantic import BaseModel

from klinklang.server import KlinkklangServer


class RateLimitResponse(BaseModel):
    message: str
    details: Optional[str] = None


class StatsRequest(BaseModel):
    license: str
    stat_type: str
    recorded: datetime.datetime
    value: Any


app = FastAPI()

server = KlinkklangServer()
server.start()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/code")
async def save_code_for_email(code: str, email: str):
    pass


@app.post("/connect")
async def connect_worker():
    """
    Endpoint used to connect a new worker to the Server.
    Every worker will get an own id based on the ip.
    """
    pass


@app.get("/service/config")
async def get_service_config(service: str):
    """
    Endpoint to get the configuration for a specific service.
    """
    config = server.get_config_for_service(service=service)
    if config:
        return {"config": config.value}
    return {"config": None}

@app.post("/service/heartbeat")
async def post_service_heartbeat(service: str):
    """
    Endpoint to post a heartbeat for a specific service.
    """
    # TODO
    return {"status": "OK"}