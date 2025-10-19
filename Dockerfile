# Specify a stable Python 3.12 image
FROM python:3.12-slim

# Install the necessary PostgreSQL development packages
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /usr/src/app

# === CORRECTED: Copy the requirements file from the ROOT directory ===
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code (backend/, frontend/, etc.)
COPY . .

# Change directory to run alembic relative to its config
WORKDIR /usr/src/app/backend

# Run the database migrations (finds alembic.ini in current dir)
RUN alembic upgrade head

# Change back to the app root for the CMD
WORKDIR /usr/src/app

# Define the command to run the web service
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "10000"]