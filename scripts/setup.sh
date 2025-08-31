#!/bin/bash

echo "Setting up School Fee App development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "Docker is running."

# Build and start containers
echo "Building and starting Docker containers..."
docker-compose up --build -d

# Wait for database to be ready
echo "Waiting for database to be ready..."
sleep 10

# Check if containers are running
echo "Checking container status..."
if docker-compose ps | grep -q "Up"; then
    echo "Containers are running successfully!"
    echo "Django Admin: http://localhost:8000/admin"
    echo "API: http://localhost:8000/api/"
    echo "Database: postgresql://localhost:5432/school_fee_db"
else
    echo "Some containers failed to start. Check logs with: docker-compose logs"
    exit 1
fi

# Install Python dependencies in the container
echo "Installing Python dependencies in the container..."
docker-compose exec app pip install -r requirements.txt

echo "Setup completed successfully!"
echo "To create a Django superuser: docker-compose exec app python manage.py createsuperuser"
echo "To run migrations: docker-compose exec app python manage.py migrate"
