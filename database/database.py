import os
import mysql.connector

from dotenv import load_dotenv
from mysql.connector.pooling import MySQLConnectionPool

load_dotenv()

pool = MySQLConnectionPool(
    pool_name="permacore_pool",
    pool_size=10,
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    autocommit=False,
    ssl_disabled=False
)

def get_connection():
    return pool.get_connection()