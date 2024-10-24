from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class HashtagModel(BaseModel):
     id: int
     name: str
     
     
class PostCreateModel(BaseModel):
    content: Optional[str] = None
    image : str
    location:Optional[str] = None
    

class PostUpdateModel(BaseModel):
    content: Optional[str] = None
    location: Optional[str] = None
    

class PostModel(PostCreateModel):
    id: int
    author_id: int
    likes_count: int
    created_at: datetime
    
    
    class Config:
         from_attributes = True