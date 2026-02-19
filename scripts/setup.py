#!/usr/bin/env python3
"""
Setup script for AI-Augmented QA Engine
Installs dependencies and configures the environment
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f" {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f" {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f" {description} failed: {e.stderr}")
        sys.exit(1)

def setup_environment():
    """Setup the complete development environment"""
    
    print("Setting up AI-Augmented QA Engine")
    print("=" * 50)
    
    # Install Python dependencies
    run_command("python3 -m pip install --upgrade pip", "Upgrading pip")
    run_command("python3 -m pip install -r requirements.txt", "Installing Python dependencies")
    
    # Install Playwright browsers
    run_command("python3 -m playwright install", "Installing Playwright browsers")
    
    # Create necessary directories
    directories = [
        "logs",
        "reports", 
        "screenshots",
        "data/models",
        "data/historical"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Set up configuration
    print("\n  Configuration Summary:")
    print("   - AI Vision Healing: Enabled")
    print("   - Predictive Analytics: Enabled") 
    print("   - Dashboard: Streamlit")
    print("   - Test Runner: Pytest")
    
    print("\n Quick Start Commands:")
    print("   1. Run demo: python3 demo_healing.py")
    print("   2. Run tests: python3 -m pytest tests/ -v")
    print("   3. Launch dashboard: streamlit run Dashboard/app.py")
    
    print("\n Setup completed successfully!")
    print("Your AI-Augmented QA Engine is ready!")

if __name__ == "__main__":
    setup_environment()
