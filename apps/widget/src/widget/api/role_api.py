from fastapi import APIRouter
from ..models.role import Role

router = APIRouter()

@router.get("/")
def get_all():
    return [{"message": "List of roles"}]

@router.get("/role_id")
def get_role(role_id: int):
    return {"message": "Get a single role", "id": role_id}

@router.post("/")
def create_role(payload: Role):
    return {"message": "Create role", "data": payload}
