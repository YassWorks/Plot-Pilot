from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import requests
from helpers.handle_code import handle_code
from helpers.sanitize import checkPrompt, checkCode
import io
from pathlib import Path
import textwrap

app = FastAPI(title="Plot Pilot API")

# add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # REMINDER: restrict this in deployment
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
    # get file contents
    file_content_str: str | None = None
    try:
        if file:
            file_content_bytes = await file.read()  # read file as bytes
            # Attempt to decode, handle potential errors
            try:
                file_content_str = file_content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    # Fallback to latin-1 if utf-8 fails
                    file_content_str = file_content_bytes.decode("latin-1")
                except Exception as decode_err:
                    print(f"Error decoding file: {decode_err}")
                    return {"error": "Failed to decode uploaded file content."}
            finally:
                await file.close()  # Ensure file is closed

    except Exception as e:
        print(f"Error reading file: {e}")
        return {"error": f"File reading failed: {str(e)}"}

    # rules
    try:
        rules_path = Path(__file__).parent / "rules.txt"
        with open(rules_path, "r") as rules_file:
            rules = rules_file.read()
    except FileNotFoundError:
        print("Error: rules.txt not found.")
        return {"error": "Internal server error: Configuration file missing."}
    except Exception as e:
        print(f"Error reading rules.txt: {e}")
        return {"error": "Internal server error: Failed to read configuration."}

    # build the payload for the LLM
    input_text = f"{rules}\n\n"
    if not file_content_str:
        print(f"Error processing file content for prompt: {e}")
        return {"error": "Failed to process file content for prompt. It could be empty."}
    
    try:
        lines = file_content_str.splitlines()
        if lines:
            input_text += f"Extracted column names from the data provided by the user: \n{lines[0]}\n"
            input_text += "A sample of the data (first few rows):\n"
            for i in range(1, min(len(lines), 5)):
                input_text += f"{lines[i]}\n"
    except Exception as e:
        print(f"Error while processing file content: {e}")
        return {"error": f"An error occurred while processing the file content: {str(e)}"}

    input_text += f"\nUser plotting request: {prompt}\n\n"
    
    input_text += "IMPORTANT INSTRUCTIONS FOR CODE GENERATION:\n"
    input_text += "- The required libraries are ALREADY IMPORTED. Do NOT import any additional libraries.\n"
    input_text += "- Use the following aliases ONLY: `pd` for pandas, `plt` for matplotlib.pyplot, `sns` for seaborn, and `np` for numpy. DO NOT use any other aliases or libraries.\n"
    input_text += "- The data is ALREADY LOADED into a DataFrame named `df`. Use `df` DIRECTLY for all data manipulations and plotting.\n"
    input_text += "- DO NOT handle saving the plot or call `plt.show()`. Plot saving is ALREADY HANDLED in the provided code.\n"
    input_text += "- FOLLOW THESE INSTRUCTIONS STRICTLY. Any deviation will result in errors.\n"

    print("FULL PROMPT SENT TO LLM:")
    print("========================================================================")
    print(input_text)
    print("========================================================================")
    
    is_allowed_prompt = checkPrompt(prompt)
    is_allowed_file = checkPrompt(file_content_str)
    if not (is_allowed_prompt and is_allowed_file):
        return {"error": "[CRITICAL]: Prompt contains disallowed content!"} # 🚩🚩
    
    # template for the generated code (imports + data loading)
    generated_code = """
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    import os

    # Load the data
    df = pd.read_csv(data_path, encoding='latin-1')
    """
    generated_code = textwrap.dedent(generated_code)
    
    # code generation (using Ollama deepseek-r1:8b model for now)
    try:
        print("Sending request to Ollama...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "deepseek-r1:8b", "prompt": input_text, "stream": False})

        response.raise_for_status()
        response_data = response.json()
        llm_generated_code = response_data.get("response", "")

        # specific to Ollama deepseek-r1:8b model only
        llm_generated_code = llm_generated_code[llm_generated_code.find("#START") + 6 : -3]

        if not llm_generated_code:
            print("Failed to extract code from LLM response.")
            print("Raw response:", llm_generated_code)
            return {"error": "Failed to extract valid code from LLM response."}

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        return {"error": f"Failed to generate code: Could not connect to LLM service."}
    except Exception as e:
        print(f"Error during code generation phase: {e}")
        return {"error": f"Failed to generate code: {str(e)}"}
    
    generated_code += llm_generated_code
    
    generated_code += "\nplt.savefig(output_image_path)\n"
    
    print("========================================================================")
    print("CODE GENERATED BY THE LLM + GIVEN TEMPLATE:")
    print(generated_code)
    print("========================================================================")

    is_allowed_code = checkCode(generated_code)
    if not is_allowed_code:
        return {"error": "[CRITICAL]: Generated code contains disallowed content!"} # 🚩🚩

    # plot
    if generated_code:
        print("Handling generated code...")
        plot_image_bytes = handle_code(generated_code, file_content_str)

        if plot_image_bytes:
            print("Returning plot image.")
            return StreamingResponse(
                io.BytesIO(plot_image_bytes), media_type="image/png"
            )
        else:
            print("handle_code did not return image bytes.")
            return {"error": "Failed to execute code or generate plot image."}
    else:
        return {"error": "No code was generated to execute."}
