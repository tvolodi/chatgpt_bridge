#!/usr/bin/env python3
"""
Diagnostic script to verify the API key fix is properly installed
"""
import sys
from pathlib import Path

def check_singleton_pattern():
    """Check if singleton pattern is implemented in ai_providers.py"""
    api_file = Path("backend/api/ai_providers.py")
    if not api_file.exists():
        print("❌ backend/api/ai_providers.py not found")
        return False
    
    content = api_file.read_text()
    
    checks = [
        ("_ai_provider_service_instance" in content, "Global singleton variable defined"),
        ("if _ai_provider_service_instance is None:" in content, "Singleton check implemented"),
        ("global _ai_provider_service_instance" in content, "Global keyword used"),
    ]
    
    all_passed = True
    for check, description in checks:
        if check:
            print(f"✅ {description}")
        else:
            print(f"❌ {description}")
            all_passed = False
    
    return all_passed

def check_absolute_path():
    """Check if absolute path is implemented in ai_provider_service.py"""
    service_file = Path("backend/services/ai_provider_service.py")
    if not service_file.exists():
        print("❌ backend/services/ai_provider_service.py not found")
        return False
    
    content = service_file.read_text()
    
    checks = [
        ("self.project_root = Path(__file__).parent.parent.parent" in content, "Project root calculated"),
        ("self.env_file_path = self.project_root" in content, "Absolute env_file_path set"),
        ("str(self.env_file_path)" in content, "Using instance env_file_path for saving"),
        ("self.env_file_path.exists()" in content, "Using instance env_file_path for loading"),
    ]
    
    all_passed = True
    for check, description in checks:
        if check:
            print(f"✅ {description}")
        else:
            print(f"❌ {description}")
            all_passed = False
    
    return all_passed

def check_test_files():
    """Check if test files exist"""
    test_files = [
        "tests/test_api_key_update_fix.py",
        "tests/test_api_key_e2e.py",
    ]
    
    all_exist = True
    for test_file in test_files:
        path = Path(test_file)
        if path.exists():
            print(f"✅ {test_file} exists")
        else:
            print(f"❌ {test_file} not found")
            all_exist = False
    
    return all_exist

def check_env_file():
    """Check if .env file exists"""
    env_file = Path(".env")
    if env_file.exists():
        print(f"✅ .env file exists at {env_file.absolute()}")
        return True
    else:
        print(f"❌ .env file not found at {env_file.absolute()}")
        return False

def main():
    print("=" * 60)
    print("API Key Fix Diagnostic Report")
    print("=" * 60)
    print()
    
    print("1. Checking Singleton Pattern Implementation...")
    print("-" * 40)
    singleton_ok = check_singleton_pattern()
    print()
    
    print("2. Checking Absolute Path Implementation...")
    print("-" * 40)
    path_ok = check_absolute_path()
    print()
    
    print("3. Checking Test Files...")
    print("-" * 40)
    tests_ok = check_test_files()
    print()
    
    print("4. Checking .env File...")
    print("-" * 40)
    env_ok = check_env_file()
    print()
    
    print("=" * 60)
    if singleton_ok and path_ok and tests_ok and env_ok:
        print("✅ ALL CHECKS PASSED - Fix is properly installed!")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Please review the issues above")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
