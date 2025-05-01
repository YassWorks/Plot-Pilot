from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import requests
from helpers.handle_code import handle_code
from helpers.sanitize import checkPrompt
import io
from pathlib import Path
# import textwrap

app = FastAPI(title="Plot Pilot API")

# add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Consider restricting this in production
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
    if file_content_str:
        try:
            lines = file_content_str.splitlines()
            if lines:
                input_text += f"Extracted column names: {lines[0]}\n\n"
                input_text += "Sample data (first few rows):\n"
                for i in range(1, min(len(lines), 5)):
                    input_text += f"{lines[i]}\n"
            else:
                input_text += "Uploaded file is empty.\n"
        except Exception as e:
            print(f"Error processing file content for prompt: {e}")

    input_text += f"\nUser plotting request: {prompt}\n\n"
    input_text += "Save it using `plt.savefig('/app/output/plot.png')`. You don't need to show the plot using `plt.show()`.\n\n"

    # code generation (using Ollama deepseek-r1:8b model for now)
    try:
        is_allowed_prompt = checkPrompt(prompt)
        if not is_allowed_prompt:
            return {"error": "Prompt contains disallowed content. 🚩🚩"}

        print("Sending request to Ollama...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "deepseek-r1:8b", "prompt": input_text, "stream": False})

        response.raise_for_status()
        response_data = response.json()
        generated_code = response_data.get("response", "")

        # specific to Ollama deepseek-r1:8b model only
        generated_code = generated_code[generated_code.find("#START") + 6 : -3]

        if not generated_code:
            print("Failed to extract code from LLM response.")
            print("Raw response:", generated_code)
            return {"error": "Failed to extract valid code from LLM response."}

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        return {"error": f"Failed to generate code: Could not connect to LLM service."}
    except Exception as e:
        print(f"Error during code generation phase: {e}")
        return {"error": f"Failed to generate code: {str(e)}"}

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
