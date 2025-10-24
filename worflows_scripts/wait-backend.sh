#!/bin/bash

echo "Waiting for backend service to be healthy..."

# Loop until the backend responds successfully
until curl -f http://localhost:5000/health; do
  echo "Backend not ready yet, waiting..."
  sleep 5
done

echo "Backend is healthy!"
