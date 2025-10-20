#!/bin/bash
set -e 
sleep 5
python init_db.py
echo "Démarrage de ETL"
python etl.py

if [ $? -eq 0 ]; then
    echo "ETL completed successfully"
    echo "Starting Flask application..."
    exec python app.py 
else 
    echo "Erreur de l'ETL"
    exit 1
fi

