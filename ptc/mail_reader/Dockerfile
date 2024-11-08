FROM --platform=linux/amd64 python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update &&  apt-get install -y git

# Create a working directory
WORKDIR /app

# Copy only the requirements file and install dependencies
COPY ./mail_reader .
RUN pip install --no-cache-dir -r requirements.txt

# Install klinklang
COPY ../klinklang /app/klinklang
COPY ../pyproject.toml /app/pyproject.toml
RUN pip install .

# Command to run the start script
CMD [ "python", "index.py" ]
