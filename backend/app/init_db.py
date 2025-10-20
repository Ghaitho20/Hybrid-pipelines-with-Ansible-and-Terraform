import os
from sqlalchemy import create_engine, text

def init_database():
    POSTGRES_DB=os.getenv('POSTGRES_DB')
    POSTGRES_USER=os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')
    POSTGRES_SERVICE=os.getenv('POSTGRES_SERVICE')
    POSTGRES_PORT=os.getenv('POSTGRES_PORT')

    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVICE}:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # This will automatically create the database if using PostgreSQL
        print("Database connection successful!")
        
        # Create table if not exists
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS arbres1 (
            idbase INTEGER PRIMARY KEY,
            arrondissement VARCHAR,
            adresse VARCHAR,
            nom VARCHAR,
            genre VARCHAR,
            espece VARCHAR,
            variete VARCHAR,
            hauteur FLOAT,
            circonference FLOAT,
            stade VARCHAR,
            remarquable INTEGER,
            lon FLOAT,
            lat FLOAT
        );
        """
        conn.execute(text(create_table_sql))
        conn.commit()
        print("Table 'arbres1' created or already exists!")

if __name__ == "__main__":
    init_database()