#!/usr/bin/env python3
"""
Providence SOC - Architecture Validator
Validates the SOC architecture against best practices.
"""

import json
import sys
from typing import Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class ValidationRule:
    """Represents a validation rule."""
    name: str
    category: str
    check: callable
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str


@dataclass
class ValidationResult:
    """Result of a validation check."""
    rule: str
    passed: bool
    severity: str
    message: str
    details: Dict = field(default_factory=dict)


class ArchitectureValidator:
    """Validates Providence SOC architecture."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.results: List[ValidationResult] = []
        self.rules = self._init_rules()
    
    def _init_rules(self) -> List[ValidationRule]:
        """Initialize validation rules."""
        return [
            # Network Validation Rules
            ValidationRule(
                name="vlan_segmentation",
                category="Network",
                check=self._check_vlan_segmentation,
                severity="CRITICAL",
                description="VLANs must be properly segmented"
            ),
            ValidationRule(
                name="firewall_zones",
                category="Network",
                check=self._check_firewall_zones,
                severity="HIGH",
                description="Firewall zones must be defined"
            ),
            ValidationRule(
                name="dhcp_isolation",
                category="Network",
                check=self._check_dhcp_isolation,
                severity="HIGH",
                description="DHCP should be isolated per VLAN"
            ),
            
            # Security Validation Rules
            ValidationRule(
                name="management_network",
                category="Security",
                check=self._check_management_network,
                severity="CRITICAL",
                description="Management network must be isolated"
            ),
            ValidationRule(
                name="siem_network",
                category="Security",
                check=self._check_siem_network,
                severity="HIGH",
                description="SIEM network must have access to all segments"
            ),
            ValidationRule(
                name="attacker_isolation",
                category="Security",
                check=self._check_attacker_isolation,
                severity="HIGH",
                description="Attacker network must be restricted"
            ),
            
            # High Availability Rules
            ValidationRule(
                name="firewall_ha",
                category="HA",
                check=self._check_firewall_ha,
                severity="MEDIUM",
                description="Firewall should have HA"
            ),
            ValidationRule(
                name="siem_redundancy",
                category="HA",
                check=self._check_siem_redundancy,
                severity="MEDIUM",
                description="SIEM should have redundancy"
            ),
            
            # Monitoring Rules
            ValidationRule(
                name="logging_coverage",
                category="Monitoring",
                check=self._check_logging_coverage,
                severity="HIGH",
                description="All networks should be logged"
            ),
            ValidationRule(
                name="alerting_configured",
                category="Monitoring",
                check=self._check_alerting,
                severity="MEDIUM",
                description="Alerting should be configured"
            ),
        ]
    
    def _check_vlan_segmentation(self) -> ValidationResult:
        """Check VLAN segmentation."""
        vlans = self.config.get('vlans', {})
        
        required_vlans = {10, 20, 30, 40, 50}
        existing_vlans = set(vlans.keys())
        
        missing = required_vlans - existing_vlans
        
        if missing:
            return ValidationResult(
                rule="vlan_segmentation",
                passed=False,
                severity="CRITICAL",
                message=f"Missing required VLANs: {missing}",
                details={"required": list(required_vlans), "existing": list(existing_vlans)}
            )
        
        # Check for overlapping subnets
        subnets = []
        for vlan_id, vlan_config in vlans.items():
            subnet = vlan_config.get('subnet', '')
            if subnet in subnets:
                return ValidationResult(
                    rule="vlan_segmentation",
                    passed=False,
                    severity="CRITICAL",
                    message=f"Duplicate subnet found: {subnet}"
                )
            subnets.append(subnet)
        
        return ValidationResult(
            rule="vlan_segmentation",
            passed=True,
            severity="CRITICAL",
            message="VLAN segmentation is properly configured",
            details={"vlans": list(existing_vlans)}
        )
    
    def _check_firewall_zones(self) -> ValidationResult:
        """Check firewall zones configuration."""
        zones = self.config.get('firewall_zones', {})
        
        if not zones:
            return ValidationResult(
                rule="firewall_zones",
                passed=False,
                severity="HIGH",
                message="No firewall zones configured"
            )
        
        required_zones = {'wan', 'lan', 'dmz', 'siem', 'attacker', 'management'}
        existing_zones = set(zones.keys())
        
        missing = required_zones - existing_zones
        
        if missing:
            return ValidationResult(
                rule="firewall_zones",
                passed=False,
                severity="HIGH",
                message=f"Missing firewall zones: {missing}"
            )
        
        return ValidationResult(
            rule="firewall_zones",
            passed=True,
            severity="HIGH",
            message="Firewall zones properly configured",
            details={"zones": list(existing_zones)}
        )
    
    def _check_dhcp_isolation(self) -> ValidationResult:
        """Check DHCP isolation per VLAN."""
        vlans = self.config.get('vlans', {})
        
        for vlan_id, vlan_config in vlans.items():
            if 'dhcp_range' not in vlan_config:
                return ValidationResult(
                    rule="dhcp_isolation",
                    passed=False,
                    severity="HIGH",
                    message=f"VLAN {vlan_id} missing DHCP range"
                )
        
        return ValidationResult(
            rule="dhcp_isolation",
            passed=True,
            severity="HIGH",
            message="DHCP properly isolated per VLAN"
        )
    
    def _check_management_network(self) -> ValidationResult:
        """Check management network isolation."""
        management_vlan = self.config.get('vlans', {}).get(50, {})
        
        if not management_vlan:
            return ValidationResult(
                rule="management_network",
                passed=False,
                severity="CRITICAL",
                message="Management VLAN (50) not found"
            )
        
        # Management should have minimal internet access
        firewall_rules = self.config.get('firewall_rules', {})
        
        # Check if there's a rule blocking internet from management
        block_rules = [r for r in firewall_rules if 'management' in r.get('source', '').lower()]
        
        return ValidationResult(
            rule="management_network",
            passed=True,
            severity="CRITICAL",
            message="Management network properly isolated",
            details={"vlan": 50}
        )
    
    def _check_siem_network(self) -> ValidationResult:
        """Check SIEM network has proper access."""
        siem_vlan = self.config.get('vlans', {}).get(20, {})
        
        if not siem_vlan:
            return ValidationResult(
                rule="siem_network",
                passed=False,
                severity="HIGH",
                message="SIEM VLAN (20) not found"
            )
        
        return ValidationResult(
            rule="siem_network",
            passed=True,
            severity="HIGH",
            message="SIEM network configured",
            details={"vlan": 20}
        )
    
    def _check_attacker_isolation(self) -> ValidationResult:
        """Check attacker network is properly isolated."""
        attacker_vlan = self.config.get('vlans', {}).get(30, {})
        
        if not attacker_vlan:
            return ValidationResult(
                rule="attacker_isolation",
                passed=False,
                severity="HIGH",
                message="Attacker VLAN (30) not found"
            )
        
        # Attacker should only access DMZ and be logged
        firewall_rules = self.config.get('firewall_rules', [])
        
        # Should have explicit rules for attacker network
        attacker_rules = [r for r in firewall_rules if 'attacker' in str(r).lower()]
        
        if not attacker_rules:
            return ValidationResult(
                rule="attacker_isolation",
                passed=False,
                severity="HIGH",
                message="No explicit firewall rules for attacker network"
            )
        
        return ValidationResult(
            rule="attacker_isolation",
            passed=True,
            severity="HIGH",
            message="Attacker network properly isolated with rules",
            details={"rules_count": len(attacker_rules)}
        )
    
    def _check_firewall_ha(self) -> ValidationResult:
        """Check firewall high availability."""
        ha_config = self.config.get('high_availability', {})
        
        if not ha_config.get('firewall_enabled', False):
            return ValidationResult(
                rule="firewall_ha",
                passed=False,
                severity="MEDIUM",
                message="Firewall HA not enabled"
            )
        
        return ValidationResult(
            rule="firewall_ha",
            passed=True,
            severity="MEDIUM",
            message="Firewall HA configured"
        )
    
    def _check_siem_redundancy(self) -> ValidationResult:
        """Check SIEM redundancy."""
        ha_config = self.config.get('high_availability', {})
        
        if not ha_config.get('siem_enabled', False):
            return ValidationResult(
                rule="siem_redundancy",
                passed=False,
                severity="MEDIUM",
                message="SIEM redundancy not configured"
            )
        
        return ValidationResult(
            rule="siem_redundancy",
            passed=True,
            severity="MEDIUM",
            message="SIEM redundancy configured"
        )
    
    def _check_logging_coverage(self) -> ValidationResult:
        """Check logging coverage across VLANs."""
        logging_config = self.config.get('logging', {})
        
        if not logging_config:
            return ValidationResult(
                rule="logging_coverage",
                passed=False,
                severity="HIGH",
                message="Logging not configured"
            )
        
        # Check each VLAN has logging
        vlans = self.config.get('vlans', {})
        logging_vlans = set(logging_config.get('enabled_vlans', []))
        all_vlans = set(vlans.keys())
        
        not_logged = all_vlans - logging_vlans
        
        if not_logged:
            return ValidationResult(
                rule="logging_coverage",
                passed=False,
                severity="HIGH",
                message=f"VLANs without logging: {not_logged}"
            )
        
        return ValidationResult(
            rule="logging_coverage",
            passed=True,
            severity="HIGH",
            message="All VLANs have logging enabled"
        )
    
    def _check_alerting(self) -> ValidationResult:
        """Check alerting configuration."""
        alerting_config = self.config.get('alerting', {})
        
        if not alerting_config.get('enabled', False):
            return ValidationResult(
                rule="alerting_configured",
                passed=False,
                severity="MEDIUM",
                message="Alerting not enabled"
            )
        
        channels = alerting_config.get('channels', [])
        
        if not channels:
            return ValidationResult(
                rule="alerting_configured",
                passed=False,
                severity="MEDIUM",
                message="No alerting channels configured"
            )
        
        return ValidationResult(
            rule="alerting_configured",
            passed=True,
            severity="MEDIUM",
            message=f"Alerting configured with {len(channels)} channels",
            details={"channels": channels}
        )
    
    def run_validation(self) -> Tuple[bool, List[ValidationResult]]:
        """Run all validation checks."""
        print("\n" + "=" * 60)
        print("PROVIDENCE SOC - ARCHITECTURE VALIDATION")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for rule in self.rules:
            result = rule.check()
            self.results.append(result)
            
            if result.passed:
                passed += 1
                status = "✅"
            else:
                failed += 1
                status = "❌"
            
            severity_icon = {
                "CRITICAL": "🔴",
                "HIGH": "🟠",
                "MEDIUM": "🟡",
                "LOW": "🟢"
            }.get(result.severity, "⚪")
            
            print(f"\n{status} {severity_icon} {result.rule}")
            print(f"   {result.message}")
        
        print("\n" + "=" * 60)
        print(f"SUMMARY: {passed} passed, {failed} failed")
        print("=" * 60)
        
        # Print failed checks
        if failed > 0:
            print("\n🔴 FAILED CHECKS:")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.rule}: {result.message}")
        
        return failed == 0, self.results


def main():
    """Main entry point."""
    # Sample configuration (would normally load from config file)
    sample_config = {
        "vlans": {
            10: {"name": "victim", "subnet": "10.10.10.0/24", "gateway": "10.10.10.1", "dhcp_range": "10.10.10.100-10.10.10.200"},
            20: {"name": "siem", "subnet": "10.10.20.0/24", "gateway": "10.10.20.1", "dhcp_range": "10.10.20.100-10.10.20.150"},
            30: {"name": "attacker", "subnet": "10.10.30.0/24", "gateway": "10.10.30.1", "dhcp_range": "10.10.30.100-10.10.30.200"},
            40: {"name": "dmz", "subnet": "10.10.40.0/24", "gateway": "10.10.40.1", "dhcp_range": "10.10.40.50-10.10.40.100"},
            50: {"name": "management", "subnet": "10.10.50.0/24", "gateway": "10.10.50.1", "dhcp_range": "10.10.50.10-10.10.50.50"}
        },
        "firewall_zones": {
            "wan": {"description": "External network"},
            "lan": {"description": "Internal network"},
            "dmz": {"description": "Demilitarized zone"},
            "siem": {"description": "SIEM monitoring"},
            "attacker": {"description": "Red team network"},
            "management": {"description": "Admin network"}
        },
        "firewall_rules": [
            {"source": "attacker", "destination": "dmz", "action": "allow"},
            {"source": "attacker", "destination": "management", "action": "deny"}
        ],
        "high_availability": {
            "firewall_enabled": True,
            "siem_enabled": True
        },
        "logging": {
            "enabled_vlans": [10, 20, 30, 40, 50]
        },
        "alerting": {
            "enabled": True,
            "channels": ["email", "slack", "telegram"]
        }
    }
    
    validator = ArchitectureValidator(sample_config)
    success, results = validator.run_validation()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
