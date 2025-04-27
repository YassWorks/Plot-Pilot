# this file is meant to handle the raw python code
# that the LLM generated
# we must be careful of LLM injections and hallucinations
# a user could send a malicious code and we must not execute it

def handle_code(code: str):
    
    with open("output.py", "w") as file:
        file.write(code)