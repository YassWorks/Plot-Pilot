from fastapi import FastAPI
from pydantic import BaseModel

class FormData(BaseModel):
    prompt: str
    file: bytes

app = FastAPI(title="Plot Pilot API")

@app.get("/")
async def root():
    return {"message": "works fine"}

@app.get("/health")
async def health_check():
    return {"status": "healthy <3"}

@app.post("/api/plot")
async def create_plot(form_data: FormData):
    prompt = form_data.prompt
    file = form_data.file
    
    # sending the prompt to the LLM and getting the python code back
    
    