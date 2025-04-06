import sqlite3
import pandas as pd
from pathlib import Path


base_dir = Path(__file__).parent 
file1_path = base_dir / 'output' / 'cleaned_data_second_sheet_updated_years.xlsx'
file2_path = base_dir / 'output' / 'cleaned_final_result_waiting_list.xlsx'
db_path = base_dir / 'database' / 'local_authority_housing.db'


db_path.parent.mkdir(exist_ok=True)

def create_database():
    # Connect to SQLite database (creates a new one if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Step 1: Create the database tables based on the ERD
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Area (
        area_code TEXT PRIMARY KEY,
        area_name TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Year (
        year INTEGER PRIMARY KEY
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Affordable_Housing_Data (
        area_code TEXT,
        year INTEGER,
        housing_units INTEGER NOT NULL,
        PRIMARY KEY (area_code, year),
        FOREIGN KEY (area_code) REFERENCES Area(area_code),
        FOREIGN KEY (year) REFERENCES Year(year)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Waiting_List_Data (
        area_code TEXT,
        year INTEGER,
        households_count INTEGER NOT NULL,
        PRIMARY KEY (area_code, year),
        FOREIGN KEY (area_code) REFERENCES Area(area_code),
        FOREIGN KEY (year) REFERENCES Year(year)
    )
    ''')

    conn.commit()

    # Step 2: Load data from Excel files
    try:
        df1 = pd.read_excel(file1_path)
        df2 = pd.read_excel(file2_path)
        print(f"Data files loaded successfully:\n  - {file1_path}\n  - {file2_path}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return
    except Exception as e:
        print(f"Unexpected error while reading files: {e}")
        return

    # Step 3: Prepare and normalize the data
    # Normalize Area data
    area_data = pd.concat([
        df1[['Current\nONS code', 'Area name']].rename(columns={
            'Current\nONS code': 'area_code',
            'Area name': 'area_name'
        }),
        df2[['Current ONS Code', 'Area name']].rename(columns={
            'Current ONS Code': 'area_code',
            'Area name': 'area_name'
        })
    ]).drop_duplicates()

    # Normalize Year data
    years = pd.concat([
        pd.melt(df1, id_vars=['Current\nONS code', 'Area name'], var_name='year', value_name='housing_units')['year'],
        pd.melt(df2, id_vars=['Current ONS Code', 'Area name'], var_name='year', value_name='households_count')['year']
    ]).drop_duplicates().astype(int)

    # Prepare Affordable Housing Data
    affordable_housing_data = pd.melt(
        df1, id_vars=['Current\nONS code', 'Area name'], var_name='year', value_name='housing_units'
    ).rename(columns={
        'Current\nONS code': 'area_code',
        'Area name': 'area_name'
    }).dropna(subset=['housing_units'])

    # Prepare Waiting List Data
    waiting_list_data = pd.melt(
        df2, id_vars=['Current ONS Code', 'Area name'], var_name='year', value_name='households_count'
    ).rename(columns={
        'Current ONS Code': 'area_code',
        'Area name': 'area_name'
    }).dropna(subset=['households_count'])

    # Step 4: Insert data into the database
    try:
        # Insert Area data
        area_data.to_sql('Area', conn, if_exists='replace', index=False)

        # Insert Year data
        pd.DataFrame(years, columns=['year']).to_sql('Year', conn, if_exists='replace', index=False)

        # Insert Affordable Housing Data
        affordable_housing_data[['area_code', 'year', 'housing_units']].to_sql(
            'Affordable_Housing_Data', conn, if_exists='replace', index=False
        )

        # Insert Waiting List Data
        waiting_list_data[['area_code', 'year', 'households_count']].to_sql(
            'Waiting_List_Data', conn, if_exists='replace', index=False
        )

        print(f"Database created successfully and data inserted into: {db_path}")
    except Exception as e:
        print(f"Error while inserting data into the database: {e}")
    finally:
        # Close the connection
        conn.close()

if __name__ == "__main__":
    create_database()
