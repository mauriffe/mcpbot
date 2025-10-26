# Use an official lightweight Python image
FROM python:3.13-slim
LABEL authors="mauriffe"
# Set the working directory inside the container
# This is where your code will live and run
WORKDIR /usr/src/app

# Install system dependencies (nmap) and clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends nmap net-tools curl && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the contents of your 'src' folder into the working directory
COPY ./src/mcpbot/server .

# The command to run your application
# This is the container's default process
CMD ["python", "server.py"]