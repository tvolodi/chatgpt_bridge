"""
Comprehensive end-to-end test of the API key settings flow

This test simulates what happens when:
1. User enters API key via Settings > Providers > Update page
2. Backend saves key to .env file
3. User refreshes the browser
4. Frontend loads the provider configs from backend
5. Backend retrieves the key from .env file
6. API key shows in the edit form
"""
import sys
from pathlib import Path
import json
import time

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.settings_service import SettingsService
from backend.models.settings import APIProviderSettings

print("=" * 80)
print("END-TO-END TEST: API KEY SETTINGS FLOW")
print("=" * 80)

# Initialize services (simulating backend startup)
service = SettingsService()

# STEP 1: Simulate user entering API key via frontend Settings page
print("\n" + "=" * 80)
print("STEP 1: USER SAVES API KEY (Settings > Providers > Update)")
print("=" * 80)

provider_settings = APIProviderSettings(
    provider_name='openai',
    api_key='sk-e2e-test-key-12345',
    base_url='https://api.openai.com/v1',
    timeout=60,
    max_retries=3,
    rate_limit_requests=60,
    rate_limit_window=60,
    enabled=True,
    priority=1
)

print(f"Frontend sends:")
print(f"  Provider: {provider_settings.provider_name}")
print(f"  API Key: {'*' * 10}")
print(f"  Base URL: {provider_settings.base_url}")

# STEP 2: Backend receives and saves
print("\n" + "=" * 80)
print("STEP 2: BACKEND RECEIVES AND SAVES API KEY")
print("=" * 80)

success = service.update_api_provider_settings('openai', provider_settings)
print(f"✅ Backend update_api_provider_settings: {'SUCCESS' if success else 'FAILED'}")

# Verify .env file was updated
env_file = Path('.env')
if env_file.exists():
    with open(env_file, 'r') as f:
        env_content = f.read()
        if 'PROVIDER_API_KEY_OPENAI' in env_content:
            print(f"✅ API key was saved to .env file")
        else:
            print(f"❌ API key was NOT found in .env file")
else:
    print(f"❌ .env file does not exist")

# STEP 3: Simulate browser refresh (clear in-memory cache, but .env persists)
print("\n" + "=" * 80)
print("STEP 3: USER REFRESHES BROWSER (Simulating new backend instance)")
print("=" * 80)

# Create a NEW instance of settings service (simulating backend restart/new request)
service2 = SettingsService()
print("✅ New SettingsService instance created (simulating browser refresh)")

# STEP 4: Frontend calls GET to load provider configs
print("\n" + "=" * 80)
print("STEP 4: FRONTEND LOADS PROVIDER CONFIGS FROM BACKEND")
print("=" * 80)

retrieved_settings = service2.get_api_provider_settings('openai')

if retrieved_settings:
    print(f"✅ Retrieved settings for 'openai' provider")
    print(f"  - provider_name: {retrieved_settings.provider_name}")
    print(f"  - api_key: {'*' * 10 if retrieved_settings.api_key else 'NONE'}")
    print(f"  - base_url: {retrieved_settings.base_url}")
    
    if retrieved_settings.api_key == 'sk-e2e-test-key-12345':
        print(f"\n✅ SUCCESS: API KEY WAS CORRECTLY RETRIEVED FROM .ENV FILE")
        print(f"   The key persists across browser refresh!")
    else:
        print(f"\n❌ ERROR: API key doesn't match")
        print(f"   Expected: sk-e2e-test-key-12345")
        print(f"   Got: {retrieved_settings.api_key}")
else:
    print(f"❌ Could not retrieve settings for 'openai'")

# STEP 5: Verify the flow is complete
print("\n" + "=" * 80)
print("STEP 5: FULL FLOW VERIFICATION")
print("=" * 80)

checks = [
    ("API key was saved to backend settings", success),
    ("API key was written to .env file", env_file.exists() and 'PROVIDER_API_KEY_OPENAI' in env_content),
    ("New backend instance loads from .env", retrieved_settings is not None),
    ("API key value matches after load", retrieved_settings and retrieved_settings.api_key == 'sk-e2e-test-key-12345'),
]

all_passed = True
for check_name, check_result in checks:
    status = "✅" if check_result else "❌"
    print(f"{status} {check_name}")
    if not check_result:
        all_passed = False

print("\n" + "=" * 80)
if all_passed:
    print("🎉 ALL TESTS PASSED - API KEY PERSISTENCE WORKING CORRECTLY!")
else:
    print("⚠️  SOME TESTS FAILED - CHECK THE LOGS ABOVE")
print("=" * 80)
