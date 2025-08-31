#!/bin/bash

echo "Verifying School Fee App environment setup..."

# Check Python version
echo "Python version: $(python3 --version)"

# Check pip version
echo "pip version: $(pip --version)"

# Check Docker version
echo "Docker version: $(docker --version)"

# Check Docker Compose version
echo "Docker Compose version: $(docker-compose --version)"

# Check if containers are running
echo "Checking running containers:"
docker-compose ps

# Check if ports are accessible
echo "Checking if ports are open:"
for port in 8000 5432; do
    if nc -z localhost $port; then
        echo "Port $port is open and accessible"
    else
        echo "Port $port is not accessible"
    fi
done

echo "Verification completed!"
