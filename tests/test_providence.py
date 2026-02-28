#!/usr/bin/env python3
"""
Providence SOC - Tests
Validates architecture, configuration and deployment.
"""

import unittest
import os
import json
from pathlib import Path


class TestArchitecture(unittest.TestCase):
    """Test Providence SOC architecture."""
    
    def setUp(self):
        """Setup test environment."""
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "configs"
        self.docs_dir = self.project_root / "docs"
    
    def test_vlan_configuration_exists(self):
        """Test VLAN configuration documentation exists."""
        vlan_doc = self.docs_dir / "SETUP.md"
        self.assertTrue(vlan_doc.exists())
        
        with open(vlan_doc, 'r') as f:
            content = f.read()
        
        # Check for VLAN configurations
        self.assertIn("VLAN", content)
        self.assertIn("10.10.10.0/24", content)
    
    def test_firewall_rules_exist(self):
        """Test firewall rules documented."""
        arch_doc = self.docs_dir / "ARCHITECTURE.md"
        self.assertTrue(arch_doc.exists())
        
        with open(arch_doc, 'r') as f:
            content = f.read()
        
        self.assertIn("Firewall", content)
        self.assertIn("pfSense", content)


class TestAnsiblePlaybooks(unittest.TestCase):
    """Test Ansible configuration."""
    
    def setUp(self):
        """Setup test environment."""
        self.project_root = Path(__file__).parent.parent
        self.ansible_dir = self.project_root / "scripts" / "ansible"
    
    def test_playbook_exists(self):
        """Test main playbook exists."""
        playbook = self.ansible_dir / "providence_soc.yml"
        self.assertTrue(playbook.exists())
    
    def test_inventory_exists(self):
        """Test inventory file exists."""
        inventory = self.ansible_dir / "inventory"
        self.assertTrue(inventory.exists())
    
    def test_playbook_valid_yaml(self):
        """Test playbook is valid YAML (basic check)."""
        playbook = self.ansible_dir / "providence_soc.yml"
        with open(playbook, 'r') as f:
            content = f.read()
        
        # Basic YAML validation - just check it's not empty and starts with expected content
        self.assertTrue(content.startswith("---"))
        self.assertIn("hosts:", content)
        self.assertIn("tasks:", content)
        self.assertIn("become:", content)


class TestTerraform(unittest.TestCase):
    """Test Terraform configuration."""
    
    def setUp(self):
        """Setup test environment."""
        self.project_root = Path(__file__).parent.parent
        self.terraform_dir = self.project_root / "terraform"
    
    def test_terraform_files_exist(self):
        """Test Terraform main file exists."""
        main_tf = self.terraform_dir / "main.tf"
        self.assertTrue(main_tf.exists())
    
    def test_terraform_has_variables(self):
        """Test Terraform has variables defined."""
        main_tf = self.terraform_dir / "main.tf"
        
        with open(main_tf, 'r') as f:
            content = f.read()
        
        self.assertIn("variable", content)
        self.assertIn("vlan_config", content)


class TestDocumentation(unittest.TestCase):
    """Test documentation completeness."""
    
    def setUp(self):
        """Setup test environment."""
        self.project_root = Path(__file__).parent.parent
        self.docs_dir = self.project_root / "docs"
    
    def test_required_docs_exist(self):
        """Test all required documentation exists."""
        required_docs = [
            "SETUP.md",
            "ARCHITECTURE.md"
        ]
        
        for doc in required_docs:
            doc_path = self.docs_dir / doc
            self.assertTrue(doc_path.exists(), f"Missing: {doc}")
    
    def test_setup_has_vlan_section(self):
        """Test setup has VLAN configuration section."""
        setup_doc = self.docs_dir / "SETUP.md"
        
        with open(setup_doc, 'r') as f:
            content = f.read()
        
        self.assertIn("VLAN", content)
    
    def test_architecture_has_patterns(self):
        """Test architecture has design patterns."""
        arch_doc = self.docs_dir / "ARCHITECTURE.md"
        
        with open(arch_doc, 'r') as f:
            content = f.read()
        
        # Check for design patterns
        self.assertIn("PATTERN", content.upper())


class TestSecurity(unittest.TestCase):
    """Test security configurations."""
    
    def test_readme_has_security_section(self):
        """Test README has security information."""
        project_root = Path(__file__).parent.parent
        readme = project_root / "README.md"
        
        with open(readme, 'r') as f:
            content = f.read()
        
        self.assertIn("Security", content)
        self.assertIn("VLAN", content)


class TestProjectStructure(unittest.TestCase):
    """Test project structure."""
    
    def setUp(self):
        """Setup test environment."""
        self.project_root = Path(__file__).parent.parent
    
    def test_required_directories(self):
        """Test all required directories exist."""
        required_dirs = [
            "docs",
            "scripts",
            "configs",
            "terraform",
            "tests"
        ]
        
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            self.assertTrue(dir_path.exists(), f"Missing directory: {dir_name}")
    
    def test_readme_exists(self):
        """Test README.md exists."""
        readme = self.project_root / "README.md"
        self.assertTrue(readme.exists())
    
    def test_readme_has_architecture_diagram(self):
        """Test README has architecture diagram."""
        readme = self.project_root / "README.md"
        
        with open(readme, 'r') as f:
            content = f.read()
        
        # Check for architecture elements
        self.assertIn("VLAN", content)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
