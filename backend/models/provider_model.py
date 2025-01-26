from pydantic import BaseModel


class Provider(BaseModel):
    name: str
    path: str
    username: str
    password: str
    link: str
