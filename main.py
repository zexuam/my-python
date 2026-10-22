import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

load_dotenv()

app = FastAPI()

origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncIOMotorClient(os.getenv("MONGO_URL"))
db = client[os.getenv("DB_NAME", "shop")]


class Product(BaseModel):
    name: str
    price: float


@app.get("/")
async def home():
    return {"message": "Api is running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/products")
async def list_products():
    docs = await db.products.find().to_list(100)
    return [{"id": str(d["_id"]), "name": d["name"], "price": d["price"]} for d in docs]


@app.post("/api/products", status_code=201)
async def create_product(product: Product):
    result = await db.products.insert_one(product.model_dump())
    return {"id": str(result.inserted_id), **product.model_dump()}
