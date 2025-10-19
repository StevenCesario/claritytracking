# Specify a stable Python 3.12 image
FROM python:3.12-slim

# Install the necessary PostgreSQL development packages
# (libpq-dev is needed for psycopg to compile)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the backend requirements file
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the database migrations
# We must set the DATABASE_URL as a build-time secret
# for this command to work.
RUN alembic upgrade head

# Define the command to run the web service
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "10000"]