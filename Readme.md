# Paris Trees Data Visualization


## Project Overview
Data visualization of Paris trees using OpenData Paris API.

## Architecture
- **Frontend**: HTML/CSS/JS with Chart.js and Leaflet maps
- **Backend**: Flask API with SQLAlchemy
- **Database**: PostgreSQL
- **Infrastructure**: Docker with nginx reverse proxy

## Quick Start

```bash
# 2. Start all services
docker-compose up -d --build

# 3. Access the application
# Frontend: http://localhost
# Backend API: http://localhost:5000
# Database: localhost:5432

