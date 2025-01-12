from fastapi import APIRouter
from ..models.company import Company

router = APIRouter()

@router.get("/")
def get_all():
    return [{"message": "List of companys"}]

@router.get("/company_id")
def get_company(company_id: int):
    return {"message": "Get a single company", "id": company_id}

@router.post("/")
def create_company(payload: Company):
    return {"message": "Create company", "data": payload}
