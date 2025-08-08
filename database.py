import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import pooling, Error

# Load environment variables from .env file
load_dotenv()

DB_CONFIG = {
    'host': 'localhost',
    'database': 'stylist_db',
    'user': 'root',
    # Read the password from the environment variables
    'password': os.getenv("DB_PASSWORD")
}

# (The rest of the database.py file remains exactly the same)
connection_pool = None
try:
    connection_pool = pooling.MySQLConnectionPool(pool_name="stylist_pool", pool_size=5, **DB_CONFIG)
    print("MySQL Connection Pool created successfully.")
except Error as e:
    print(f"Error while creating MySQL connection pool: {e}")

def get_db_connection():
    if connection_pool is None: return None
    try: return connection_pool.get_connection()
    except Error as e: print(f"Error getting connection from pool: {e}"); return None

def get_wardrobe_by_user(user_id: int):
    """Fetches a user's wardrobe by joining the user_wardrobe and base_items tables."""
    conn = get_db_connection()
    if conn is None: return []
    cursor = conn.cursor(dictionary=True)
    # SQL JOIN to combine information from both tables
    query = """
        SELECT b.* FROM base_items b
        JOIN user_wardrobe w ON b.id = w.item_id
        WHERE w.user_id = %s
    """
    try:
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching wardrobe: {e}"); return []
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def add_clothing_item(user_id: int, item: dict, image_path: str):
    """
    First, adds the item to the master catalog if it's new.
    Then, links the item to the user.
    """
    conn = get_db_connection()
    if conn is None: return False, "Database connection failed"
    cursor = conn.cursor()
    try:
        # Check if this item (based on image path) already exists in the master catalog
        cursor.execute("SELECT id FROM base_items WHERE ImagePath = %s", (image_path,))
        result = cursor.fetchone()

        if result:
            item_id = result[0]
        else:
            # If not, insert it into the master catalog
            query_insert_base = """
                INSERT INTO base_items (ItemName, Type, Color, ColorFamily, Style, Pattern, MinTemp, MaxTemp, ConditionType, ImagePath)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values_base = (item['ItemName'], item['Type'], item['Color'], item['ColorFamily'], item['Style'],
                           item['Pattern'], item['MinTemp'], item['MaxTemp'], item['ConditionType'], image_path)
            cursor.execute(query_insert_base, values_base)
            item_id = cursor.lastrowid # Get the ID of the new item

        # Link the base item to the user
        cursor.execute("INSERT INTO user_wardrobe (user_id, item_id) VALUES (%s, %s)", (user_id, item_id))
        conn.commit()
        return True, f"Item '{item['ItemName']}' added to wardrobe."
    except Error as e:
        conn.rollback(); return False, str(e)
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def delete_clothing_item(user_id: int, item_id: int):
    """Deletes an item from a user's wardrobe (removes the link)."""
    conn = get_db_connection()
    if conn is None: return False, "Database connection failed"
    cursor = conn.cursor()
    # We only delete the link in user_wardrobe, not the item from the master catalog
    query = "DELETE FROM user_wardrobe WHERE item_id = %s AND user_id = %s"
    try:
        cursor.execute(query, (item_id, user_id))
        conn.commit()
        if cursor.rowcount > 0: return True, "Item removed from wardrobe"
        else: return False, "Item not found in user's wardrobe"
    except Error as e:
        conn.rollback(); return False, str(e)
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()