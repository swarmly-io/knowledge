# Use the official Python 3.11 image
FROM python:3.11-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY ./ /app

# Specify the command to run on container start
CMD ["python", "app.py"]
