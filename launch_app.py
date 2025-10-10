#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to launch the Tkinter app
"""

try:
    import subprocess
    import sys
    import os
    
    # Change to project directory
    project_dir = r"c:\Users\fermi\line-group-reminder-bot"
    os.chdir(project_dir)
    
    print("🚀 Launching Parser Tester App...")
    print(f"Working directory: {os.getcwd()}")
    
    # Run the app
    result = subprocess.run([sys.executable, "parser_tester_app.py"], 
                          capture_output=False, text=True)
    
    print(f"App exited with code: {result.returncode}")
    
except Exception as e:
    print(f"Error launching app: {e}")
    input("Press Enter to exit...")