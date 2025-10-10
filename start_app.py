import os
import sys
import subprocess

# Simple app launcher
if __name__ == "__main__":
    try:
        print("🤖 Enhanced Smart Parser Tester")
        print("=" * 40)
        
        # Check if we're in the right directory
        if not os.path.exists("utils/enhanced_smart_parser.py"):
            print("❌ Enhanced parser not found!")
            print("Make sure you're in the correct directory")
            input("Press Enter to exit...")
            sys.exit(1)
        
        print("✅ Found enhanced parser")
        print("🚀 Starting GUI app...")
        
        # Import and run the app directly
        from parser_tester_app import main
        main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nTrying alternative method...")
        try:
            exec(open("parser_tester_app.py").read())
        except Exception as e2:
            print(f"❌ Failed to run app: {e2}")
            input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Error: {e}")
        input("Press Enter to exit...")