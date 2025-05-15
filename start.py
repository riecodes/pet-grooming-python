import os
import subprocess
import sys

REQUIREMENTS_FILE = 'requirements.txt'
DB_SETUP_SCRIPT = 'db_config.py'
MAIN_APP = 'main.py'


def install_requirements():
    print("[INFO] Installing required Python packages...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', REQUIREMENTS_FILE])
        print("[SUCCESS] All requirements installed.")
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to install requirements. Please check your internet connection and try again.")
        sys.exit(1)

def setup_database():
    print("[INFO] Setting up the MySQL database (requires XAMPP/MySQL running)...")
    try:
        subprocess.check_call([sys.executable, DB_SETUP_SCRIPT])
        print("[SUCCESS] Database setup complete.")
    except subprocess.CalledProcessError:
        print("[ERROR] Database setup failed. Make sure MySQL is running and accessible.")
        sys.exit(1)

def run_app():
    print("[INFO] Launching the PawBuddy application...")
    try:
        subprocess.check_call([sys.executable, MAIN_APP])
    except subprocess.CalledProcessError:
        print("[ERROR] Failed to launch the application.")
        sys.exit(1)

def main():
    print("""
============================
 PawBuddy Setup & Launcher
============================

This script will:
 1. Install all required Python packages
 2. Set up the MySQL database (requires XAMPP/MySQL running)
 3. Launch the PawBuddy application

If this is your first time, make sure:
 - XAMPP is installed and MySQL is running
 - You have Python 3.7+ installed

Press ENTER to continue, or Ctrl+C to cancel.
""")
    input()
    install_requirements()
    setup_database()
    run_app()

if __name__ == "__main__":
    main() 