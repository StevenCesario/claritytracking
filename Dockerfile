# Specify a stable Python 3.12 image
FROM python:3.12-slim

# Install the necessary PostgreSQL development packages
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /usr/src/app

# --- This is the key change ---
# Copy the *backend* requirements file first
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# (This copies the 'backend' and 'frontend' folders, etc.)
COPY . .

# Run the database migrations
RUN alembic upgrade head

# Define the command to run the web service
# This points to your main:app object inside the 'backend' folder
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "10000"]
