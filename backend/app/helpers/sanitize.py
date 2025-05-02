# this file is meant to sanitize the prompt of the user
# before sending it to the model to concerve resources.
import re
import ast

# for the prompt & file (pre-generation)
def checkPrompt(prompt):
    dangerous_keywords = [
        r"\bsubprocess\.",       # Matches 'subprocess.' to prevent spawning processes
        r"\beval\b",             # Matches 'eval' to prevent arbitrary code execution
        r"\bexec\b",             # Matches 'exec' to prevent arbitrary code execution
        r"\brm\b",               # Matches 'rm' to prevent file deletions
        r"\bdelete\b",           # Matches 'delete' to prevent destructive operations
        r"\bimport\s+sys\b",     # Matches 'import sys' to prevent importing the sys module
        r"\bopen\s*\(",          # Matches 'open(' to prevent file operations
        r"\bshutil\.",           # Matches 'shutil.' to prevent file system operations
        r"\binput\s*\(",         # Matches 'input(' to prevent user input during execution
        r"\bexecfile\b",         # Matches 'execfile' to prevent execution of files
        r"\bcompile\b",          # Matches 'compile' to prevent dynamic code compilation
    ]
    for keyword in dangerous_keywords:
        if re.search(keyword, prompt, re.IGNORECASE):
            return False
    return True

# for the code (post-generation)
def checkCode(code):
    if not restrict_imports(code):
        return False
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ["system", "run", "popen"]:
                    return False
            elif isinstance(node.func, ast.Name):
                if node.func.id in ["eval", "exec"]:
                    return False
    return True

def restrict_imports(code):
    allowed_modules = ["pandas", "matplotlib.pyplot", "numpy", "seaborn", "os"]
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            for name in node.names:
                if name.name not in allowed_modules:
                    return False
    return True