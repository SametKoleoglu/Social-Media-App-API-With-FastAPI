from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from datetime import datetime

from ..database import Base

class Activity(Base):
     __tablename__ = "activities"

     id = Column(Integer, primary_key=True, index=True)
     username = Column(String,nullable=False)
     timestamp = Column(DateTime, nullable=False,default=datetime.utcnow())
     
     liked_post_id = Column(Integer)
     username_like = Column(String)
     liked_post_image = Column(String)
     
     followed_username = Column(String)
     followed_user_pic = Column(String)