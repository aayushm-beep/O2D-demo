#!/usr/bin/env python3
import subprocess
import sys

def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def check_mysql():
    try:
        import pymysql  # noqa
        print("✓ PyMySQL OK")
    except ImportError:
        print("✗ PyMySQL missing")

if __name__ == "__main__":
    print("Setting up...")
    install_requirements()
    check_mysql()
    print("Done. Run: python app.py")
