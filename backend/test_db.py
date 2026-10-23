# import os
# import psycopg
# from dotenv import load_dotenv

# load_dotenv()

# database_url = os.getenv("DATABASE_URL")

# if not database_url:
#     raise RuntimeError("DATABASE_URL not found in .env")

# try:
#     conn = psycopg.connect(database_url)

#     with conn.cursor() as cursor:
#         cursor.execute("SELECT current_database(), current_user;")
#         database, user = cursor.fetchone()

#         print("✅ Database connection successful!")
#         print(f"Database: {database}")
#         print(f"User: {user}")

#     conn.close()

# except Exception as e:
#     print("❌ Database connection failed!")
#     print(e)

import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError("DATABASE_URL not found in .env")

try:
    conn = psycopg.connect(database_url)

    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT extname
            FROM pg_extension
            WHERE extname = 'vector';
        """)

        result = cursor.fetchone()

        if result:
            print("✅ PostgreSQL connection successful!")
            print("✅ pgvector extension is installed!")
        else:
            print("❌ pgvector extension not found!")

    conn.close()

except Exception as e:
    print("❌ Database test failed!")
    print(e)