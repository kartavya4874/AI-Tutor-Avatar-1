"""
Setup verification script for Azure AI Avatar application
Run this after configuring your .env file to verify everything is set up correctly
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def check_env_file():
    """Check if .env file exists"""
    print_header("Checking Environment File")
    
    env_path = Path('.env')
    if env_path.exists():
        print_success(".env file found")
        load_dotenv(env_path)
        return True
    else:
        print_error(".env file not found")
        print_info("Please create .env file from .env.example")
        print_info("Run: cp .env.example .env")
        return False

def check_required_vars():
    """Check if all required environment variables are set"""
    print_header("Checking Required Environment Variables")
    
    required_vars = {
        'AZURE_SPEECH_KEY': 'Azure Speech API Key',
        'AZURE_SPEECH_REGION': 'Azure Speech Region',
        'AZURE_OPENAI_ENDPOINT': 'Azure OpenAI Endpoint',
        'AZURE_OPENAI_KEY': 'Azure OpenAI API Key',
        'AZURE_OPENAI_DEPLOYMENT': 'Azure OpenAI Deployment Name'
    }
    
    all_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value.strip():
            print_success(f"{description}: Set")
        else:
            print_error(f"{description}: Missing (set {var} in .env)")
            all_present = False
    
    return all_present

def check_optional_vars():
    """Check optional environment variables"""
    print_header("Checking Optional Environment Variables")
    
    optional_vars = {
        'ENABLE_AZURE_SEARCH': 'Azure Search Enabled',
        'AZURE_SEARCH_ENDPOINT': 'Azure Search Endpoint',
        'AZURE_SEARCH_KEY': 'Azure Search API Key',
        'AZURE_SEARCH_INDEX': 'Azure Search Index',
        'AVATAR_CHARACTER': 'Avatar Character',
        'AVATAR_STYLE': 'Avatar Style',
        'TTS_VOICE': 'TTS Voice'
    }
    
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value and value.strip():
            if var == 'ENABLE_AZURE_SEARCH':
                if value.lower() == 'true':
                    print_info(f"{description}: Enabled")
                else:
                    print_info(f"{description}: Disabled")
            else:
                print_info(f"{description}: {value}")
        else:
            print_warning(f"{description}: Not set (using default)")

def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version_str} (meets minimum requirement: 3.8+)")
        return True
    else:
        print_error(f"Python {version_str} (requires 3.8 or higher)")
        return False

def check_dependencies():
    """Check if required packages are installed"""
    print_header("Checking Python Dependencies")
    
    required_packages = {
        'streamlit': 'Streamlit',
        'azure.cognitiveservices.speech': 'Azure Speech SDK',
        'requests': 'Requests',
        'dotenv': 'Python Dotenv'
    }
    
    all_installed = True
    for package, name in required_packages.items():
        try:
            __import__(package)
            print_success(f"{name}: Installed")
        except ImportError:
            print_error(f"{name}: Not installed")
            all_installed = False
    
    if not all_installed:
        print_info("\nInstall missing packages with:")
        print_info("pip install -r requirements.txt")
    
    return all_installed

def test_azure_speech_connection():
    """Test connection to Azure Speech service"""
    print_header("Testing Azure Speech Service Connection")
    
    speech_key = os.getenv('AZURE_SPEECH_KEY')
    speech_region = os.getenv('AZURE_SPEECH_REGION')
    
    if not speech_key or not speech_region:
        print_warning("Cannot test - credentials not set")
        return False
    
    try:
        # Test getting token
        url = f"https://{speech_region}.api.cognitive.microsoft.com/sts/v1.0/issuetoken"
        headers = {
            'Ocp-Apim-Subscription-Key': speech_key
        }
        
        response = requests.post(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print_success("Azure Speech Service: Connected successfully")
            return True
        else:
            print_error(f"Azure Speech Service: Connection failed (Status: {response.status_code})")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Azure Speech Service: Connection failed ({str(e)})")
        return False

def test_azure_openai_connection():
    """Test connection to Azure OpenAI service"""
    print_header("Testing Azure OpenAI Service Connection")
    
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_key = os.getenv('AZURE_OPENAI_KEY')
    deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
    
    if not endpoint or not api_key or not deployment:
        print_warning("Cannot test - credentials not set")
        return False
    
    try:
        # Test with a simple completion request
        url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2023-06-01-preview"
        headers = {
            'api-key': api_key,
            'Content-Type': 'application/json'
        }
        data = {
            'messages': [{'role': 'user', 'content': 'test'}],
            'max_tokens': 5
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            print_success("Azure OpenAI Service: Connected successfully")
            return True
        else:
            print_error(f"Azure OpenAI Service: Connection failed (Status: {response.status_code})")
            print_info(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Azure OpenAI Service: Connection failed ({str(e)})")
        return False

def test_azure_search_connection():
    """Test connection to Azure Search service (if enabled)"""
    print_header("Testing Azure Search Service Connection")
    
    if os.getenv('ENABLE_AZURE_SEARCH', '').lower() != 'true':
        print_info("Azure Search is not enabled - skipping test")
        return True
    
    endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
    api_key = os.getenv('AZURE_SEARCH_KEY')
    index_name = os.getenv('AZURE_SEARCH_INDEX')
    
    if not endpoint or not api_key or not index_name:
        print_warning("Cannot test - credentials not set")
        return False
    
    try:
        # Test by listing indexes
        url = f"{endpoint}/indexes?api-version=2023-11-01"
        headers = {
            'api-key': api_key
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print_success("Azure Search Service: Connected successfully")
            
            # Check if the specified index exists
            indexes = response.json().get('value', [])
            index_names = [idx['name'] for idx in indexes]
            
            if index_name in index_names:
                print_success(f"Index '{index_name}': Found")
            else:
                print_warning(f"Index '{index_name}': Not found in search service")
                print_info(f"Available indexes: {', '.join(index_names)}")
            
            return True
        else:
            print_error(f"Azure Search Service: Connection failed (Status: {response.status_code})")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Azure Search Service: Connection failed ({str(e)})")
        return False

def validate_configuration():
    """Validate configuration values"""
    print_header("Validating Configuration")
    
    # Validate speech region
    valid_regions = [
        'westus', 'westus2', 'eastus', 'eastus2', 'centralus',
        'northeurope', 'westeurope', 'southeastasia', 'eastasia',
        'japaneast', 'australiaeast', 'swedencentral'
    ]
    
    speech_region = os.getenv('AZURE_SPEECH_REGION', '')
    if speech_region in valid_regions:
        print_success(f"Speech Region '{speech_region}': Valid")
    else:
        print_warning(f"Speech Region '{speech_region}': Not in common regions list")
        print_info(f"Common regions: {', '.join(valid_regions[:5])}, ...")
    
    # Validate endpoint format
    openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '')
    if openai_endpoint.startswith('https://') and '.openai.azure.com' in openai_endpoint:
        print_success("OpenAI Endpoint: Valid format")
    elif openai_endpoint:
        print_warning("OpenAI Endpoint: Unusual format (should be https://xxx.openai.azure.com)")
    
    # Validate avatar character
    valid_characters = ['lisa', 'anna', 'meg']
    avatar_character = os.getenv('AVATAR_CHARACTER', 'lisa')
    if avatar_character in valid_characters:
        print_success(f"Avatar Character '{avatar_character}': Valid")
    else:
        print_warning(f"Avatar Character '{avatar_character}': Not standard (may not work)")
        print_info(f"Valid characters: {', '.join(valid_characters)}")

def print_summary(results):
    """Print summary of verification"""
    print_header("Verification Summary")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    
    if failed == 0:
        print("\n🎉 All checks passed! You're ready to run the application.")
        print("\n🚀 Start the application with:")
        print("   python run.py")
        print("   OR")
        print("   streamlit run app.py")
    else:
        print("\n⚠️  Some checks failed. Please review the errors above.")
        print("\n💡 Common solutions:")
        print("   - Verify credentials in .env file")
        print("   - Check Azure resources are active")
        print("   - Ensure correct regions and deployments")
        print("   - Install missing dependencies: pip install -r requirements.txt")

def main():
    """Main verification function"""
    print("\n" + "🔍 Azure AI Avatar Setup Verification".center(60))
    
    results = {}
    
    # Run checks
    results['env_file'] = check_env_file()
    if not results['env_file']:
        print_summary(results)
        return
    
    results['python_version'] = check_python_version()
    results['dependencies'] = check_dependencies()
    results['required_vars'] = check_required_vars()
    
    check_optional_vars()
    validate_configuration()
    
    # Test connections (only if basic setup is correct)
    if results['required_vars']:
        results['speech_connection'] = test_azure_speech_connection()
        results['openai_connection'] = test_azure_openai_connection()
        results['search_connection'] = test_azure_search_connection()
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Verification cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()