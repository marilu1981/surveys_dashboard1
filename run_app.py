#!/usr/bin/env python3
"""
Startup script for the Surveys Dashboard
"""
import subprocess
import sys
import os

def main():
    """Run the Streamlit application"""
    print("🚀 Starting Surveys Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print("🔄 Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        # Run streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
