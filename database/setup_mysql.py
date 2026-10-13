import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

def init_mysql():
    host = os.environ.get('MYSQL_HOST', 'localhost')
    port = int(os.environ.get('MYSQL_PORT', 3306))
    user = os.environ.get('MYSQL_USER', 'root')
    password = os.environ.get('MYSQL_PASSWORD', 'root')
    dbname = os.environ.get('MYSQL_DB', 'linux_learning_assistant')

    print(f"[*] Connecting to MySQL server at {host}:{port} as user '{user}'...")
    try:
        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            print(f"[+] Database `{dbname}` verified or created successfully!")
        conn.close()

        # Now trigger schema and seed through Flask
        from app import create_app
        from models import db
        from database.seed_data import seed_curriculum

        app = create_app()
        with app.app_context():
            db.create_all()
            seed_curriculum()
            print("[+] All tables created and curriculum seed data populated successfully in MySQL!")

    except Exception as e:
        print(f"[-] MySQL initialization error: {e}")
        print("    Ensure your MySQL service is running and credentials in .env are correct.")

if __name__ == '__main__':
    init_mysql()
