from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message" : "Hello World"}

@app.post("/items/")
async def create_item(name: str):
    return {"name": name}