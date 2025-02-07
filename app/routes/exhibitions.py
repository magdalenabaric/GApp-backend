from typing import List, Dict
from fastapi import APIRouter, HTTPException
from app.database import dynamodb
from pydantic import BaseModel
import uuid
import sys
sys.stdout.reconfigure(encoding='utf-8')

router = APIRouter()

# Povezivanje s tablicom Exhibitions
exhibitions_table = dynamodb.Table("Exhibitions")


class Image(BaseModel):
    url: str
    name: str


class User(BaseModel):
    displayName: str


class ExhibitionCreate(BaseModel):
    naziv: str
    opis: str
    user: User
    images: List[Image]

# Kreiranje nove izložbe


@router.post("/create", status_code=201)
def create_exhibition(exhibition: ExhibitionCreate):
    exhibition_id = str(uuid.uuid4())
    try:
        exhibitions_table.put_item(
            Item={
                "exhibition_id": exhibition_id,
                "naziv": exhibition.naziv,
                "opis": exhibition.opis,
                "user": exhibition.user.dict(),  # Pretvaramo User objekt u dictionary
                #  Svaki Image pretvaramo u dictionary
                "images": [image.dict() for image in exhibition.images]
            }
        )
        return {"message": "Nova izložba je kreirana!", "exhibition_id": exhibition_id}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Došlo je do pogreške pri kreiranju izložbe: {str(e)}")

# Dohvat svih izložbi


@router.get("/")
def get_exhibitions():
    try:
        response = exhibitions_table.scan()
        exhibitions = response.get("Items", [])

        # Formatiramo podatke za frontend
        formatted_exhibitions = [
            {
                "exhibition_id": exhibit.get("exhibition_id"),
                # Preimenuj opis u description
                "description": exhibit.get("opis", ""),
                # Dodaj user podatke ako postoje
                "user": exhibit.get("user", {}),
                "images": exhibit.get("images", [])  # Dodaj slike ako postoje
            }
            for exhibit in exhibitions
        ]

        return {"exhibitions": formatted_exhibitions}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Greška pri dohvaćanju izložbi: {str(e)}")

# Dohvat jedne izložbe prema ID-u


@router.get("/{exhibition_id}")
def get_exhibition(exhibition_id: str):
    try:
        response = exhibitions_table.get_item(
            Key={"exhibition_id": exhibition_id})
        if "Item" not in response:
            raise HTTPException(
                status_code=404, detail="Izložba nije pronađena")
        return response["Item"]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Pogreška pri dohvaćanju izložbe: {str(e)}")
