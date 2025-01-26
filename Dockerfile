# Use Ubuntu as base image
FROM ubuntu:20.04

# Set environment to non-interactive mode to avoid prompts during installs
ENV DEBIAN_FRONTEND=noninteractive

# Install curl and other required packages
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    ffmpeg \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js (version 18.x)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory for backend
WORKDIR /backend

# Copy backend files
COPY ./backend /backend

# Install Python dependencies for the backend
RUN pip3 install --no-cache-dir -r /backend/requirements.txt

# Set working directory for frontend
WORKDIR /frontend

# Copy frontend files
COPY ./frontend /frontend

# Install npm dependencies and build the production-ready frontend
RUN npm install && npm run build

# Install a lightweight HTTP server to serve the static frontend files
RUN npm install -g serve

# Copy m3us files
WORKDIR /m3us

# Move to results directory
WORKDIR /results
WORKDIR /jellyfin
WORKDIR /

# Expose the backend port
EXPOSE 8001 3000

# Use a process manager like "concurrently" to run both backend and frontend
RUN npm install -g concurrently

# Set CMD to serve the production-ready frontend and run the backend
# CMD ["concurrently", "--kill-others", "\"python3 /backend/main.py\"", "\"serve -s /frontend/build -l 3000\""]
CMD ["concurrently", "--kill-others", "\"python3 /backend/main.py\"", "\"cd /frontend && serve -s build\""]
