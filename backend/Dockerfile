FROM python:3.10-slim

WORKDIR /app

# Install system dependencies that might be needed by libraries (optional, add if needed)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

COPY ./app /app/app

COPY ./executor /app/executor

EXPOSE 5000

# Define environment variables (optional)
# ENV NAME World

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]