# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install dependencies
RUN pip install flask requests psycopg2-binary

# Set environment variables for Flask
ENV FLASK_APP=server.py

# Run the application on the specified port
CMD ["flask", "run", "--host=0.0.0.0"]