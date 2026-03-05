"""
Smoke tests - verify core modules can be imported.
"""

import sys
from pathlib import Path

def test_import_validate_architecture():
    """Import validate_architecture script."""
    import scripts.validate_architecture
    assert scripts.validate_architecture is not None

def test_import_architecture_validator_class():
    """Import ArchitectureValidator class."""
    from scripts.validate_architecture import ArchitectureValidator
    assert ArchitectureValidator is not None

def test_import_validation_rule_class():
    """Import ValidationRule class."""
    from scripts.validate_architecture import ValidationRule
    assert ValidationRule is not None

def test_import_validation_result_class():
    """Import ValidationResult class."""
    from scripts.validate_architecture import ValidationResult
    assert ValidationResult is not None
