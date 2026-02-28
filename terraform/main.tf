# Terraform Configuration for Providence SOC
# Provider configuration

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    proxmox = {
      source = "telmate/proxmox"
      version = "3.0.1"
    }
  }
}

provider "proxmox" {
  pm_api_url          = var.proxmox_api_url
  pm_api_token_id     = var.proxmox_api_token_id
  pm_api_token_secret = var.proxmox_api_token_secret
  pm_tls_insecure     = true
}

# ============================================================
# Variables
# ============================================================

variable "proxmox_api_url" {
  description = "Proxmox API URL"
  type        = string
  default     = "https://192.168.1.100:8006/api2/json"
}

variable "proxmox_api_token_id" {
  description = "Proxmox API Token ID"
  type        = string
  sensitive   = true
}

variable "proxmox_api_token_secret" {
  description = "Proxmox API Token Secret"
  type        = string
  sensitive   = true
}

variable "vm_password" {
  description = "Default password for VMs"
  type        = string
  sensitive   = true
}

# Network configuration
variable "network_bridge" {
  description = "Proxmox bridge for VMs"
  type        = string
  default     = "vmbr0"
}

variable "storage_pool" {
  description = "Proxmox storage pool"
  type        = string
  default     = "local-lvm"
}

# ============================================================
# VPC Network Configuration
# ============================================================

variable "vlan_config" {
  description = "VLAN configuration for networks"
  type = map(object({
    vlan_id   = number
    subnet    = string
    gateway   = string
    dhcp_start = string
    dhcp_end   = string
  }))
  
  default = {
    victim = {
      vlan_id    = 10
      subnet     = "10.10.10.0/24"
      gateway    = "10.10.10.1"
      dhcp_start = "10.10.10.100"
      dhcp_end   = "10.10.10.200"
    }
    siem = {
      vlan_id    = 20
      subnet     = "10.10.20.0/24"
      gateway    = "10.10.20.1"
      dhcp_start = "10.10.20.100"
      dhcp_end   = "10.10.20.150"
    }
    attacker = {
      vlan_id    = 30
      subnet     = "10.10.30.0/24"
      gateway    = "10.10.30.1"
      dhcp_start = "10.10.30.100"
      dhcp_end   = "10.10.30.200"
    }
    dmz = {
      vlan_id    = 40
      subnet     = "10.10.40.0/24"
      gateway    = "10.10.40.1"
      dhcp_start = "10.10.40.50"
      dhcp_end   = "10.10.40.100"
    }
    management = {
      vlan_id    = 50
      subnet     = "10.10.50.0/24"
      gateway    = "10.10.50.1"
      dhcp_start = "10.10.50.10"
      dhcp_end   = "10.10.50.50"
    }
  }
}

# ============================================================
# VM Definitions
# ============================================================

# Domain Controller - VLAN 10 (Victim)
resource "proxmox_vm_qemu" "dc01" {
  name        = "dc01"
  target_node = var.proxmox_node
  iso         = var.iso_windows_server
  
  cores   = 2
  sockets = 1
  memory  = 4096
  
  disk {
    size    = "80G"
    storage = var.storage_pool
  }
  
  network {
    bridge   = var.network_bridge
    vlan_tag = 10
  }
  
  os_type = "win"
  
  provisioner "remote-exec" {
    inline = [
      "Set-ExecutionPolicy -Scope LocalMachine -ExecutionPolicy RemoteSigned -Force",
      "Install-WindowsFeature AD-Domain-Services, DNS -IncludeManagementTools"
    ]
  }
}

# Security Onion - VLAN 20 (SIEM)
resource "proxmox_vm_qemu" "securityonion" {
  name        = "securityonion"
  target_node = var.proxmox_node
  iso         = var.iso_security_onion
  
  cores   = 4
  sockets = 1
  memory  = 16384
  
  disk {
    size    = "500G"
    storage = var.storage_pool
  }
  
  network {
    bridge   = var.network_bridge
    vlan_tag = 20
  }
  
  os_type = "l26"
  
  boot = "order=scsi0"
}

# Wazuh Manager - VLAN 20 (SIEM)
resource "proxmox_vm_qemu" "wazuh" {
  name        = "wazuh"
  target_node = var.proxmox_node
  
  cores   = 4
  sockets = 1
  memory  = 8192
  
  disk {
    size    = "200G"
    storage = var.storage_pool
  }
  
  network {
    bridge   = var.network_bridge
    vlan_tag = 20
  }
  
  os_type = "l26"
  boot    = "order=scsi0"
  
  provisioner "ansible" {
    plays = [
      file("${path.module}/../ansible/providence_soc.yml")
    ]
  }
}

# Kali Linux - VLAN 30 (Attacker)
resource "proxmox_vm_qemu" "kali" {
  name        = "kali"
  target_node = var.proxmox_node
  
  cores   = 2
  sockets = 1
  memory  = 4096
  
  disk {
    size    = "50G"
    storage = var.storage_pool
  }
  
  network {
    bridge   = var.network_bridge
    vlan_tag = 30
  }
  
  os_type = "l26"
  boot    = "order=scsi0"
}

# JumpHost - VLAN 50 (Management)
resource "proxmox_vm_qemu" "jumphost" {
  name        = "jumphost"
  target_node = var.proxmox_node
  
  cores   = 2
  sockets = 1
  memory  = 2048
  
  disk {
    size    = "40G"
    storage = var.storage_pool
  }
  
  network {
    bridge   = var.network_bridge
    vlan_tag = 50
  }
  
  os_type = "l26"
  boot    = "order=scsi0"
}

# Nginx Proxy - VLAN 40 (DMZ)
resource "proxmox_vm_qemu" "nginx" {
  name        = "nginx-proxy"
  target_node = var.proxmox_node
  
  cores   = 1
  sockets = 1
  memory  = 1024
  
  disk {
    size    = "20G"
    storage = var.storage_pool
  }
  
  network {
    bridge   = var.network_bridge
    vlan_tag = 40
  }
  
  os_type = "l26"
  boot    = "order=scsi0"
}

# ============================================================
# Outputs
# ============================================================

output "vm_ip_addresses" {
  description = "IP addresses of deployed VMs"
  value = {
    dc01           = proxmox_vm_qemu.dc01.ipv4_address
    securityonion = proxmox_vm_qemu.securityonion.ipv4_address
    wazuh          = proxmox_vm_qemu.wazuh.ipv4_address
    kali           = proxmox_vm_qemu.kali.ipv4_address
    jumphost       = proxmox_vm_qemu.jumphost.ipv4_address
    nginx          = proxmox_vm_qemu.nginx.ipv4_address
  }
}

output "network_configuration" {
  description = "Network configuration summary"
  value       = var.vlan_config
}
