from pydantic import BaseModel, EmailStr, Field, ConfigDict


class  SUserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class SUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True) # Когда дают объект user читать через точку
    id: int
    email: EmailStr
    is_active: bool


class SUserLogin(BaseModel):
    email:EmailStr
    password: str


class SToken(BaseModel):
    access_token: str
    token_type: str = 'bearer'




