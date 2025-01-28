# Stage 1: Build the frontend
FROM node:18 AS frontend-builder
WORKDIR /frontend
COPY ./frontend /frontend
RUN npm install && npm run build

# Stage 3: Final image
FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (including Node.js and npm)
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

WORKDIR /backend
COPY ./backend /backend
RUN pip3 install --no-cache-dir -r /backend/requirements.txt

# Copy built frontend files
COPY --from=frontend-builder /frontend/build /frontend/build


# Install serve globally
RUN npm install -g serve \
    npm install -g concurrently


# Create directories
RUN mkdir -p /m3us /results /jellyfin/movies /jellyfin/tvshows
WORKDIR /
# Expose ports
EXPOSE 8001 3000

# Run the application
CMD ["concurrently", "--kill-others", "\"python3 /backend/main.py\"", "\"serve -s /frontend/build -l 3000\""]