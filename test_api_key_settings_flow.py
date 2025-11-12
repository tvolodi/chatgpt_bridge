#!/usr/bin/env python3
"""
Test script to verify API key saving flow works end-to-end.
Tests that updating provider settings via Settings API saves key to .env
"""

import sys
import os
from pathlib import Path
import json
import time

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.settings_service import SettingsService
from backend.models.settings import APIProviderSettings

def test_api_key_saving_flow():
    """Test that API key is saved to .env when updating provider settings"""
    
    print("\n" + "="*70)
    print("TEST: API Key Saving Flow (Settings → .env)")
    print("="*70)
    
    # Setup
    settings_service = SettingsService()
    env_file = Path('.env')
    
    # Test data
    test_provider_name = "TEST_OPENAI_KEYSAVE"
    test_api_key = "sk-test-key-for-settings-api-12345"
    
    print(f"\n1. Updating provider settings with API key...")
    print(f"   Provider: {test_provider_name}")
    print(f"   API Key: {test_api_key[:20]}...")
    
    # Create provider settings
    provider_settings = APIProviderSettings(
        provider_name=test_provider_name,
        api_key=test_api_key,
        enabled=True
    )
    
    # Update API provider settings (this should save to .env)
    success = settings_service.update_api_provider_settings(
        provider_name=test_provider_name,
        provider_settings=provider_settings
    )
    
    if not success:
        print("❌ FAILED: update_api_provider_settings returned False")
        return False
    
    print("✅ update_api_provider_settings succeeded")
    
    # Give it a moment to write the file
    time.sleep(0.5)
    
    # Check if .env file exists
    if not env_file.exists():
        print(f"❌ FAILED: .env file not found at {env_file}")
        return False
    
    print(f"✅ .env file exists at {env_file}")
    
    # Read .env file and check for the key
    print(f"\n2. Checking .env file for the API key...")
    
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    # Look for the environment variable
    env_var_name = f"PROVIDER_API_KEY_{test_provider_name.upper().replace(' ', '_').replace('-', '_')}"
    
    if env_var_name in env_content:
        print(f"✅ Found {env_var_name} in .env file")
        
        # Extract the line
        for line in env_content.split('\n'):
            if env_var_name in line:
                print(f"   Line: {line}")
                
                # Check if the actual key is there
                if test_api_key in line:
                    print(f"✅ API key is correctly saved in .env")
                    return True
                else:
                    print(f"❌ API key value not found in line")
                    return False
    else:
        print(f"❌ {env_var_name} NOT found in .env file")
        print(f"   Expected variable name: {env_var_name}")
        print(f"   .env content snippet:")
        for line in env_content.split('\n')[-10:]:
            if line.strip():
                print(f"     {line}")
        return False

if __name__ == "__main__":
    try:
        success = test_api_key_saving_flow()
        if success:
            print("\n" + "="*70)
            print("✅ TEST PASSED: API key was saved to .env successfully")
            print("="*70 + "\n")
            sys.exit(0)
        else:
            print("\n" + "="*70)
            print("❌ TEST FAILED: API key was not saved to .env")
            print("="*70 + "\n")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
