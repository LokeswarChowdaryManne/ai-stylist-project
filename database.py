# database.py
import mysql.connector
from mysql.connector import Error

# --- DATABASE CONFIGURATION ---
DB_CONFIG = {
    'host': 'localhost',
    'database': 'stylist_db',
    'user': 'root',
    'password': '1234' # IMPORTANT: Change this!
}

def get_db_connection():
    """Creates and returns a connection to the database."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def get_wardrobe_by_user(user_id: int):
    """Fetches all clothing items for a specific user from the database."""
    conn = get_db_connection()
    if conn is None:
        return []

    # The dictionary=True argument makes the cursor return rows as dictionaries
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM clothing_items WHERE user_id = %s"

    try:
        cursor.execute(query, (user_id,))
        wardrobe = cursor.fetchall()
        return wardrobe
    except Error as e:
        print(f"Error fetching wardrobe: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def add_clothing_item(user_id: int, item: dict):
    """Inserts a new clothing item for a user into the database."""
    conn = get_db_connection()
    if conn is None:
        return False, "Database connection failed"

    cursor = conn.cursor()
    query = """
        INSERT INTO clothing_items 
        (user_id, ItemName, Type, Color, ColorFamily, Style, Pattern, MinTemp, MaxTemp, ConditionType) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Prepare a tuple of values from the item dictionary in the correct order
    values = (
        user_id,
        item['ItemName'],
        item['Type'],
        item['Color'],
        item['ColorFamily'],
        item['Style'],
        item['Pattern'],
        item['MinTemp'],
        item['MaxTemp'],
        item['ConditionType']
    )

    try:
        cursor.execute(query, values)
        conn.commit()  # commit() saves the changes to the database
        return True, f"Item '{item['ItemName']}' added successfully"
    except Error as e:
        conn.rollback()  # rollback() undoes the change if an error occurs
        print(f"Error adding item: {e}")
        return False, str(e)
    finally:
        cursor.close()
        conn.close()