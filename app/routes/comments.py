from app.database import dynamodb
from fastapi import APIRouter, HTTPException
import boto3
import uuid
from pydantic import BaseModel
from fastapi import Query
import os
router = APIRouter()

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url="http://localhost:8000",  # Lokalni DynamoDB
    region_name="us-east-1",
    # Dummy AWS kljucevi, ja imam lokalnu bazu, zamjenit ces to svojim aws kljucevima na kraju projekta
    aws_access_key_id="fakeMyKeyId",
    aws_secret_access_key="fakeSecretAccessKey"
)
comments_table = dynamodb.Table("Comments")


class Comment(BaseModel):
    image_name: str
    text: str
    user_id: str


COMMENTS_TABLE = "Comments"


@router.get("/")
# dohvaca sve komentare koji su povezani s odredenom slikom
def get_comments(image_name: str = Query(..., alias="imageName")):
    try:
        response = comments_table.scan(  # trazi slike gdje je image name iz urla kad pozivamo jednako image name iz baze od neke slike, vratit ce vec podatke u json formatu
            FilterExpression="image_name = :image",
            ExpressionAttributeValues={":image": image_name}
        )
        comments = response.get("Items", [])
        return {"comments": comments}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Pogreška pri dohvaćanju komentara!")


@router.post("/")
def add_comment(comment: Comment):  # funkcija za dodavanje novog komentara
    try:
        comment_id = str(uuid.uuid4())  # Generiraj jedinstveni ID komentara
        image_name = str(comment.image_name) if comment.image_name else None
        # predstavlja sadrzaj komentara
        text = str(comment.text) if comment.text else None
        user_id = str(comment.user_id) if comment.user_id else None
        artwork_id = str(comment.image_name)

        # provjera da nijedno polje nije None
        if not all([comment_id, image_name, text, user_id, artwork_id]):
            raise HTTPException(
                status_code=400, detail="Sva polja su obavezna!")

        comments_table.put_item(  # zapisuje u bazu novi komentar
            Item={
                "comment_id": comment_id,
                "artwork_id": artwork_id,
                "image_name": image_name,
                "text": text,
                "user_id": user_id
            }
        )

        return {"message": "Komentar je uspješno dodan!", "comment_id": comment_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
