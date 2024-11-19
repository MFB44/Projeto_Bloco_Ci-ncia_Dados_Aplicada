from fastapi import APIRouter, HTTPException
from transformers import pipeline
from pydantic import BaseModel

router = APIRouter()

class AutoCompleteModel(BaseModel):
    phrase: str

@router.get("/")
async def read_root():
    return {"message": "Hello World"}

def generate_response(message: str):
    generator = pipeline("text-generation", model="gpt2-large")
    return generator(message)

@router.post("/autocomplete")
async def autocomplete(body: AutoCompleteModel):
    if not body.phrase:
        raise HTTPException(status_code=400, detail="Invalid prompt.")
    response = generate_response(body.phrase)
    return {"assistant": response}