from fastapi import FastAPI
from app.routes import exhibitions, users, comments
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Art Gallery Backend")

# ruta za usere
app.include_router(users.router, prefix="/users")
app.include_router(exhibitions.router, prefix="/exhibits")
app.include_router(comments.router, prefix="/comments")


@app.get("/")
def home():
    return {"message": "Dobrodošli u Art Gallery!"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Dozvoli sve metode (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Dozvoli sve zaglavlja
)
