from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
# from .database import get_db
import base64, io, os
from PIL import Image
from pymongo import MongoClient
from pydantic import BaseModel
from .routers import auth, users, serviceProviders, services, categories, initializeDB
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

origins = [
    "http://localhost:5173",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(initializeDB.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(serviceProviders.router)
app.include_router(services.router)

# @app.post("/icon")
# def postIcon(icon: UploadFile = File(...), db: MongoClient = Depends(get_db)):
#     db["icons"].insert_one({"icon": base64.b64encode(icon.file.read())})

# @app.get("/icon")
# def getIcon(db: MongoClient = Depends(get_db)):
#     icon = db["icons"].find_one()
#     image = base64.b64decode(icon["icon"])
#     return {"icon": image}
