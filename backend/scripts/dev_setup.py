#!/usr/bin/env python3
"""
Development setup script for InkWell AI backend.

This script helps set up the development environment, create a .env file,
and run database migrations.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 50)
    print(f" {text}".center(50))
    print("=" * 50)

def run_command(command, cwd=None):
    """Run a shell command and print the output."""
    print(f"\n$ {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def create_env_file():
    """Create a .env file if it doesn't exist."""
    env_path = Path(".env")
    if env_path.exists():
        print("\n.env file already exists. Skipping creation.")
        return True
    
    print("\nCreating .env file...")
    env_content = """# Application
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./inkwell.db

# Security
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
ALGORITHM=HS256

# OpenAI
OPENAI_API_KEY=your-openai-api-key-here

# CORS (comma-separated list of origins)
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
"""
    try:
        with open(env_path, "w") as f:
            f.write(env_content)
        print("Created .env file. Please update it with your configuration.")
        return True
    except Exception as e:
        print(f"Error creating .env file: {e}")
        return False

def install_dependencies():
    """Install Python dependencies."""
    print_header("Installing Dependencies")
    return run_command("pip install -r requirements.txt")

def run_migrations():
    """Run database migrations."""
    print_header("Running Database Migrations")
    return run_command("alembic upgrade head")

def run_tests():
    """Run the test suite."""
    print_header("Running Tests")
    return run_command("pytest -v")

def start_development_server():
    """Start the development server."""
    print_header("Starting Development Server")
    print("\nStarting Uvicorn server...")
    print("The API will be available at http://localhost:8000")
    print("API documentation will be available at http://localhost:8000/docs\n")
    
    # Use os.system to keep the server running in the foreground
    os.system("uvicorn app.main:app --reload")

def main():
    """Main entry point for the setup script."""
    # Change to the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print_header("InkWell AI Backend Setup")
    
    # Create .env file if it doesn't exist
    if not create_env_file():
        print("\nFailed to create .env file. Please create it manually.")
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("\nFailed to install dependencies. Please check the error messages above.")
        return 1
    
    # Run migrations
    if not run_migrations():
        print("\nFailed to run migrations. Please check the error messages above.")
        return 1
    
    # Run tests
    if not run_tests():
        print("\nSome tests failed. Please check the test output above.")
        return 1
    
    # Start the development server
    start_development_server()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
