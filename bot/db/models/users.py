from pydantic import BaseModel


class Users(BaseModel):
    user_id: int
    username: str
    status: int
    days: int
    trial_status: int
