FROM python:3.10-slim

WORKDIR /app

COPY requirements_executor.txt .
RUN pip install --no-cache-dir -r requirements_executor.txt

# Copy the execution script helper
COPY execute_code.py .

# The entrypoint will run the helper script
ENTRYPOINT ["python", "execute_code.py"]