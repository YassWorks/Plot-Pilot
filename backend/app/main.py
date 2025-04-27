from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import requests
from helpers.handle_code import handle_code
from helpers.sanitize import checkPrompt

app = FastAPI(title="Plot Pilot API")

# add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    # code (using Ollama deepseek-r1:8b model for now)
    try:
        is_allowed_prompt = checkPrompt(input_text)
        if not is_allowed_prompt:
            return {"error": "Prompt contains disallowed content. 🚩🚩"}

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "deepseek-r1:8b", "prompt": input_text, "stream": False},
        )
        response.raise_for_status()  # raise an error if the request fails
        generated_code = response.json()["response"]
        
        # specific to Ollama deepseek-r1:8b model only
        generated_code = generated_code[generated_code.find("#START") + 6: -3]
        
    except Exception as e:
        return {"error": f"Failed to generate code with Ollama: {str(e)}"}

    handle_code(generated_code)
    return {"message": "Order completed and ready!"}
