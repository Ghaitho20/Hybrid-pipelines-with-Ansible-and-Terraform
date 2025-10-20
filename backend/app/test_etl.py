import os
import pytest
from unittest.mock import patch, MagicMock

# ----------------------
# Set fake env vars
# ----------------------
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_PASSWORD"] = "123456"
os.environ["POSTGRES_DB"] = "parisdb"
os.environ["POSTGRES_SERVICE"] = "localhost"
os.environ["POSTGRES_PORT"] = "5432"
os.environ["LIMIT_EXAMPLES"] = "10"

import etl

# ----------------------
# Test transform function (pure function)
# ----------------------
def test_transform():
    sample_input = [
        {
            "idbase": 1,
            "typeemplacement": "alignement",
            "domanialite": "Public",
            "arrondissement": "PARIS 1ER",
            "adresse": "Rue de Test",
            "libellefrancais": "Chêne",
            "genre": "Quercus",
            "espece": "robur",
            "varieteoucultivar": "Var1",
            "circonferenceencm": 30,
            "hauteurenm": 10,
            "stadedeveloppement": "Jeune (arbre)",
            "remarquable": "OUI",
            "geo_point_2d": {"lat": 48.8566, "lon": 2.3522}
        }
    ]

    result = etl.transform(sample_input)
    assert len(result) == 1
    tree = result[0]
    assert tree["idbase"] == 1
    assert tree["stade"] == "Jeune"
    assert tree["remarquable"] == 1
    assert tree["latitude"] == 48.8566
    assert tree["longitude"] == 2.3522

# ----------------------
# Test extract function with mocked requests
# ----------------------
@patch("etl.requests.get")
def test_extract(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"results": ["tree1", "tree2"]}
    mock_response.raise_for_status = lambda: None
    mock_get.return_value = mock_response

    result = etl.extract(limit=2)
    assert result == ["tree1", "tree2"]

# ----------------------
# Test load function with mocked create_engine
# ----------------------
@patch("etl.create_engine")
def test_load(mock_create_engine):
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    sample_data = [
        {
            "idbase": 1,
            "arrondissement": "PARIS 1ER",
            "adresse_complete": "Rue de Test",
            "libelle": "Chêne",
            "genre": "Quercus",
            "espece": "robur",
            "variete": "Var1",
            "hauteur_m": 10,
            "circonference_cm": 30,
            "stade": "Jeune",
            "remarquable": 1,
            "longitude": 2.3522,
            "latitude": 48.8566
        }
    ]

    etl.load(sample_data)
    # Check that the engine was created
    mock_create_engine.assert_called_once()
    # Check that the connection was used
    assert mock_engine.begin.called

# ----------------------
# Test main function with extract/load mocked
# ----------------------
@patch("etl.extract", return_value=[])
@patch("etl.load")
def test_main(mock_load, mock_extract):
    etl.main()
    mock_extract.assert_called_once()
    mock_load.assert_called_once()
