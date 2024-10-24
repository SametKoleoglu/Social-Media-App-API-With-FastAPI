from fastapi import FastAPI


from .database import Base,engine
from .api import base_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
     title="Social Media App API",
     description="Engine Behind Social Media App",
     version="0.1.0",
     docs_url="/",
)

app.include_router(base_router)