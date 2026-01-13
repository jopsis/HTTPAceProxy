#!/bin/bash

# HTTPAceProxy Quick Start Script

echo "================================================"
echo "HTTPAceProxy with NewEra Plugin - Quick Start"
echo "================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed."
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed."
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
fi

echo "Building Docker image..."
docker-compose build

echo ""
echo "Starting HTTPAceProxy container..."
docker-compose up -d

echo ""
echo "Waiting for service to start..."
sleep 5

# Check if service is running
if curl -s http://localhost:8001/stat > /dev/null; then
    echo ""
    echo "================================================"
    echo "✓ HTTPAceProxy is running successfully!"
    echo "================================================"
    echo ""
    echo "Access URLs:"
    echo "  - Playlist: http://localhost:8001/newera.m3u8"
    echo "  - Stats:    http://localhost:8001/stat"
    echo ""
    echo "Commands:"
    echo "  - View logs:    docker-compose logs -f"
    echo "  - Stop:         docker-compose down"
    echo "  - Restart:      docker-compose restart"
    echo ""
    echo "Or use: make help"
    echo "================================================"
else
    echo ""
    echo "================================================"
    echo "✗ Service failed to start. Check logs with:"
    echo "  docker-compose logs"
    echo "================================================"
    exit 1
fi
