# Use an official Python runtime as a parent image
FROM python:3.11.5-slim-bullseye

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Install system dependencies if required (e.g., for psycopg2)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Django runs on (default is 8000)
EXPOSE 8000

# Define the command to run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]