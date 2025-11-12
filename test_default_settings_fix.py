"""
Test to verify the default settings are properly returned
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.settings_service import SettingsService
from backend.models.settings import APIProviderSettings

print("=" * 80)
print("TEST: Default Settings Retrieval and API Provider Update")
print("=" * 80)

# Create a fresh settings service
service = SettingsService()

# Test 1: Get default settings
print("\nTest 1: Retrieving default settings")
try:
    default_settings = service.get_default_settings()
    if default_settings:
        print(f"✅ Successfully retrieved default settings")
        print(f"   ID: {default_settings.id}")
        print(f"   Initial API providers: {len(default_settings.api_providers)}")
    else:
        print(f"❌ default_settings is None!")
except Exception as e:
    print(f"❌ Failed to get default settings: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Update API provider settings
print("\nTest 2: Updating API provider settings (saving API key)")
try:
    provider_settings = APIProviderSettings(
        provider_name='openai',
        api_key='sk-test-key-from-fix',
        base_url='https://api.openai.com/v1',
        enabled=True,
        timeout=60,
        max_retries=3
    )
    
    success = service.update_api_provider_settings('openai', provider_settings)
    if success:
        print(f"✅ Successfully updated API provider settings")
    else:
        print(f"❌ update_api_provider_settings returned False")
except Exception as e:
    print(f"❌ Failed to update API provider settings: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Verify the API key was saved to .env
print("\nTest 3: Verifying API key was saved to .env")
try:
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'PROVIDER_API_KEY_OPENAI' in content:
                print(f"✅ API key found in .env file")
            else:
                print(f"❌ API key not found in .env file")
    else:
        print(f"❌ .env file doesn't exist")
except Exception as e:
    print(f"❌ Error checking .env: {e}")

# Test 4: Verify the settings were saved to file
print("\nTest 4: Verifying settings were persisted to file")
try:
    default_settings_after = service.get_default_settings()
    openai_configs = [p for p in default_settings_after.api_providers if p.provider_name == 'openai']
    if openai_configs:
        print(f"✅ OpenAI config found in default settings")
        print(f"   Provider name: {openai_configs[0].provider_name}")
        print(f"   Has API key: {bool(openai_configs[0].api_key)}")
    else:
        print(f"❌ OpenAI config not found in default settings")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Create a NEW service instance and verify persistence
print("\nTest 5: Testing persistence with new service instance")
try:
    service2 = SettingsService()
    default_from_new = service2.get_default_settings()
    
    if default_from_new is None:
        print(f"❌ New service instance returned None for default settings")
    else:
        openai_configs_2 = [p for p in default_from_new.api_providers if p.provider_name == 'openai']
        if openai_configs_2:
            print(f"✅ OpenAI config persisted in new service instance")
            loaded_key = service2._load_api_key_from_env('openai')
            if loaded_key == 'sk-test-key-from-fix':
                print(f"✅ API key correctly loaded from .env: {'*' * 10}")
            else:
                print(f"❌ API key mismatch: expected sk-test-key-from-fix, got {loaded_key}")
        else:
            print(f"❌ OpenAI config not in new instance")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TESTS COMPLETE")
print("=" * 80)
