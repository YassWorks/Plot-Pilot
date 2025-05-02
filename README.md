# Plot Pilot 📊✈️

Your AI-powered data visualization assistant. Describe the plot you want, upload your data, and let Plot Pilot generate it!

## Features

*   **Natural Language Plotting:** Just tell Plot Pilot what kind of plot you need.
*   **Supports Your Data:** Works with common formats like CSV and Excel (`.csv`, `.xlsx`, `.xls`).
*   **AI-Generated Code:** Uses Large Language Models (LLMs) to create Python plotting code (Matplotlib, Seaborn).
*   **Secure by Design:**
    *   **Input Sanitization:** Checks your prompts and data for harmful content before sending to the AI.
    *   **Code Analysis:** Reviews the AI-generated code for dangerous commands before running.
    *   **Isolated Execution:** Runs the plotting code safely inside a restricted Docker container with no internet access.

## Stack

*   **Frontend:** Next.js, React, Tailwind CSS, TypeScript
*   **Backend:** FastAPI, Python, Docker
*   **Executor:** Matplotlib, Seaborn, Pandas, NumPy
*   **LLM Integration:** Ollama (at the time of development)