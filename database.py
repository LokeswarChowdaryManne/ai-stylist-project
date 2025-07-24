# database.py - Corrected version with robust pool handling
import mysql.connector
from mysql.connector import pooling, Error

# --- DATABASE CONFIGURATION ---
DB_CONFIG = {
    'host': 'localhost',
    'database': 'stylist_db',
    'user': 'root',
    'password': '1234' # IMPORTANT: Change this!
}

# Initialize the pool variable to None first
connection_pool = None

try:
    # Attempt to create the connection pool
    connection_pool = pooling.MySQLConnectionPool(pool_name="stylist_pool",
                                                  pool_size=5,
                                                  **DB_CONFIG)
    print("MySQL Connection Pool created successfully.")
except Error as e:
    print(f"Error while creating MySQL connection pool: {e}")
    # If pool creation fails, connection_pool remains None

def get_db_connection():
    """Gets a connection from the connection pool."""
    # Check if the pool was successfully created before trying to use it
    if connection_pool is None:
        print("Cannot get connection, the connection pool is not available.")
        return None
    
    try:
        conn = connection_pool.get_connection()
        return conn
    except Error as e:
        print(f"Error getting connection from pool: {e}")
        return None

# The rest of your functions (get_wardrobe_by_user, add_clothing_item, delete_clothing_item)
# do not need to be changed. Just make sure they are present in the file.
def get_wardrobe_by_user(user_id: int):
    conn = get_db_connection()
    if conn is None: return []
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM clothing_items WHERE user_id = %s"
    try:
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching wardrobe: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def add_clothing_item(user_id: int, item: dict):
    conn = get_db_connection()
    if conn is None: return False, "Database connection failed"
    cursor = conn.cursor()
    query = """
        INSERT INTO clothing_items 
        (user_id, ItemName, Type, Color, ColorFamily, Style, Pattern, MinTemp, MaxTemp, ConditionType) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (user_id, item['ItemName'], item['Type'], item['Color'], item['ColorFamily'], item['Style'],
              item['Pattern'], item['MinTemp'], item['MaxTemp'], item['ConditionType'])
    try:
        cursor.execute(query, values)
        conn.commit()
        return True, f"Item '{item['ItemName']}' added successfully"
    except Error as e:
        conn.rollback()
        return False, str(e)
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def delete_clothing_item(user_id: int, item_id: int):
    conn = get_db_connection()
    if conn is None: return False, "Database connection failed"
    cursor = conn.cursor()
    query = "DELETE FROM clothing_items WHERE id = %s AND user_id = %s"
    try:
        cursor.execute(query, (item_id, user_id))
        conn.commit()
        if cursor.rowcount > 0:
            return True, "Item deleted successfully"
        else:
            return False, "Item not found or user does not have permission"
    except Error as e:
        conn.rollback()
        return False, str(e)
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()