from flask import Flask, jsonify, request
import pandas as pd
import json
from sqlalchemy import create_engine, Column, String, Float, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry
import uuid
import os
from sqlalchemy.sql import text # For executing raw SQL like CREATE EXTENSION
from flask_cors import CORS # <--- ADD THIS LINE

app = Flask(__name__)
CORS(app)  

# Database connection details (replace with your actual credentials if different)
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "TravelCities"
DB_USER = "postgres"
DB_PASSWORD = "Jacket123123"
CSV_FILE = "input_file_0.csv"

# Construct the database URL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Define the base for declarative models
Base = declarative_base()

# Define the table structure using SQLAlchemy ORM
class TravelCity(Base):
    __tablename__ = 'travel_cities'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city = Column(String)
    country = Column(String)
    region = Column(String)
    short_description = Column(Text)
    latitude = Column(Float)
    longitude = Column(Float)
    geometry = Column(Geometry(geometry_type='POINT', srid=4326)) # SRID 4326 for WGS 84 (latitude, longitude)
    avg_temp_monthly = Column(JSONB)
    ideal_durations = Column(JSONB)
    budget_level = Column(String)
    culture = Column(Integer)
    adventure = Column(Integer)
    nature = Column(Integer)
    beaches = Column(Integer)
    nightlife = Column(Integer)
    cuisine = Column(Integer)
    wellness = Column(Integer)
    urban = Column(Integer)
    seclusion = Column(Integer)

    def to_dict(self):
        """Converts the SQLAlchemy object to a dictionary for JSON serialization."""
        return {
            "id": str(self.id),
            "city": self.city,
            "country": self.country,
            "region": self.region,
            "short_description": self.short_description,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "avg_temp_monthly": self.avg_temp_monthly,
            "ideal_durations": self.ideal_durations,
            "budget_level": self.budget_level,
            "culture": self.culture,
            "adventure": self.adventure,
            "nature": self.nature,
            "beaches": self.beaches,
            "nightlife": self.nightlife,
            "cuisine": self.cuisine,
            "wellness": self.wellness,
            "urban": self.urban,
            "seclusion": self.seclusion,
            # 'geometry': self.geometry.wkt # You could include WKT if needed, but lat/lon are usually sufficient
        }

    def __repr__(self):
        return f"<TravelCity(city='{self.city}', country='{self.country}')>"

# Function to parse JSON strings safely from CSV
def parse_json_string(json_str):
    try:
        if pd.isna(json_str) or not json_str.strip():
            return None
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Warning: Could not parse JSON string '{json_str}' during CSV load. Error: {e}")
        return None

# --- Flask Routes ---

@app.route('/')
def index():
    return "Welcome to the Travel Cities API. Use /load-data, /search, or /recommend endpoints."

