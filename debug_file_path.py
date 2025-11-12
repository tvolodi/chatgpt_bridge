"""
Check what __file__ resolves to
"""
from pathlib import Path

# This is in backend/services/ai_provider_service.py
file_path = Path(__file__)
print(f"__file__: {__file__}")
print(f"Path(__file__): {file_path}")
print(f"Is absolute: {file_path.is_absolute()}")
print()

# Go up 3 parents
parent1 = file_path.parent
parent2 = parent1.parent
parent3 = parent2.parent

print(f"Parent 1: {parent1}")
print(f"Parent 2: {parent2}")
print(f"Parent 3: {parent3}")
print()

# Correct way
project_root = Path(__file__).resolve().parent.parent.parent
print(f"Using .resolve(): {project_root}")
print(f"Is absolute: {project_root.is_absolute()}")
