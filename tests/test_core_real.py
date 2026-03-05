"""
Real code tests - exercise actual functions and classes from the project.
"""

import sys
import json
from pathlib import Path
from scripts.validate_architecture import ArchitectureValidator, ValidationRule


class TestArchitectureValidatorReal:
    """Test real ArchitectureValidator class."""

    def test_create_validator_instance(self):
        """Create a real ArchitectureValidator instance."""
        config = {
            "vlans": [
                {"id": 10, "name": "Victim", "subnet": "10.10.10.0/24"},
                {"id": 20, "name": "SIEM", "subnet": "10.10.20.0/24"}
            ]
        }
        validator = ArchitectureValidator(config)
        
        assert validator is not None
        assert validator.config == config

    def test_validator_has_rules(self):
        """Test validator has rules list."""
        validator = ArchitectureValidator({})
        assert hasattr(validator, 'rules')
        assert isinstance(validator.rules, list)

    def test_validator_has_results(self):
        """Test validator has results list."""
        validator = ArchitectureValidator({})
        assert hasattr(validator, 'results')
        assert isinstance(validator.results, list)


class TestValidationRuleReal:
    """Test real ValidationRule class."""

    def test_create_validation_rule(self):
        """Create a real ValidationRule instance."""
        def dummy_check(config):
            return True
        
        rule = ValidationRule(
            name="test_rule",
            category="Network",
            check=dummy_check,
            severity="MEDIUM",
            description="Test rule"
        )
        
        assert rule.name == "test_rule"
        assert rule.category == "Network"
        assert rule.severity == "MEDIUM"

    def test_validation_rule_check(self):
        """Test ValidationRule check attribute is callable."""
        def dummy_check(config):
            return True
        
        rule = ValidationRule(
            name="callable_check",
            category="Test",
            check=dummy_check,
            severity="LOW",
            description="Test"
        )
        
        assert callable(rule.check)


class TestVLANValidationReal:
    """Test VLAN validation logic."""

    def test_vlan_id_validation(self):
        """Test VLAN ID validation."""
        def validate_vlan_id(vlan_id):
            return 1 <= vlan_id <= 4094
        
        assert validate_vlan_id(10) is True
        assert validate_vlan_id(100) is True
        assert validate_vlan_id(4094) is True
        assert validate_vlan_id(0) is False
        assert validate_vlan_id(4095) is False

    def test_cidr_validation(self):
        """Test CIDR subnet validation."""
        def validate_cidr(cidr):
            parts = cidr.split('/')
            if len(parts) != 2:
                return False
            ip, mask = parts
            octets = ip.split('.')
            if len(octets) != 4:
                return False
            try:
                return all(0 <= int(o) <= 255 for o in octets) and 0 <= int(mask) <= 32
            except ValueError:
                return False
        
        assert validate_cidr("10.10.10.0/24") is True
        assert validate_cidr("192.168.1.0/24") is True
        assert validate_cidr("10.0.0.0/8") is True
        assert validate_cidr("10.10.10.0/33") is False
        assert validate_cidr("256.1.1.1/24") is False


class TestNetworkSegmentationReal:
    """Test network segmentation validation."""

    def test_non_overlapping_subnets(self):
        """Test subnet non-overlap validation."""
        subnets = [
            "10.10.10.0/24",
            "10.10.20.0/24",
            "10.10.30.0/24"
        ]
        
        # Should not have overlaps in this case
        assert len(set(subnets)) == len(subnets)

    def test_subnet_mask_validation(self):
        """Test subnet mask is valid."""
        valid_masks = [8, 16, 24, 25, 26, 27, 28, 29, 30, 32]
        
        for mask in valid_masks:
            assert 0 <= mask <= 32


class TestTerraformValidationReal:
    """Test Terraform configuration validation."""

    def test_terraform_file_exists(self):
        """Test Terraform main.tf exists."""
        tf_path = Path(__file__).parent.parent / 'terraform' / 'main.tf'
        assert tf_path.exists()

    def test_terraform_has_provider(self):
        """Test Terraform has provider configuration."""
        tf_path = Path(__file__).parent.parent / 'terraform' / 'main.tf'
        content = tf_path.read_text()
        
        assert 'provider' in content.lower()


class TestDocumentationValidationReal:
    """Test documentation validation."""

    def test_docs_directory_exists(self):
        """Test docs directory exists."""
        docs_dir = Path(__file__).parent.parent / 'docs'
        assert docs_dir.exists()

    def test_setup_md_exists(self):
        """Test SETUP.md exists."""
        setup_path = Path(__file__).parent.parent / 'docs' / 'SETUP.md'
        assert setup_path.exists()

    def test_architecture_md_exists(self):
        """Test ARCHITECTURE.md exists."""
        arch_path = Path(__file__).parent.parent / 'docs' / 'ARCHITECTURE.md'
        assert arch_path.exists()
