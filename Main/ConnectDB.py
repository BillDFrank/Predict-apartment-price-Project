import os
import pyodbc
import pandas as pd
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def connect_to_database():
    """
    Establishes a connection to the Azure SQL Database using environment variables.
    Returns:
        conn (pyodbc.Connection): The database connection object.
    """
    # Retrieve credentials from environment variables
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    driver = "{ODBC Driver 18 for SQL Server}"

    if not all([server, database, username, password]):
        print("❌ Missing database credentials. Check environment variables.")
        return None

    conn_str = (
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )

    try:
        conn = pyodbc.connect(conn_str)
        print("✅ Connected to Azure SQL Database successfully!")
        return conn
    except Exception as e:
        print("❌ Failed to connect:", e)
        return None


def get_last_scraped_page_today(conn, today_str):
    """
    Retrieve the last scraped page for today's date from the advertisings table.

    Args:
        conn (pyodbc.Connection): The database connection object.
        today_str (str): Today's date as a string (e.g., "2025-02-02").

    Returns:
        int: The last scraped page number for today, or 0 if no records exist.
    """
    query = "SELECT MAX(page) FROM advertisings WHERE date_scraped = ?;"
    cursor = conn.cursor()
    cursor.execute(query, today_str)
    result = cursor.fetchone()[0]
    return result if result is not None else 0


def save_data_to_db(conn, df):
    cursor = conn.cursor()

    for _, row in df.iterrows():
        # Convert the Area field to float if possible.
        try:
            area_val = float(row['Area']) if row['Area'] else None
        except Exception as e:
            print(f"❌ Error converting area value: {row['Area']} - {e}")
            area_val = None

        # Handle NaN values in the Location column
        location_val = row['Location'] if pd.notna(row['Location']) else None

        cursor.execute("""
            INSERT INTO advertisings 
                (page, url, title, price, location, rooms, area, bathrooms, construction_year, energetic_certificate, date_scraped) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
                       row['Page'],
                       row['URL'],
                       row['Title'],
                       row['Price'],
                       location_val,
                       row['Rooms'],
                       area_val,        # Now using the converted area value
                       None,            # Bathrooms (to be filled later)
                       # Construction year (to be filled later)
                       None,
                       # Energetic certificate (to be filled later)
                       None,
                       row['ScrapeDate']
                       )
    conn.commit()
    print(f"✅ {len(df)} rows inserted successfully!")


def convert_to_int(val):
    """
    Attempts to extract the first integer from a string.
    Returns:
        int if conversion is possible; otherwise, None.
    """
    if not isinstance(val, str):
        return None
    # Try direct conversion
    try:
        return int(val)
    except:
        pass
    # Otherwise, extract digits using regex
    match = re.search(r'\d+', val)
    if match:
        return int(match.group())
    return None


def update_details_in_db(conn, record_id, bathrooms, construction_year, energetic_certificate):
    """
    Update additional detail fields for a given advertising record.

    Args:
        conn (pyodbc.Connection): The database connection object.
        record_id (int): The ID of the record to update.
        bathrooms (str): The scraped bathroom information.
        construction_year (str): The scraped construction year.
        energetic_certificate (str): The scraped energetic certificate.

    This function converts bathrooms and construction_year to integer values if possible.
    For energetic_certificate, it truncates the string to a maximum length (assumed 10 characters).
    """
    # Convert bathrooms and construction_year to integers, if possible
    b_val = convert_to_int(
        bathrooms) if bathrooms and bathrooms.upper() != "N/A" else None
    cy_val = convert_to_int(
        construction_year) if construction_year and construction_year.upper() != "N/A" else None

    # For energetic_certificate, if the value is "N/A", set to None;
    # otherwise, truncate to 10 characters (adjust max length as needed).
    ec_val = energetic_certificate if energetic_certificate and energetic_certificate.upper() != "N/A" else None
    if ec_val and len(ec_val) > 10:
        ec_val = ec_val[:10]

    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE advertisings
            SET bathrooms = ?, construction_year = ?, energetic_certificate = ?
            WHERE id = ?
        """, b_val, cy_val, ec_val, record_id)
        conn.commit()
    except Exception as e:
        print(f"❌ Error updating record {record_id}: {e}")
