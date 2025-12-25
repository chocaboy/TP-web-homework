"""
Database configuration file
"""
import os

DB_NAME = os.environ.get('DB_NAME', 'questions_db')
DB_USER = os.environ.get('DB_USER', 'vladimirzdobnov')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')

