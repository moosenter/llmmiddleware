import pyodbc
print(pyodbc.drivers())

conn = pyodbc.connect(
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=localhost,1433;"
    "Database=TestDB;"
    "UID=sa;"
    "PWD=YourStrong!Passw0rd;"
    "Encrypt=no;"
    "TrustServerCertificate=yes;"
    "Connection Timeout=5;"
)
cursor = conn.cursor()
cursor.execute("SELECT @@VERSION")
print(cursor.fetchone())

# Fetch all table names
cursor.execute("SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
tables = cursor.fetchall()

# Print table list
for schema, table in tables:
    print(f"{schema}.{table}")

cursor = conn.cursor()
cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
tables = cursor.fetchall()

for table in tables:
    print(table[0])

def get_table_columns(conn, table_name):
    cursor = conn.cursor()
    cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
    return cursor.fetchall()

columns = get_table_columns(conn, "spt_fallback_db")
for name, dtype in columns:
    print(f"{name}: {dtype}")
