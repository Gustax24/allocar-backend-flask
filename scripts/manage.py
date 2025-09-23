from app import app
from extensions.db import db

if __name__ == "__main__":
    with app.app_context():
        print("App loaded. You can run Flask CLI commands via 'flask ...'")
