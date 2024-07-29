# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies and Pandoc
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    wget \
    software-properties-common \
    git \
    && ARCH=$(dpkg --print-architecture) \
    && curl -s https://api.github.com/repos/jgm/pandoc/releases/latest \
    | grep "browser_download_url.*${ARCH}.deb" \
    | cut -d : -f 2,3 \
    | tr -d \" \
    | wget -qi - \
    && dpkg -i pandoc-*.deb \
    && rm pandoc-*.deb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME=World

# Run app.py when the container launches
CMD ["streamlit", "run", "app.py", "--server.port=8000", "--server.address=0.0.0.0"]