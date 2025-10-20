import requests
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData
import os

from sqlalchemy import text




POSTGRES_DB=os.getenv('POSTGRES_DB')
POSTGRES_USER=os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD')
POSTGRES_SERVICE=os.getenv('POSTGRES_SERVICE')
POSTGRES_PORT=os.getenv('POSTGRES_PORT')
limit = int(os.getenv('LIMIT_EXAMPLES'))

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVICE}:{POSTGRES_PORT}/{POSTGRES_DB}" 






def extract(limit):
    if limit > 100:
        print(f"Warning: limit {limit} is greater than 100. Using 100 instead.")
        limit = 100  
    
    url = f"https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/les-arbres/records?limit={limit}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # raise error if request failed
        data = response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        exit(1)

    # Extract list of trees
    arbres = data.get("results", [])
    return arbres

def transform(arbres):
    trees_data = []
    for arbre in arbres:
        tree = {}

        # Ensure idbase exists
        idbase = arbre.get("idbase")
        if not idbase:
            continue
        tree["idbase"] = idbase

        tree["type_emplacement"] = (arbre.get("typeemplacement") or "").strip().capitalize()
        tree["domanialite"] = (arbre.get("domanialite") or "").strip().capitalize()
        tree["arrondissement"] = (arbre.get("arrondissement") or "").upper()

        tree["adresse_complete"] = " ".join(
            filter(None, [arbre.get("complementadresse"), arbre.get("adresse")])
        )

        tree["libelle"] = (arbre.get("libellefrancais") or "").capitalize()
        tree["genre"] = (arbre.get("genre") or "").capitalize()
        tree["espece"] = arbre.get("espece", "")
        tree["variete"] = arbre.get("varieteoucultivar")
        tree["circonference_cm"] = arbre.get("circonferenceencm") or None
        tree["hauteur_m"] = arbre.get("hauteurenm") or None

        stade = arbre.get("stadedeveloppement")
        if stade:
            stade = stade.replace("Jeune (arbre)", "Jeune")
        tree["stade"] = stade or None

        tree["remarquable"] = (
            1 if arbre.get("remarquable") == "OUI"
            else 0 if arbre.get("remarquable") == "NON"
            else None
        )

        geo = arbre.get("geo_point_2d") or {}
        tree["latitude"] = geo.get("lat")
        tree["longitude"] = geo.get("lon")

        trees_data.append(tree)


    return trees_data


def load(trees_data):
    try:
        engine = create_engine(DATABASE_URL)
        metadata = MetaData()

        trees_table = Table(
            "arbres1", metadata,
            Column("idbase", Integer, primary_key=True),
            Column("arrondissement", String),
            Column("adresse", String),
            Column("nom", String),
            Column("genre", String),
            Column("espece", String),
            Column("variete", String),
            Column("hauteur", Float),
            Column("circonference", Float),
            Column("stade", String),
            Column("remarquable", Integer),
            Column("lon", Float),
            Column("lat", Float)
        )

        metadata.create_all(engine)
        from sqlalchemy.dialects.postgresql import insert

        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE arbres1 RESTART IDENTITY"))
            for tree in trees_data:
                mapped_tree = {
                    "idbase": tree.get("idbase"),
                    "arrondissement": tree.get("arrondissement"),
                    "adresse": tree.get("adresse_complete"),
                    "nom": tree.get("libelle"),
                    "genre": tree.get("genre"),
                    "espece": tree.get("espece"),
                    "variete": tree.get("variete"),
                    "hauteur": tree.get("hauteur_m"),
                    "circonference": tree.get("circonference_cm"),
                    "stade": tree.get("stade"),
                    "remarquable": tree.get("remarquable"),
                    "lon": tree.get("longitude"),
                    "lat": tree.get("latitude")
                }

                stmt = insert(trees_table).values(**mapped_tree)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["idbase"],
                    set_={k: mapped_tree[k] for k in mapped_tree if k != "idbase"}
                )
                conn.execute(stmt)

        print("Data successfully inserted into 'arbres1' table!")

    except Exception as e:
        print(f"Database error: {e}")

def main():
    """
    Main function to execute the ETL pipeline
    """
    print("Starting ETL pipeline...")
    
    # Extract
    print("Extracting data from API...")
    raw_data = extract(limit)
    print(f"Extracted {len(raw_data)} records")
    
    # Transform
    print("Transforming data...")
    transformed_data = transform(raw_data)
    print(f"Transformed {len(transformed_data)} records")
    
    # Load
    print("Loading data into database...")
    load(transformed_data)
    print("ETL pipeline completed successfully!")

if __name__ == "__main__":
    main()