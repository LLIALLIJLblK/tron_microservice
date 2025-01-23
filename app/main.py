
from fastapi import FastAPI
from .database import engine, Base
from .routes import address, requests

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(address.router)
app.include_router(requests.router)