@app.route('/load-data', methods=['POST'])
def load_data_endpoint():
    """
    Endpoint to load data from the CSV file into the database.
    This should typically be a one-time operation or triggered by an admin.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    inserted_count = 0

    try:
        # Ensure PostGIS extension is enabled and table exists
        with engine.connect() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            connection.commit()
        print("PostGIS extension ensured to exist.")
        Base.metadata.create_all(engine)
        print("Table 'travel_cities' ensured to exist.")

        if not os.path.exists(CSV_FILE):
            return jsonify({"status": "error", "message": f"CSV file '{CSV_FILE}' not found."}), 404

        df = pd.read_csv(CSV_FILE)
        print(f"Successfully loaded data from {CSV_FILE} into DataFrame. Shape: {df.shape}")

        # Data preprocessing
        df['avg_temp_monthly'] = df['avg_temp_monthly'].apply(parse_json_string)
        df['ideal_durations'] = df['ideal_durations'].apply(parse_json_string)

        # Insert data into the database
        print("Starting data insertion into database...")
        for index, row in df.iterrows():
            try:
                # Use str(row['id']) to handle potential non-string UUIDs from CSV
                row_id = uuid.UUID(str(row['id']))
            except ValueError:
                row_id = uuid.uuid4() # Generate a new UUID if the one from CSV is invalid

            # Create a WKT (Well-Known Text) representation for the POINT geometry
            point_wkt = f"POINT({row['longitude']} {row['latitude']})"

            city_data = TravelCity(
                id=row_id,
                city=row['city'],
                country=row['country'],
                region=row['region'],
                short_description=row['short_description'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                geometry=point_wkt,
                avg_temp_monthly=row['avg_temp_monthly'],
                ideal_durations=row['ideal_durations'],
                budget_level=row['budget_level'],
                culture=row['culture'],
                adventure=row['adventure'],
                nature=row['nature'],
                beaches=row['beaches'],
                nightlife=row['nightlife'],
                cuisine=row['cuisine'],
                wellness=row['wellness'],
                urban=row['urban'],
                seclusion=row['seclusion']
            )
            session.add(city_data)
            inserted_count += 1
        
        session.commit()
        return jsonify({"status": "success", "message": f"Successfully inserted {inserted_count} records into 'travel_cities' table."}), 200

    except Exception as e:
        session.rollback()
        error_message = f"An error occurred during data loading: {e}"
        print(error_message)
        return jsonify({"status": "error", "message": error_message}), 500
    finally:
        session.close()
        print("Database session closed.")

@app.route('/search_cities', methods=['GET'])
def search_cities():
    """
    Endpoint to search/filter cities.
    Query parameters:
    - city: Filter by city name (case-insensitive, partial match)
    - region: Filter by region (case-insensitive, partial match)
    - budget_level: Filter by budget level (e.g., 'Luxury', 'Mid-range', 'Budget')
    - limit: Number of results to return (default 20)
    - offset: Number of results to skip (default 0)
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    query = session.query(TravelCity)
    print("Received search request with parameters:", request.args)

    # 1. Filter by city
    city_name = request.args.get('city')
    if city_name:
        query = query.filter(func.lower(TravelCity.city).like(f"%{city_name.lower()}%"))

    # 2. Filter by region
    region_name = request.args.get('region')
    if region_name:
        query = query.filter(func.lower(TravelCity.region).like(f"%{region_name.lower()}%"))

    # 3. Filter by budget_level
    budget = request.args.get('budget_level')
    if budget:
        query = query.filter(func.lower(TravelCity.budget_level) == budget.lower())
    
    # Pagination
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    query = query.limit(limit).offset(offset)

    try:
        results = query.all()
        cities_data = [city.to_dict() for city in results]
        return jsonify(cities_data), 200
    except Exception as e:
        error_message = f"An error occurred during search: {e}"
        print(error_message)
        return jsonify({"status": "error", "message": error_message}), 500
    finally:
        session.close()

