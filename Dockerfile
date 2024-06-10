# Use the official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY src src
COPY app.py app.py

# Expose the port that Streamlit uses
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "app.py"]
