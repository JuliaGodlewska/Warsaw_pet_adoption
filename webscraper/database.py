import sqlite3
import os
import pandas as pd

def init_db():
    conn = sqlite3.connect("pets.db")
    cursor = conn.cursor()

    # Check if the table already exists
    cursor.execute("PRAGMA table_info(pets)")
    columns = [column[1] for column in cursor.fetchall()]

    # If the table exists and the schema needs to be updated
    if "species_id" not in columns:
        # Rename the existing table
        cursor.execute("ALTER TABLE pets RENAME TO pets_old")

        # Create the new table with the updated schema
        cursor.execute('''
            CREATE TABLE pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                species_id TEXT UNIQUE,
                name TEXT,
                species TEXT,
                breed TEXT,
                age TEXT,
                gender TEXT,
                weight TEXT,
                status TEXT,
                found TEXT,
                admitted TEXT,
                released TEXT,
                image_url TEXT,
                url TEXT
            )
        ''')

        # Copy data from the old table to the new table
        cursor.execute('''
            INSERT INTO pets (species_id, name, species, breed, age, gender, weight, status, found, admitted, released, image_url, url)
            SELECT id, name, species, breed, age, gender, weight, status, found, admitted, released, image_url, url
            FROM pets_old
        ''')

        # Drop the old table
        cursor.execute("DROP TABLE pets_old")

    conn.commit()
    conn.close()

def pet_exists(species_id, species):
    conn = sqlite3.connect("pets.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM pets WHERE species_id = ? AND species = ?", (species_id, species))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

# filepath: d:\code projects\Python projects\webscraper 2.0\database.py
def save_pet(pet_data):
    conn = sqlite3.connect("pets.db")
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO pets (species_id, name, species, breed, age, gender, weight, status, found, admitted, released, image_url, url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        pet_data['id'],  # This is now species_id
        pet_data['name'], pet_data['species'], pet_data['breed'],
        pet_data['age'], pet_data['gender'], pet_data['weight'], pet_data['status'],
        pet_data['found'], pet_data['admitted'], pet_data['released'], pet_data['image_url'], pet_data['url']
    ))

    conn.commit()
    conn.close()

def get_all_pets():
    conn = sqlite3.connect("pets.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pets")
    pets = cursor.fetchall()
    conn.close()
    return pets

def export_to_excel(file_path="pets_data.xlsx"):
    conn = sqlite3.connect("pets.db")
    query = "SELECT * FROM pets"
    df = pd.read_sql_query(query, conn)
    df.to_excel(file_path, index=False)
    conn.close()
    print(f"Data exported successfully to {file_path}")

# Initialize database on first run
init_db()