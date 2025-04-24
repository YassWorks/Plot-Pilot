from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="Plot Pilot API")

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FormData(BaseModel):
    prompt: str


@app.get("/")
async def root():
    return {"message": "works fine"}


@app.get("/health")
async def health_check():
    return {"status": "healthy <3"}


@app.post("/plot")
async def create_plot(prompt: str = Form(...), file: UploadFile = File(None)):

    try:
        file_content = None
        if file:
            file_content = await file.read()  # read file as bytes
            file_content = file_content.decode("utf-8")
    except Exception as e:
        return {"error": f"File processing failed: {str(e)}"}

    # rules
    try:
        with open("rules.txt", "r") as rules_file:
            rules = rules_file.read()
    except FileNotFoundError:
        return {"error": "rules.txt file not found."}

    try:
        input_text = f"{rules}\n\n"
        if file_content:
            lines = file_content.splitlines()
            input_text += f"\n\nExtracted column names: {lines[0]}"
            input_text += "\n\nSample data:"
            for i in range(2, 6):
                if i < len(lines):
                    input_text += f"\n{lines[i]}"
        input_text += f"\n\nNow is job is: {prompt}\nMake sure to follow all the rules."
    except Exception as e:
        return {"error": f"Error processing input: {str(e)}"}

    # code
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "deepseek-coder:1.3b", "prompt": input_text, "stream": False},
        )
        response.raise_for_status()  # Raise an error if the request fails
        generated_code = response.json()["response"]
    except Exception as e:
        return {"error": f"Failed to generate code with Ollama: {str(e)}"}

    return {"placeholder": generated_code}
