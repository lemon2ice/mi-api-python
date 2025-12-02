from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Esquemas para Usuarios
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# Esquemas para Libros
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, max_length=20)
    publication_year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    price: Optional[float] = Field(0.0, ge=0)
    stock: Optional[int] = Field(0, ge=0)
    cover_image_url: Optional[str] = None
    author_ids: Optional[List[int]] = []

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    isbn: Optional[str] = Field(None, max_length=20)
    publication_year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)
    price: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    cover_image_url: Optional[str] = None
    author_ids: Optional[List[int]] = []

class BookResponse(BookBase):
    id: int
    authors: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Esquemas para Autores
class AuthorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    nationality: Optional[str] = Field(None, max_length=100)
    birth_year: Optional[int] = Field(None, ge=1000, le=datetime.now().year)

class AuthorResponse(AuthorBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Esquema para asociar autores a libros
class BookAuthorAssociation(BaseModel):
    book_id: int
    author_id: int