"""
Debug test to check what's actually in .env and how it's being loaded
"""
import json
from pathlib import Path
from dotenv import dotenv_values, set_key
import os

# Test what set_key does
test_env = Path("test_debug.env")
if test_env.exists():
    test_env.unlink()

print("=" * 60)
print("Test 1: Using set_key() to write a value")
print("=" * 60)

# Write using set_key (what python-dotenv does)
set_key(str(test_env), "TEST_KEY_1", "sk-test-value-1")

# Read the raw file
content = test_env.read_text()
print("Raw file content:")
print(repr(content))
print()

# Try to load it with dotenv_values
values = dotenv_values(str(test_env))
print("Loaded with dotenv_values():")
for key, val in values.items():
    print(f"  {key} = {repr(val)}")
print()

# Try with os.getenv after setting in the file
os.environ["TEST_KEY_1"] = values.get("TEST_KEY_1", "")
loaded = os.getenv("TEST_KEY_1")
print(f"Loaded with os.getenv(): {repr(loaded)}")
print()

# Now test with actual .env file
print("=" * 60)
print("Test 2: Check actual .env file")
print("=" * 60)

env_file = Path(".env")
if env_file.exists():
    print("Current .env file entries with PROVIDER_API_KEY:")
    lines = env_file.read_text().split('\n')
    for line in lines:
        if 'PROVIDER_API_KEY' in line:
            print(f"  Raw: {repr(line)}")
    print()
    
    values = dotenv_values(str(env_file))
    print("Parsed values from dotenv_values():")
    for key, val in values.items():
        if 'PROVIDER_API_KEY' in key:
            print(f"  {key} = {repr(val)}")

# Clean up
if test_env.exists():
    test_env.unlink()
