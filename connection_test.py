#!/usr/bin/env python3
"""
Connection test utility for Windows 10054 errors
"""

import requests
import time
from openai import OpenAI
import os
from dotenv import load_dotenv

def test_nvidia_connection():
    """Test NVIDIA API connection with retry logic"""
    load_dotenv()
    
    nvidia_api_key = os.getenv("nvidiaKey1")
    if not nvidia_api_key:
        print("❌ No NVIDIA API key found in .env file")
        return False
    
    print("🧪 Testing NVIDIA API connection...")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=nvidia_api_key,
                timeout=30.0,
                max_retries=0
            )
            
            print(f"   Attempt {attempt + 1}/{max_retries}...")
            
            response = client.chat.completions.create(
                model="meta/llama-3.3-70b-instruct",
                messages=[{"role": "user", "content": "Hello, this is a connection test."}],
                max_tokens=50,
                temperature=0.1
            )
            
            print("✅ NVIDIA API connection successful!")
            print(f"   Response: {response.choices[0].message.content[:100]}...")
            return True
            
        except Exception as e:
            error_str = str(e)
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            
            if "10054" in error_str or "forcibly closed" in error_str:
                print("   → This is the Windows connection error 10054")
                print("   → The server closed the connection unexpectedly")
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"   → Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    
    print("❌ All connection attempts failed")
    return False

def test_basic_internet():
    """Test basic internet connectivity"""
    print("🌐 Testing basic internet connectivity...")
    
    try:
        response = requests.get("https://httpbin.org/get", timeout=10)
        if response.status_code == 200:
            print("✅ Basic internet connection works")
            return True
        else:
            print(f"❌ HTTP request failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Internet connection test failed: {e}")
        return False

def suggest_fixes():
    """Suggest fixes for Windows 10054 errors"""
    print("\n🔧 Suggestions to fix Windows connection error 10054:")
    print("   1. Check Windows Firewall settings")
    print("   2. Temporarily disable antivirus real-time protection")
    print("   3. Try using a VPN")
    print("   4. Check proxy settings")
    print("   5. Restart your network adapter")
    print("   6. Try running as administrator")
    print("   7. Check if your ISP blocks certain connections")
    print("   8. Try using mobile hotspot temporarily")

if __name__ == "__main__":
    print("🔍 Windows Connection Diagnostic Tool")
    print("=" * 50)
    
    # Test basic internet
    internet_ok = test_basic_internet()
    
    if internet_ok:
        # Test NVIDIA API
        nvidia_ok = test_nvidia_connection()
        
        if not nvidia_ok:
            suggest_fixes()
    else:
        print("❌ Basic internet connection failed - check your network first")
    
    print("\n" + "=" * 50)
    print("✅ Diagnostic complete")