from pydantic import BaseModel

class EmailCodeItem(BaseModel):
    code : str
    email : str