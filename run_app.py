#!/usr/bin/env python
"""
Quick start script to run the Sepsis Prediction Streamlit app
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("=" * 60)
    print("🏥 Sepsis Survival & Risk Prediction Platform")
    print("=" * 60)
    
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    app_file = project_root / "app" / "app.py"
    
    if not app_file.exists():
        print(f"❌ Error: app.py not found at {app_file}")
        sys.exit(1)
    
    print(f"✅ Found app at: {app_file}")
    print(f"📁 Project root: {project_root}")
    print("\n📦 Starting Streamlit app...")
    print("-" * 60)
    print("App will open in your browser at: http://localhost:8501")
    print("Press Ctrl+C to stop the server\n")
    
    # Run streamlit from the project root directory
    try:
        # Change to project root to ensure relative paths work
        os.chdir(project_root)
        subprocess.run(
            ["streamlit", "run", str(app_file)],
            cwd=str(project_root)
        )
    except KeyboardInterrupt:
        print("\n\n✋ App stopped by user")
    except Exception as e:
        print(f"❌ Error running app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
