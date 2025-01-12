from fastapi import APIRouter
from ..models.user import User

router = APIRouter()

@router.get("/")
def get_all():
    return [{"message": "List of users"}]

@router.get("/user_id")
def get_user(user_id: int):
    return {"message": "Get a single user", "id": user_id}

@router.post("/")
def create_user(payload: User):
    return {"message": "Create user", "data": payload}
