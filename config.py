import os

class Config:
    # MySQL Database
    MYSQL_HOST     = 'localhost'
    MYSQL_USER     = 'root'
    MYSQL_PASSWORD = 'root'          # ← உங்க MySQL password இங்க போடுங்க
    MYSQL_DB       = 'ucsp_db'
    MYSQL_PORT     = 3306

    # Flask
    SECRET_KEY = 'ucsp_secret_key_2026'
    DEBUG      = True

    # Upload
    UPLOAD_FOLDER   = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
