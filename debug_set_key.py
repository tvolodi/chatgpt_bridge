"""
Debug test to identify why the API key is not being saved to .env
"""
from pathlib import Path
from dotenv import set_key, dotenv_values

# Test 1: Check if set_key works with absolute path
print("=" * 60)
print("Test 1: Testing set_key() with absolute path")
print("=" * 60)

test_env = Path("test_debug_env.txt")
if test_env.exists():
    test_env.unlink()

try:
    # Test with absolute path
    set_key(str(test_env.absolute()), "TEST_KEY", "test_value")
    print(f"✓ set_key() succeeded")
    print(f"  File created at: {test_env.absolute()}")
    
    # Read it back
    content = test_env.read_text()
    print(f"  File content: {repr(content)}")
    
    values = dotenv_values(str(test_env))
    print(f"  Parsed values: {values}")
except Exception as e:
    print(f"✗ set_key() failed: {e}")
    import traceback
    traceback.print_exc()

# Clean up
if test_env.exists():
    test_env.unlink()

# Test 2: Test with project root path
print("\n" + "=" * 60)
print("Test 2: Testing with actual project root path")
print("=" * 60)

project_root = Path(__file__).parent.parent.parent
env_file = project_root / "test_debug_env2.txt"

print(f"Project root: {project_root}")
print(f"Env file path: {env_file}")
print(f"Exists: {env_file.exists()}")

if env_file.exists():
    env_file.unlink()

try:
    set_key(str(env_file), "TEST_OPENAI_KEY", "sk-test-value-123")
    print(f"✓ set_key() succeeded")
    
    content = env_file.read_text()
    print(f"✓ File content: {repr(content)}")
    
    values = dotenv_values(str(env_file))
    print(f"✓ Parsed: {values}")
except Exception as e:
    print(f"✗ set_key() failed: {e}")
    import traceback
    traceback.print_exc()

# Clean up
if env_file.exists():
    env_file.unlink()

print("\n" + "=" * 60)
print("Test 3: Check actual .env file location")
print("=" * 60)

env_file = Path(".env")
print(f"Working directory: {Path.cwd()}")
print(f".env path: {env_file}")
print(f".env absolute: {env_file.absolute()}")
print(f".env exists: {env_file.exists()}")

if env_file.exists():
    lines = env_file.read_text().split('\n')
    print(f".env has {len(lines)} lines")
    provider_lines = [l for l in lines if 'PROVIDER_API_KEY' in l]
    print(f"PROVIDER_API_KEY entries: {len(provider_lines)}")
    if provider_lines:
        print("First 3 entries:")
        for line in provider_lines[:3]:
            print(f"  {repr(line)}")
