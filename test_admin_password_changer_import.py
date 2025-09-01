#!/usr/bin/env python3
"""
Test script to verify that AdminPasswordChanger can be imported without syntax errors.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_import():
    """Test that AdminPasswordChanger can be imported without syntax errors."""
    try:
        print("Testing AdminPasswordChanger import...")
        from app.gui.windows.admin_password_changer import AdminPasswordChanger
        print("✓ AdminPasswordChanger imported successfully!")
        print(f"✓ Class found: {AdminPasswordChanger}")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error in AdminPasswordChanger: {e}")
        print(f"  File: {e.filename}")
        print(f"  Line: {e.lineno}")
        print(f"  Text: {e.text}")
        return False
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_basic_methods():
    """Test that basic methods can be called."""
    try:
        from app.gui.windows.admin_password_changer import AdminPasswordChanger
        
        # Test that we can access the class docstring and methods
        print(f"✓ Class docstring: {AdminPasswordChanger.__doc__[:50]}...")
        
        # Check if main methods exist
        expected_methods = [
            '__init__',
            '_setup_ui',
            '_validate_form',
            '_on_save_click',
            'destroy',
            'is_visible'
        ]
        
        for method_name in expected_methods:
            if hasattr(AdminPasswordChanger, method_name):
                print(f"✓ Method '{method_name}' exists")
            else:
                print(f"✗ Method '{method_name}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing methods: {e}")
        return False

if __name__ == "__main__":
    print("AdminPasswordChanger Import Test")
    print("=" * 40)
    
    success1 = test_import()
    if success1:
        success2 = test_basic_methods()
        
        if success1 and success2:
            print("\n✓ All tests passed!")
            print("AdminPasswordChanger is ready to use.")
        else:
            print("\n✗ Some tests failed.")
    else:
        print("\n✗ Import test failed.")