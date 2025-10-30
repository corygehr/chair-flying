#!/usr/bin/env python3
"""
Setup Verification Script for Chair Flying
This script helps users verify their installation is correct.
"""

import sys
import json
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def print_success(text):
    """Print success message."""
    print(f"✓ {text}")


def print_error(text):
    """Print error message."""
    print(f"✗ {text}")


def print_warning(text):
    """Print warning message."""
    print(f"⚠ {text}")


def check_python_version():
    """Check if Python version is adequate."""
    print_header("Checking Python Version")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"Python version: {version_str}")
    
    if version >= (3, 7):
        print_success(f"Python {version_str} is compatible (requires 3.7+)")
        return True
    else:
        print_error(f"Python {version_str} is too old. Please upgrade to 3.7 or higher.")
        return False


def check_file_exists(filepath, description):
    """Check if a required file exists."""
    path = Path(filepath)
    if path.exists():
        print_success(f"{description} found: {filepath}")
        return True
    else:
        print_error(f"{description} not found: {filepath}")
        return False


def check_config_file():
    """Check if config.json exists and is valid."""
    print_header("Checking Configuration File")
    
    if not check_file_exists("config.json", "Configuration file"):
        print("\nPlease create config.json. Example:")
        print("""
{
  "maneuvers_file": "maneuvers.json",
  "interval_min_sec": 30,
  "interval_max_sec": 120,
  "show_next_maneuver_time": true,
  "show_maneuver_type": true,
  "show_maneuver_description": true
}
        """)
        return False
    
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
        print_success("Configuration file is valid JSON")
        
        # Check required fields
        if "maneuvers_file" not in config:
            print_error("Configuration missing required field: maneuvers_file")
            return False
        
        print_success(f"Maneuvers file setting: {config['maneuvers_file']}")
        
        # Check interval settings
        if "interval_min_sec" in config or "interval_max_sec" in config:
            if "interval_min_sec" not in config or "interval_max_sec" not in config:
                print_error("Both interval_min_sec and interval_max_sec must be provided together")
                return False
            
            min_val = config["interval_min_sec"]
            max_val = config["interval_max_sec"]
            
            if min_val > max_val:
                print_error(f"interval_min_sec ({min_val}) must be <= interval_max_sec ({max_val})")
                return False
            
            print_success(f"Interval range: {min_val}-{max_val} seconds")
        else:
            print_warning("Manual mode: No automatic intervals configured")
        
        return True
        
    except json.JSONDecodeError as e:
        print_error(f"Configuration file has invalid JSON: {e}")
        print("\nPlease check your config.json for syntax errors:")
        print("  - Missing or extra commas")
        print("  - Missing quotes around strings")
        print("  - Missing closing brackets or braces")
        return False
    except Exception as e:
        print_error(f"Error reading configuration: {e}")
        return False


def check_maneuvers_file():
    """Check if maneuvers file exists and is valid."""
    print_header("Checking Maneuvers File")
    
    # First, get the maneuvers file path from config
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
        maneuvers_file = config.get("maneuvers_file", "maneuvers.json")
    except:
        maneuvers_file = "maneuvers.json"
    
    if not check_file_exists(maneuvers_file, "Maneuvers file"):
        print("\nPlease create a maneuvers file. Example:")
        print("""
[
  {
    "name": "Power-Off Stall",
    "type": "maneuver",
    "kind": "private",
    "description": "Demonstrate recognition and recovery from power-off stall"
  },
  {
    "name": "Engine Failure on Takeoff",
    "type": "emergency",
    "description": "Engine fails during takeoff roll or initial climb"
  }
]
        """)
        return False
    
    try:
        with open(maneuvers_file, 'r') as f:
            maneuvers = json.load(f)
        
        print_success("Maneuvers file is valid JSON")
        
        if not isinstance(maneuvers, list):
            print_error("Maneuvers file must contain a JSON array")
            return False
        
        if not maneuvers:
            print_error("Maneuvers file must contain at least one maneuver")
            return False
        
        print_success(f"Found {len(maneuvers)} maneuver(s)")
        
        # Count by type
        emergency_count = sum(1 for m in maneuvers if m.get("type", "").lower() == "emergency")
        private_count = sum(1 for m in maneuvers if m.get("kind", "").lower() == "private")
        commercial_count = sum(1 for m in maneuvers if m.get("kind", "").lower() == "commercial")
        
        print(f"  - Emergency maneuvers: {emergency_count}")
        print(f"  - Private pilot maneuvers: {private_count}")
        print(f"  - Commercial pilot maneuvers: {commercial_count}")
        
        # Check for required fields in each maneuver
        for i, maneuver in enumerate(maneuvers):
            if "name" not in maneuver:
                print_warning(f"Maneuver #{i+1} is missing 'name' field")
        
        return True
        
    except json.JSONDecodeError as e:
        print_error(f"Maneuvers file has invalid JSON: {e}")
        return False
    except Exception as e:
        print_error(f"Error reading maneuvers file: {e}")
        return False


def check_main_script():
    """Check if the main script exists."""
    print_header("Checking Main Script")
    return check_file_exists("chair_flying.py", "Main script")


def main():
    """Run all verification checks."""
    print_header("Chair Flying - Setup Verification")
    print("This script will verify your installation is set up correctly.")
    
    checks = [
        ("Python Version", check_python_version),
        ("Main Script", check_main_script),
        ("Configuration", check_config_file),
        ("Maneuvers", check_maneuvers_file),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Unexpected error during {name} check: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(f"{name}: OK")
        else:
            print_error(f"{name}: FAILED")
    
    print(f"\n{passed}/{total} checks passed")
    
    if passed == total:
        print_success("\nYour setup is complete! You're ready to use Chair Flying.")
        print("\nTo start the application:")
        print("  - Windows: Double-click run_chair_flying.bat")
        print("  - macOS/Linux: Run ./run_chair_flying.sh")
        print("  - Or run: python chair_flying.py (or python3 chair_flying.py)")
        return 0
    else:
        print_error("\nSome checks failed. Please fix the issues above and run this script again.")
        print("\nFor help, see:")
        print("  - QUICK_START.md for step-by-step setup instructions")
        print("  - README.md for detailed documentation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
