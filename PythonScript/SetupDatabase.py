import pandas as pd
import json
from sqlalchemy import create_engine, Column, String, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry
import uuid

# Database connection details
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "TravelCities"
DB_USER = "postgres"
DB_PASSWORD = "Jacket123123"
CSV_FILE = r"E:\CLASS\DataVisualization\WorldWideTravelCities\WorldwideTravelCities.csv"

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

    def __repr__(self):
        return f"<TravelCity(city='{self.city}', country='{self.country}')>"

# Create the table in the database (if it doesn't exist)
# This will also enable PostGIS if not already enabled on the database,
# but it's good practice to enable it manually via SQL: CREATE EXTENSION postgis;
try:
    Base.metadata.create_all(engine)
    print("Table 'travel_cities' ensured to exist.")
except Exception as e:
    print(f"Error creating table: {e}")
    print("Please ensure the 'postgis' extension is enabled in your database (e.g., via 'CREATE EXTENSION postgis;' in psql).")

# Load data from CSV
try:
    df = pd.read_csv(CSV_FILE)
    print(f"Successfully loaded data from {CSV_FILE}. Shape: {df.shape}")
    print("Columns:", df.columns.tolist())
    # print("\nFirst 5 rows of the dataframe:")
    # print(df.head())
except FileNotFoundError:
    print(f"Error: The file '{CSV_FILE}' was not found.")
    exit()
except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit()

# Data preprocessing
def parse_json_string(json_str):
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None

df['avg_temp_monthly'] = df['avg_temp_monthly'].apply(parse_json_string)
df['ideal_durations'] = df['ideal_durations'].apply(parse_json_string)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Insert data into the database
print("\nStarting data insertion...")
inserted_count = 0
try:
    for index, row in df.iterrows():
        # Handle potential UUID conversion issues if 'id' column from CSV is not UUID-like
        try:
            row_id = uuid.UUID(row['id'])
        except ValueError:
            row_id = uuid.uuid4() # Generate a new UUID if the one from CSV is invalid

        # Create a WKT (Well-Known Text) representation for the POINT geometry
        # Note: PostGIS expects (longitude latitude) order for POINT
        point_wkt = f"POINT({row['longitude']} {row['latitude']})"

        city_data = TravelCity(
            id=row_id,
            city=row['city'],
            country=row['country'],
            region=row['region'],
            short_description=row['short_description'],
            latitude=row['latitude'],
            longitude=row['longitude'],
            geometry=point_wkt, # Assign WKT string directly
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
    print(f"Successfully inserted {inserted_count} records into 'travel_cities' table.")

except Exception as e:
    session.rollback()
    print(f"An error occurred during data insertion: {e}")
finally:
    session.close()
    print("Database session closed.")

