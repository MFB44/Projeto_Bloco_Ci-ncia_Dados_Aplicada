from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def read_root():
    return {"message": "Hello World"}

@router.post("/items/")
async def create_item(name: str):
    return {"name": name}