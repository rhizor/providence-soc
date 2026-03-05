# Providence SOC - Repository Analysis Report

## Repository Overview

- **Name:** Providence SOC
- **Type:** Infrastructure as Code (Terraform) + Python automation
- **Description:** Mini Security Operations Center (SOC) architecture on Proxmox
- **Language:** Python (tests/automation) + HCL (Terraform)

## Repository Structure

```
providence-soc/
├── README.md           # Main documentation
├── docs/               # Setup and architecture docs
│   ├── SETUP.md
│   └── ARCHITECTURE.md
├── scripts/            # Automation scripts
│   ├── validate_architecture.py
│   └── ansible/        # Ansible playbooks
├── terraform/         # Terraform configurations
│   └── main.tf
├── tests/             # Test suite
│   └── test_providence.py
└── configs/           # Configuration files
```

## How the Application Runs

This is infrastructure code, not a running application:

```bash
# Validate architecture
python3 scripts/validate_architecture.py

# Run tests
python3 -m pytest tests/
# or
python3 -m unittest tests.test_providence

# Terraform operations
cd terraform
terraform init
terraform plan
terraform apply
```

## Dependencies

- Python 3.8+
- Terraform >= 1.0
- pytest (optional, unittest included)

## Architecture

This is a **Security Operations Center (SOC)** infrastructure project:

- **Network Segmentation:** Multiple VLANs (Victim, SIEM, Attacker, DMZ, Management)
- **Components:** Proxmox VE, pfSense, Security Onion, Wazuh
- **Automation:** Ansible, Terraform, Python validation scripts
- **Security:** VLAN segmentation, firewall rules, IDS/IPS

## Existing Tests

Yes - uses **unittest** framework:
- TestArchitecture - VLAN configuration, firewall rules
- TestAnsiblePlaybooks - Ansible validation
- TestTerraform - Terraform configuration
- TestDocumentation - Doc completeness
- TestSecurity - Security config checks
- TestProjectStructure - Directory structure

## Recommended Testing Strategy

1. **Unit tests** (existing): Validate configuration files exist and contain expected content
2. **Integration tests**: Terraform syntax validation, Ansible playbook syntax
3. **Architecture validation**: Python script validates network segmentation

## Potential Reliability Issues

- **External dependencies:** Proxmox API, Terraform providers
- **Network-specific:** Hardcoded IP ranges (10.10.x.x)
- **Credentials:** Requires API tokens for Proxmox

## Environment Variables

```
PROXMOX_API_URL=https://192.168.1.100:8006/api2/json
PROXMOX_API_TOKEN_ID=terraform@pam!terraform
PROXMOX_API_TOKEN_SECRET=uuid-guid-uuid-guid
```

## Testing Approach for Docker

The Docker container will:
1. Install Python and pytest
2. Copy project files
3. Run existing unittest-based tests
4. Validate configuration files

This ensures deterministic, reproducible validation of the SOC architecture.
