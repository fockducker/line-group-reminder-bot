import subprocess
import sys
import os

print("🚀 Enhanced Parser Tester Launcher")
print("="*40)

try:
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"Working directory: {script_dir}")
    print("Starting GUI application...")
    print()
    
    # Launch the GUI app
    result = subprocess.Popen([sys.executable, "simple_gui.py"])
    
    print("✅ GUI app started successfully!")
    print("👀 Look for the new window that opened")
    print()
    print("Press Ctrl+C to stop this launcher (the GUI will continue running)")
    
    # Wait for the process to complete
    try:
        result.wait()
    except KeyboardInterrupt:
        print("\n🛑 Launcher stopped (GUI app is still running)")
    
except FileNotFoundError:
    print("❌ simple_gui.py not found")
    print("Make sure you're in the correct directory")
except Exception as e:
    print(f"❌ Error launching app: {e}")

print("\nPress Enter to exit...")
input()