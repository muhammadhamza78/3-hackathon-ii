# from pydantic import BaseModel
# from typing import Optional

# # Response schema for reading user data
# class UserRead(BaseModel):
#     id: int
#     name: str
#     email: str
#     is_active: bool

#     class Config:
#         orm_mode = True




from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    profile_picture: Optional[str] = None

    class Config:
        from_attributes = True
