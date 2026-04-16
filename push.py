# mysql_to_sqlite.py
import mysql.connector
import sqlite3
import os

# ============ CONFIGURATION ============
# Local MySQL connection (no SSH needed - you're local!)
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'newpassword123',
    'database': 'new_library'
}


SQLITE_FILE = 'data.sqlite'
TABLES_TO_MIGRATE = []  # Empty = all tables

# ========================================

def get_mysql_tables(cursor):
    """Get all table names from MySQL"""
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    cursor.fetchall()  # Consume any remaining results
    return tables

def get_table_schema(cursor, table_name):
    """Get column information for a table"""
    cursor.execute(f"DESCRIBE `{table_name}`")
    columns = cursor.fetchall()
    
    schema = []
    for col in columns:
        name = col[0]
        col_type = col[1].lower()
        
        # Map MySQL types to SQLite types
        if 'int' in col_type:
            sqlite_type = 'INTEGER'
        elif 'float' in col_type or 'double' in col_type or 'decimal' in col_type:
            sqlite_type = 'REAL'
        elif 'blob' in col_type:
            sqlite_type = 'BLOB'
        else:
            sqlite_type = 'TEXT'
        
        nullable = '' if col[2] == 'NO' else ''
        
        schema.append({
            'name': name,
            'type': sqlite_type,
            'nullable': nullable
        })
    
    return schema

def create_sqlite_table(sqlite_cursor, table_name, schema):
    """Create table in SQLite"""
    col_defs = []
    for col in schema:
        col_def = f"`{col['name']}` {col['type']}"
        if col['nullable'] == 'NO':
            col_def += " NOT NULL"
        col_defs.append(col_def)
    
    cols_str = ', '.join(col_defs)
    
    sqlite_cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
    create_query = f"CREATE TABLE `{table_name}` ({cols_str})"
    sqlite_cursor.execute(create_query)

def migrate_table(mysql_cursor, sqlite_cursor, table_name):
    """Copy all data from MySQL table to SQLite"""
    
    # Get row count first
    mysql_cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
    row_count = mysql_cursor.fetchone()[0]
    mysql_cursor.fetchall()  # Consume results
    
    if row_count == 0:
        print(f"  ⚠️ Table '{table_name}' is empty")
        return 0
    
    # Get all data
    mysql_cursor.execute(f"SELECT * FROM `{table_name}`")
    rows = mysql_cursor.fetchall()
    
    if not rows:
        return 0
    
    # Get column names from cursor description
    columns = [desc[0] for desc in mysql_cursor.description]
    
    # Prepare insert statement
    placeholders = ', '.join(['?' for _ in columns])
    cols_str = ', '.join([f'`{col}`' for col in columns])
    insert_query = f"INSERT INTO `{table_name}` ({cols_str}) VALUES ({placeholders})"
    
    # Insert rows
    sqlite_cursor.executemany(insert_query, rows)
    
    return len(rows)

def main():
    print("=" * 60)
    print("🔄 MySQL to SQLite Migration")
    print("=" * 60)
    
    # Connect to MySQL with buffered cursor
    print("📡 Connecting to MySQL...")
    try:
        mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
        mysql_cursor = mysql_conn.cursor(buffered=True)  # 🔑 KEY FIX: buffered cursor
        print("✅ Connected to MySQL")
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return
    
    # Create/connect to SQLite
    print(f"\n💾 Creating SQLite database: {SQLITE_FILE}")
    sqlite_conn = sqlite3.connect(SQLITE_FILE)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Get tables to migrate
    all_tables = get_mysql_tables(mysql_cursor)
    tables = TABLES_TO_MIGRATE if TABLES_TO_MIGRATE else all_tables
    
    print(f"\n📊 Found {len(tables)} table(s) to migrate\n")
    
    total_rows = 0
    
    for table_name in tables:
        print(f"📋 Migrating table: {table_name}", end=" ")
        
        try:
            # Get schema
            schema = get_table_schema(mysql_cursor, table_name)
            
            # Create SQLite table
            create_sqlite_table(sqlite_cursor, table_name, schema)
            
            # Copy data
            rows_copied = migrate_table(mysql_cursor, sqlite_cursor, table_name)
            total_rows += rows_copied
            
            print(f"✅ {rows_copied} rows")
            sqlite_conn.commit()
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            continue
    
    # Clean up
    mysql_cursor.close()
    mysql_conn.close()
    sqlite_conn.close()
    
    # Show file size
    file_size = os.path.getsize(SQLITE_FILE) / (1024 * 1024)  # MB
    
    print("\n" + "=" * 60)
    print(f"✨ Migration Complete!")
    print(f"📁 SQLite file: {SQLITE_FILE}")
    print(f"📊 Total rows migrated: {total_rows}")
    print(f"💾 File size: {file_size:.2f} MB")
    print("=" * 60)
    print("\n📤 Next step: Upload this file to PythonAnywhere via Files tab")

if __name__ == "__main__":
    main()