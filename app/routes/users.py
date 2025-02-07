from datetime import datetime, timedelta  # Ispravan import
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import BaseModel, EmailStr
from app.database import dynamodb
import bcrypt
import uuid

router = APIRouter()

# Povezivanje na DynamoDB tablicu
users_table = dynamodb.Table("Users")


class UserRegister(BaseModel):
    ime: str
    korisnicko_ime: str
    email: EmailStr
    lozinka: str


@router.post("/register")
def register_user(user: UserRegister):
    response = users_table.scan(
        FilterExpression="email = :email",
        ExpressionAttributeValues={":email": user.email}
    )

    if response.get("Items"):
        raise HTTPException(status_code=400, detail="Korisnik već postoji!")
    if "Item" in response:
        raise HTTPException(status_code=400, detail="Korisnik već postoji!")

    # enkripcija lozinke usera
    hashed_password = bcrypt.hashpw(user.lozinka.encode(), bcrypt.gensalt())

    # Spremanje korisnika u tablicu
    users_table.put_item(
        Item={
            "user_id": str(uuid.uuid4()),
            "ime": user.ime,
            "korisnicko_ime": user.korisnicko_ime,
            "email": user.email,
            "lozinka": hashed_password.decode()
        }
    )
    return {"message": "Registracija je uspješna!"}


SECRET_KEY = "tajni_kljuc"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserLogin(BaseModel):
    email: EmailStr
    lozinka: str


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login")
def login(user: UserLogin):
    print(f"Pokušaj prijave korisnika: {user.email}")

    # Tražimo korisnika pomoću `scan()` jer `email` nije primarni ključ
    response = users_table.scan(
        FilterExpression="email = :email",
        ExpressionAttributeValues={":email": user.email}
    )

    print(f"Dohvaceni podaci iz baze: {response}")

    # ako korisnik ne postoji jos u bazi
    if not response.get("Items"):
        print("Korisnik ne postoji!")
        raise HTTPException(
            status_code=401, detail="Neispravni podaci za prijavu!")

    user_data = response["Items"][0]
    print(f"Korisnicki podaci: {user_data}")

    # provjeravamo jel lozinka ispravna
    if not bcrypt.checkpw(user.lozinka.encode(), user_data["lozinka"].encode()):
        print("Neispravna lozinka!")
        raise HTTPException(status_code=401, detail="Neispravna lozinka!")

    # kreiranje tokena
    access_token = create_access_token(data={"sub": user.email})
    print(f"Generiran token: {access_token}")

    # tu sam dodala prosljedivanje user id-a da se moze pohranit nova izlozba povezana sa id-em korisnika
    return {"access_token": access_token, "token_type": "bearer", "user_id": user_data["user_id"]}