@app.route('/recommend', methods=['POST'])
def recommend_cities():
    """
    Endpoint to get cities ranked by custom importance weights.
    Request Body (JSON):
    {
        "rank_weights": {
            "culture": 5,
            "adventure": 3,
            "nature": 4,
            "beaches": 2,
            "nightlife": 1,
            "cuisine": 5,
            "wellness": 3,
            "urban": 4,
            "seclusion": 1
        },
        "filters": { # Optional filters, same as /search endpoint
            "region": "europe",
            "budget_level": "Mid-range"
        },
        "limit": 10,
        "offset": 0
    }
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    data = request.get_json()

    if not data or 'rank_weights' not in data:
        return jsonify({"status": "error", "message": "Missing 'rank_weights' in request body."}), 400

    rank_weights = data['rank_weights']
    filters = data.get('filters', {})
    limit = data.get('limit', 20, type=int)
    offset = data.get('offset', 0, type=int)

    # Define the columns that can be used for ranking
    rankable_columns = {
        "culture": TravelCity.culture,
        "adventure": TravelCity.adventure,
        "nature": TravelCity.nature,
        "beaches": TravelCity.beaches,
        "nightlife": TravelCity.nightlife,
        "cuisine": TravelCity.cuisine,
        "wellness": TravelCity.wellness,
        "urban": TravelCity.urban,
        "seclusion": TravelCity.seclusion
    }

    # Build the scoring expression
    score_expression = 0
    for category, weight in rank_weights.items():
        if category in rankable_columns and isinstance(weight, (int, float)):
            score_expression += (rankable_columns[category] * weight)
        else:
            print(f"Warning: Invalid category '{category}' or weight '{weight}' in rank_weights. Skipping.")

    if score_expression == 0:
        return jsonify({"status": "error", "message": "No valid rank_weights provided for scoring."}), 400

    query = session.query(TravelCity, score_expression.label('score'))

    # Apply filters
    city_name = filters.get('city')
    if city_name:
        query = query.filter(func.lower(TravelCity.city).like(f"%{city_name.lower()}%"))

    region_name = filters.get('region')
    if region_name:
        query = query.filter(func.lower(TravelCity.region).like(f"%{region_name.lower()}%"))

    budget = filters.get('budget_level')
    if budget:
        query = query.filter(func.lower(TravelCity.budget_level) == budget.lower())

    # Order by the calculated score (descending)
    query = query.order_by(func.coalesce(score_expression, 0).desc()) # Use coalesce to handle potential None values in score calculation

    # Pagination
    query = query.limit(limit).offset(offset)

    try:
        results = query.all()
        # results are tuples: (TravelCity object, score)
        cities_data = []
        for city_obj, score in results:
            city_dict = city_obj.to_dict()
            city_dict['score'] = score # Add the calculated score to the response
            cities_data.append(city_dict)
            
        return jsonify(cities_data), 200
    except Exception as e:
        session.rollback()
        error_message = f"An error occurred during recommendation: {e}"
        print(error_message)
        return jsonify({"status": "error", "message": error_message}), 500
    finally:
        session.close()

@app.route('/city_counts_by_region', methods=['GET'])
def get_city_counts_by_region():
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        # Group by region and count cities
        results = session.query(
            TravelCity.region,
            func.count(TravelCity.id)
        ).group_by(TravelCity.region).all()

        # Format the results for frontend consumption
        data = []
        for region, count in results:
            if region: # Filter out potential None or empty regions
                data.append({"name": region, "value": count})

        return jsonify(data), 200
    except Exception as e:
        session.rollback()
        error_message = f"An error occurred while fetching city counts by region: {e}"
        print(error_message)
        return jsonify({"status": "error", "message": error_message}), 500
    finally:
        session.close()

@app.route('/city_counts_by_country_in_region', methods=['GET'])
def get_city_counts_by_country_in_region():
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        region_name = request.args.get('region')
        if not region_name:
            return jsonify({"status": "error", "message": "Region parameter is required."}), 400

        # Filter by region, then group by country and count cities
        results = session.query(
            TravelCity.country,
            func.count(TravelCity.id)
        ).filter(
            func.lower(TravelCity.region) == region_name.lower()
        ).group_by(TravelCity.country).all()

        # Format the results
        data = []
        for country, count in results:
            if country: # Filter out potential None or empty countries
                data.append({"name": country, "value": count})

        return jsonify(data), 200
    except Exception as e:
        session.rollback()
        error_message = f"An error occurred while fetching city counts by country in region '{region_name}': {e}"
        print(error_message)
        return jsonify({"status": "error", "message": error_message}), 500
    finally:
        session.close()

@app.route('/get_short_description_text', methods=['GET']) # Renamed endpoint
def get_short_description_text():
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        region = request.args.get('region')
        country = request.args.get('country')
        city = request.args.get('city')

        query = session.query(TravelCity.short_description) # Querying 'short_description' column

        if city:
            query = query.filter(func.lower(TravelCity.city) == city.lower())
        elif country:
            query = query.filter(func.lower(TravelCity.country) == country.lower())
        elif region:
            query = query.filter(func.lower(TravelCity.region) == region.lower())

        short_description_data = query.all() # Renamed variable
        
        # Concatenate all non-empty short_descriptions
        full_text = " ".join([sd[0] for sd in short_description_data if sd[0] is not None and sd[0].strip() != ""])

        return jsonify({"text": full_text}), 200
    except Exception as e:
        session.rollback()
        print(f"Error fetching short description text: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        session.close()

@app.route('/search_countries', methods=['GET'])
def search_countries():
    """
    Endpoint to search for countries, optionally filtered by region.
    Query parameters:
    - region: Filter countries within a specific region (case-insensitive, exact match)
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        region_name = request.args.get('region')
        
        query = session.query(TravelCity.country).distinct()

        if region_name:
            query = query.filter(func.lower(TravelCity.region) == region_name.lower())
        
        countries = query.order_by(TravelCity.country).all()
        # Extract country names and filter out any None or empty strings
        country_list = [c[0] for c in countries if c[0] is not None and c[0].strip() != ""]

        return jsonify(country_list), 200
    except Exception as e:
        session.rollback()
        error_message = f"An error occurred while searching for countries: {e}"
        print(error_message)
        return jsonify({"status": "error", "message": error_message}), 500
    finally:
        session.close()
        
if __name__ == '__main__':
    # This runs the Flask development server.
    # For production, use a WSGI server like Gunicorn or uWSGI.
    app.run(debug=True, host='0.0.0.0', port=5000)