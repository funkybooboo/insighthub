"""Test configuration for deletion worker tests."""

import os
import sys

# Add the dummy shared modules to the path for all tests
dummy_shared_path = os.path.join(os.path.dirname(__file__), "dummy_shared")
if dummy_shared_path not in sys.path:
    sys.path.insert(0, dummy_shared_path)
