.PHONY: help build up down restart logs shell test clean

help:
	@echo "HTTPAceProxy Docker Commands"
	@echo ""
	@echo "  make build    - Build the Docker image"
	@echo "  make up       - Start the container"
	@echo "  make down     - Stop and remove the container"
	@echo "  make restart  - Restart the container"
	@echo "  make logs     - Show container logs"
	@echo "  make shell    - Open a shell in the container"
	@echo "  make test     - Test the service is running"
	@echo "  make clean    - Remove container and image"
	@echo ""

build:
	@echo "Building Docker image..."
	docker-compose build

up:
	@echo "Starting HTTPAceProxy container..."
	docker-compose up -d
	@echo "Container started! Access at http://localhost:8888/newera.m3u8"

down:
	@echo "Stopping container..."
	docker-compose down

restart:
	@echo "Restarting container..."
	docker-compose restart

logs:
	@echo "Showing logs (Ctrl+C to exit)..."
	docker-compose logs -f

shell:
	@echo "Opening shell in container..."
	docker-compose exec httpaceproxy /bin/bash

test:
	@echo "Testing service..."
	@curl -s http://localhost:8888/stat > /dev/null && echo "✓ Service is running!" || echo "✗ Service is not responding"
	@curl -s http://localhost:8888/newera.m3u8 | head -5

clean:
	@echo "Cleaning up..."
	docker-compose down
	docker rmi httpaceproxy:latest 2>/dev/null || true
	@echo "Cleanup complete!"
