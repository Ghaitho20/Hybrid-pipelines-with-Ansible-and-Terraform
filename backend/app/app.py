from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time

# Load environment variables from .env file
load_dotenv() 

PORT_SERVER = os.getenv('FLASK_PORT')
FLASK_HOST=os.getenv('FLASK_HOST')
FLASK_DEBUG=os.getenv('FLASK_DEBUG')


app = Flask(__name__)
CORS(app)
POSTGRES_DB=os.getenv('POSTGRES_DB')
POSTGRES_USER=os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')
POSTGRES_SERVICE=os.getenv('POSTGRES_SERVICE')
POSTGRES_PORT=os.getenv('POSTGRES_PORT')

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP Request Duration')
DB_CONNECTION_ERRORS = Counter('db_connection_errors_total', 'Database Connection Errors')


DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVICE}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)


@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    # Calculate request duration
    duration = time.time() - getattr(request, 'start_time', time.time())
    REQUEST_DURATION.observe(duration)
    
    # Count requests
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    
    return response

@app.route("/health")
def health():
    return "OK", 200

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}




@app.route('/api/trees/stats/arrondissements')
def trees_by_arrondissement():
    """Nombre d'arbres par arrondissement"""
    with engine.connect() as conn:
        query = text("""
            SELECT arrondissement, COUNT(*) as count 
            FROM arbres1 
            WHERE arrondissement IS NOT NULL 
            GROUP BY arrondissement 
            ORDER BY count DESC
        """)
        result = conn.execute(query)
        data = [{"arrondissement": row[0], "count": row[1]} for row in result]
        return jsonify(data)

@app.route('/api/trees/stats/species')
def trees_by_species():
    """Top 10 des espèces les plus communes"""
    with engine.connect() as conn:
        query = text("""
            SELECT espece, COUNT(*) as count 
            FROM arbres1 
            WHERE espece IS NOT NULL AND espece != ''
            GROUP BY espece 
            ORDER BY count DESC 
            LIMIT 10
        """)
        result = conn.execute(query)
        data = [{"espece": row[0], "count": row[1]} for row in result]
        return jsonify(data)

@app.route('/api/trees/stats/height')
def trees_height_stats():
    """Statistiques de hauteur par espèce"""
    with engine.connect() as conn:
        query = text("""
            SELECT espece, 
                   AVG(hauteur) as avg_height,
                   MAX(hauteur) as max_height,
                   COUNT(*) as count
            FROM arbres1 
            WHERE hauteur IS NOT NULL AND espece IS NOT NULL
            GROUP BY espece
            HAVING COUNT(*) > 5
            ORDER BY avg_height DESC
            LIMIT 15
        """)
        result = conn.execute(query)
        data = [{
            "espece": row[0], 
            "avg_height": float(row[1]) if row[1] else 0,
            "max_height": float(row[2]) if row[2] else 0,
            "count": row[3]
        } for row in result]
        return jsonify(data)

@app.route('/api/trees/stats/remarkable')
def remarkable_trees():
    """Arbres remarquables par arrondissement"""
    with engine.connect() as conn:
        query = text("""
            SELECT arrondissement, 
                   COUNT(*) as total_trees,
                   SUM(CASE WHEN remarquable = 1 THEN 1 ELSE 0 END) as remarkable_trees
            FROM arbres1 
            WHERE arrondissement IS NOT NULL
            GROUP BY arrondissement
            ORDER BY remarkable_trees DESC
        """)
        result = conn.execute(query)
        data = [{
            "arrondissement": row[0],
            "total_trees": row[1],
            "remarkable_trees": row[2],
            "remarkable_percentage": round((row[2] / row[1]) * 100, 2) if row[1] > 0 else 0
        } for row in result]
        return jsonify(data)

@app.route('/api/trees/geolocation')
def trees_geolocation():
    """Données de géolocalisation pour la carte"""
    with engine.connect() as conn:
        query = text("""
            SELECT idbase, nom, espece, hauteur, circonference, remarquable, lon, lat
            FROM arbres1 
            WHERE lon IS NOT NULL AND lat IS NOT NULL
            LIMIT 1000
        """)
        result = conn.execute(query)
        data = [{
            "id": row[0],
            "nom": row[1],
            "espece": row[2],
            "hauteur": float(row[3]) if row[3] else None,
            "circonference": float(row[4]) if row[4] else None,
            "remarquable": bool(row[5]),
            "longitude": float(row[6]),
            "latitude": float(row[7])
        } for row in result]
        return jsonify(data)
    

if __name__ == '__main__':
    print("#################")
    print(PORT_SERVER)
    print("#################")
    print(FLASK_HOST)
    print("#################")
    print(FLASK_DEBUG)
    app.run(host=FLASK_HOST, port=PORT_SERVER, debug=FLASK_DEBUG)