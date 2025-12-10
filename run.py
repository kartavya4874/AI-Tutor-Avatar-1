"""
Runner script for Azure AI Avatar Streamlit application
Handles environment setup and launches the app
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import subprocess

def setup_environment():
    """Load environment variables from .env file"""
    env_path = Path('.') / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print("✅ Environment variables loaded from .env file")
    else:
        print("⚠️  No .env file found. Using configuration from UI or defaults.")
    
def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'azure.cognitiveservices.speech',
        'requests',
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n📦 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def run_app():
    """Launch the Streamlit application"""
    print("\n🚀 Starting Azure AI Avatar application...")
    print("📱 The app will open in your default browser")
    print("🔗 Or navigate to: http://localhost:8501\n")
    
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.headless=false"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error running application: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    print("=" * 60)
    print("  Azure AI Avatar - Python/Streamlit Application")
    print("=" * 60)
    print()
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Run the app
    run_app()

if __name__ == "__main__":
    main()