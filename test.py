"""
Quick test script to verify Azure OpenAI deployment
Run this to check if your deployment exists and is accessible
"""
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_deployment():
    """Test if the Azure OpenAI deployment is accessible"""
    
    # Get configuration
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '').rstrip('/')
    api_key = os.getenv('AZURE_OPENAI_KEY', '')
    deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT', '')
    
    print("=" * 60)
    print("Testing Azure OpenAI Deployment")
    print("=" * 60)
    print(f"\nEndpoint: {endpoint}")
    print(f"Deployment: {deployment}")
    print(f"API Key: {api_key[:10]}..." if api_key else "API Key: Not set")
    print()
    
    if not endpoint or not api_key or not deployment:
        print("❌ Missing required configuration!")
        print("   Please check your .env file.")
        return
    
    # Test 1: Try the standard chat completions endpoint
    print("Test 1: Standard Chat Completions Endpoint")
    print("-" * 60)
    
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version=2024-08-01-preview"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    body = {
        "messages": [
            {"role": "user", "content": "Say 'Hello' if you can hear me"}
        ],
        "max_tokens": 10
    }
    
    try:
        print(f"URL: {url}")
        response = requests.post(url, headers=headers, json=body, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"✅ SUCCESS! Response: {message}")
            print("\n🎉 Your deployment is working correctly!")
            return True
        else:
            print(f"❌ FAILED! Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Provide specific guidance based on error
            if response.status_code == 404:
                print("\n💡 Troubleshooting:")
                print("   1. Check if deployment name 'gpt-4o' exists in Azure Portal")
                print("   2. Go to: Azure OpenAI Studio → Deployments")
                print("   3. Verify the exact deployment name (case-sensitive)")
                print("   4. Common names: gpt-4, gpt-4o, gpt-35-turbo, gpt-4-turbo")
            elif response.status_code == 401:
                print("\n💡 Troubleshooting:")
                print("   1. Verify your API key is correct")
                print("   2. Check if the key hasn't expired")
                print("   3. Regenerate key in Azure Portal if needed")
            
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        return False
    
    print()
    
    # Test 2: List available deployments (if possible)
    print("\nTest 2: Attempting to list deployments")
    print("-" * 60)
    
    # Note: This endpoint might not be available for all API versions
    list_url = f"{endpoint}/openai/deployments?api-version=2024-08-01-preview"
    
    try:
        response = requests.get(list_url, headers=headers, timeout=10)
        if response.status_code == 200:
            deployments = response.json()
            print("✅ Available deployments:")
            for dep in deployments.get('data', []):
                print(f"   - {dep.get('id', 'unknown')}")
        else:
            print(f"⚠️  Could not list deployments (Status: {response.status_code})")
            print("   This is normal - not all API versions support this endpoint")
    except Exception as e:
        print(f"⚠️  Could not list deployments: {e}")
        print("   This is normal - not all API versions support this endpoint")

if __name__ == "__main__":
    try:
        test_deployment()
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()