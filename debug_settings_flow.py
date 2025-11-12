"""
Debug script to test the settings API key saving flow
"""
import sys
from pathlib import Path
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.settings_service import SettingsService
from backend.models.settings import APIProviderSettings

# Create settings service
service = SettingsService()

# Get default settings before update
print("=" * 60)
print("BEFORE UPDATE")
print("=" * 60)
default_before = service.get_default_settings()
print(f"Default settings ID: {default_before.id}")
print(f"API providers: {[p.provider_name for p in default_before.api_providers]}")
print(f"OpenAI config: {[p for p in default_before.api_providers if p.provider_name == 'openai']}")

# Create provider settings
provider_settings = APIProviderSettings(
    provider_name='openai',
    api_key='sk-test-debug-12345',
    base_url='https://api.openai.com/v1',
    timeout=60,
    max_retries=3,
    rate_limit_requests=60,
    rate_limit_window=60,
    enabled=True,
    priority=1
)

print("\n" + "=" * 60)
print("UPDATING PROVIDER SETTINGS")
print("=" * 60)
print(f"Provider: {provider_settings.provider_name}")
print(f"API Key: {'*' * 10}")

# Update provider settings
success = service.update_api_provider_settings('openai', provider_settings)
print(f"Update successful: {success}")

# Get default settings after update
print("\n" + "=" * 60)
print("AFTER UPDATE")
print("=" * 60)
default_after = service.get_default_settings()
print(f"Default settings ID: {default_after.id}")
print(f"API providers: {[p.provider_name for p in default_after.api_providers]}")

for provider in default_after.api_providers:
    if provider.provider_name == 'openai':
        print(f"\nOpenAI Config:")
        print(f"  - provider_name: {provider.provider_name}")
        print(f"  - api_key: {'*' * 10 if provider.api_key else 'NONE'}")
        print(f"  - base_url: {provider.base_url}")

# Check .env file
print("\n" + "=" * 60)
print("CHECKING .env FILE")
print("=" * 60)
env_file = Path('.env')
print(f".env file path: {env_file.absolute()}")
print(f".env file exists: {env_file.exists()}")

if env_file.exists():
    with open(env_file, 'r') as f:
        content = f.read()
        print(f".env file size: {len(content)} bytes")
        
        # Show last 10 lines
        lines = content.strip().split('\n')
        print(f"\nLast 10 lines of .env:")
        for line in lines[-10:]:
            if 'API_KEY' in line.upper():
                # Mask the actual key value
                parts = line.split('=')
                print(f"  {parts[0]}=***")
            else:
                print(f"  {line}")
                
        # Check specifically for OpenAI key
        print(f"\nSearching for PROVIDER_API_KEY_OPENAI...")
        for line in lines:
            if 'PROVIDER_API_KEY_OPENAI' in line:
                print(f"  ✅ Found: {line.split('=')[0]}=***")
                break
        else:
            print(f"  ❌ Not found")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
