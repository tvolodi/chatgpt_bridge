"""
Test to verify the API provider settings update works correctly
"""
import sys
from pathlib import Path
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.models.settings import APIProviderSettings

print("=" * 80)
print("TEST: APIProviderSettings Model with Extra Fields")
print("=" * 80)

# Test 1: With extra fields (should work now with extra='ignore')
print("\nTest 1: Creating settings with extra fields (organization_id, project_id)")
try:
    settings = APIProviderSettings(
        provider_name='openai',
        api_key='sk-test-123',
        base_url='https://api.openai.com/v1',
        organization_id='org-123',  # Extra field
        project_id='proj-123'        # Extra field
    )
    print(f"✅ Success! Settings created without error")
    print(f"   provider_name: {settings.provider_name}")
    print(f"   api_key: {'*' * 10}")
    print(f"   base_url: {settings.base_url}")
except Exception as e:
    print(f"❌ Failed: {e}")

# Test 2: Without extra fields (should still work)
print("\nTest 2: Creating settings without extra fields")
try:
    settings = APIProviderSettings(
        provider_name='openai',
        api_key='sk-test-123',
        base_url='https://api.openai.com/v1'
    )
    print(f"✅ Success! Settings created")
    print(f"   provider_name: {settings.provider_name}")
    print(f"   api_key: {'*' * 10}")
except Exception as e:
    print(f"❌ Failed: {e}")

print("\n" + "=" * 80)
print("TESTS COMPLETE")
print("=" * 80)
