from fastapi import FastAPI
from .routers import (
    auth,
    users,
    serviceProviders,
    services,
    categories,
    initializeDB,
    reviews,
    faqs,
    search,
    statistics,
)
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

app.include_router(initializeDB.router)
app.include_router(auth.router)
app.include_router(search.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(services.router)
app.include_router(serviceProviders.router)
app.include_router(reviews.router)
app.include_router(faqs.router)
app.include_router(statistics.router)
