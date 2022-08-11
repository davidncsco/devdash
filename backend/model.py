
from typing import Optional
from pydantic import BaseModel
    
class DemoQuestion(BaseModel):
    _id: str
    choices: list
    answer: list
    filename: str

class User(BaseModel):
    email: str
    first: str
    last: str
    start: Optional[int]
    timetaken: Optional[float] = 0

class Car(BaseModel):
    _id: str
    number: int
    ip: str
    color: str
    speed: int = 500
    backup_speed: int = 500
    position: int = 0
    start: Optional[float]
    userid: Optional[str]