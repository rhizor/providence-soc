# Providence SOC - Guía de Instalación

## Tabla de Contenidos

1. [Preparación del Hardware](#1-preparación-del-hardware)
2. [Instalación de Proxmox](#2-instalación-de-proxmox)
3. [Configuración de Red](#3-configuración-de-red)
4. [Instalación de pfSense](#4-instalación-de-pfsense)
5. [Creación de VLANs](#5-creación-de-vlans)
6. [Despliegue de VMs](#6-despliegue-de-vms)
7. [Configuración de SIEM](#7-configuración-de-siem)
8. [Automatización](#8-automatización)

---

## 1. Preparación del Hardware

### Requisitos Mínimos

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 16 GB | 32-64 GB |
| Disco | 500 GB | 1 TB SSD |
| Red | 1 NIC | 2+ NICs |

### Configuración BIOS/UEFI

```bash
# Habilitar virtualización
Intel VT-x / AMD-V: Enabled
CPU Virtualization: Enabled
IOMMU: Enabled (para PCI passthrough)
```

### Diseño de Almacenamiento

```
/dev/sda (SSD 500GB)
├── LVM: pve
│   ├── swap (8GB)
│   ├── root (100GB)
│   └── data (resto)
└── EFI (1GB)
```

---

## 2. Instalación de Proxmox

### 2.1 Descargar ISO

```bash
# Descargar Proxmox VE 8.0
wget https://download.proxmox.com/iso/proxmox-ve_8.0-2.iso
```

### 2.2 Instalación Paso a Paso

1. Boot desde USB/ISO
2. Seleccionar "Install Proxmox VE"
3. Elegir disco de destino
4. Configurar timezone y keyboard
5. Establecer contraseña de root
6. Configurar red (Management)
7. Instalar

### 2.3 Post-Instalación

```bash
# Actualizar sistema
apt update && apt full-upgrade -y

# Acceso web
https://<IP>:8006
```

### 2.4 Configuración de Red Física

```bash
# Editar /etc/network/interfaces
auto lo
iface lo inet loopback

# WAN (Internet)
auto eno1
iface eno1 inet dhcp

# LAN (Switch trunk)
auto eno2
iface eno2 inet manual
```

---

## 3. Configuración de Red

### 3.1 Crear Bridge para Trunk

```bash
# En Proxmox, crear bridge para VLANs
vmbr0: bridge with VLAN filtering
├── eno1 (WAN)
└── eno2 (Trunk) - Tagged VLANs 10,20,30,40,50
```

### 3.2 Configurar VLANs en Proxmox

```bash
# Habilitar VLAN filtering
nano /etc/network/interfaces

auto lo
iface lo inet loopback

# Bridge principal con VLANs
auto vmbr0
iface vmbr0 inet static
    address 192.168.1.100
    netmask 255.255.255.0
    gateway 192.168.1.1
    bridge-ports eno2
    bridge-stp off
    bridge-fd 0
    bridge-vlan-aware yes
    bridge-vids 10 20 30 40 50
```

---

## 4. Instalación de pfSense

### 4.1 Crear VM pfSense

```bash
# En Proxmox Web UI:
# Create VM
#   Name: pfsense-01
#   OS: FreeBSD 14
#   CPU: 2 cores
#   RAM: 4GB
#   Disk: 32GB
#   Network: vmbr0 (VLAN aware)
```

### 4.2 Configuración Inicial pfSense

#### Asignar Interfaces

```
WAN -> em0 (dhcp)
LAN -> em1 (192.168.1.1/24)
OPT1 -> em2 (10.10.10.1/24)  # Victim
OPT2 -> em3 (10.10.20.1/24)  # SIEM
OPT3 -> em4 (10.10.30.1/24)  # Attacker
OPT4 -> em5 (10.10.40.1/24)  # DMZ
OPT5 -> em6 (10.10.50.1/24)  # Management
```

### 4.3 Configuración de VLANs en pfSense

```
# Web GUI: Interfaces > Assignments > VLANs

Parent Interface: em1 (LAN)
VLAN Tag: 10
VLAN Description: Victim

Parent Interface: em2
VLAN Tag: 20
VLAN Description: SIEM

... (repetir para cada VLAN)
```

### 4.4 Reglas de Firewall

#### Reglas WAN

```
# Block all by default
Action: Block
Interface: WAN
Address Family: IPv4+IPv6
```

#### Reglas LAN

```
# Allow all from LAN
Action: Pass
Interface: LAN
Source: LAN net
Destination: Any

# Allow DNS
Action: Pass
Interface: LAN
Source: LAN net
Destination: 10.10.50.5 (DNS)
Port: 53
```

#### Reglas Victim (VLAN 10)

```
# HTTP/HTTPS to DMZ
Action: Pass
Interface: VLAN10
Source: VLAN10 net
Destination: VLAN40 net
Port: 80, 443

# DNS to Management
Action: Pass
Interface: VLAN10
Source: VLAN10 net
Destination: 10.10.50.5
Port: 53

# Allow ICMP
Action: Pass
Interface: VLAN10
Protocol: ICMP

# Block direct to Internet (force proxy)
Action: Block
Interface: VLAN10
Source: VLAN10 net
Destination: !VLAN10_net
```

#### Reglas SIEM (VLAN 20)

```
# Allow all for monitoring
Action: Pass
Interface: VLAN20
Source: VLAN20 net
Destination: VLAN10 net

# Allow to Internet
Action: Pass
Interface: VLAN20
Source: VLAN20 net
Destination: Any
Port: 443
```

#### Reglas Attacker (VLAN 30)

```
# Allow to DMZ only
Action: Pass
Interface: VLAN30
Source: VLAN30 net
Destination: VLAN40 net

# DNS to Management
Action: Pass
Interface: VLAN30
Source: VLAN30 net
Destination: 10.10.50.5
Port: 53

# Log all traffic (by default block with logging)
Action: Block
Interface: VLAN30
Source: VLAN30 net
Destination: Any
Log: Yes
```

---

## 5. Creación de VLANs

### 5.1 Resumen de VLANs

| ID | Nombre | Subred | Gateway | DHCP Range |
|----|--------|--------|---------|------------|
| 10 | Victim | 10.10.10.0/24 | .1 | .100-.200 |
| 20 | SIEM | 10.10.20.0/24 | .1 | .100-.150 |
| 30 | Attacker | 10.10.30.0/24 | .1 | .100-.200 |
| 40 | DMZ | 10.10.40.0/24 | .1 | .50-.100 |
| 50 | Management | 10.10.50.0/24 | .1 | .10-.50 |

### 5.2 Configurar DHCP en pfSense

```
# Services > DHCP Server > VLAN10

Range: 10.10.10.100 - 10.10.10.200
Gateway: 10.10.10.1
DNS: 10.10.50.5
Domain: providence.local
```

---

## 6. Despliegue de VMs

### 6.1 Plantilla de VMs

#### Windows Server (DC01)

```
OS: Windows Server 2022
CPU: 2 cores
RAM: 4GB
Disk: 80GB
Network: VLAN10 (Victim)
IP: 10.10.10.10
Role: Domain Controller
```

#### Windows Client (WIN-CLIENT01)

```
OS: Windows 10/11
CPU: 2 cores
RAM: 4GB
Disk: 60GB
Network: VLAN10 (Victim)
IP: DHCP
```

#### Security Onion

```
OS: Ubuntu 20.04
CPU: 4 cores
RAM: 16GB
Disk: 500GB
Network: VLAN20 (SIEM)
IP: 10.10.20.10
```

#### Kali Linux

```
OS: Kali Linux 2024
CPU: 2 cores
RAM: 4GB
Disk: 50GB
Network: VLAN30 (Attacker)
IP: 10.10.30.100
```

#### JumpHost

```
OS: Ubuntu 22.04
CPU: 2 cores
RAM: 2GB
Disk: 40GB
Network: VLAN50 (Management)
IP: 10.10.50.10
```

### 6.2 Scripts de Despliegue

```bash
#!/bin/bash
# scripts/bash/deploy_vms.sh

# Deploy Windows VMs using qm (Proxmox)
qm create 100 \
  --name "dc01" \
  --ostype l26 \
  --cores 2 \
  --memory 4096 \
  --net0 virtio,bridge=vmbr0,tag=10 \
  --scsihw virtio-scsi-single \
  --boot order=scsi0 \
  --scsi0 local-lvm:32

# Deploy more VMs...
```

---

## 7. Configuración de SIEM

### 7.1 Security Onion

```bash
# Configurar interfaz de monitoreo
sudo so-allow

# Agregar regla para capturar tráfico
sudo so-allow -a

# Verificar estado
sudo so-status
```

### 7.2 Wazuh

```bash
# Instalar agente en Ubuntu
curl -so wazuh-agent.pkg https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.8.0-1_amd64.deb
sudo WAZUH_MANAGER='10.10.20.20' dpkg -i wazuh-agent.pkg

# Instalar agente en Windows
# Descargar desde: https://packages.wazuh.com/4.x/windows/wazuh-agent.msi
# Instalar con: msiexec /i wazuh-agent.msi /quiet WAZUH_MANAGER="10.10.20.20"
```

---

## 8. Automatización

### 8.1 Ansible

```bash
# Instalar Ansible
sudo apt install -y ansible

# Configurar inventario
cat > inventory.ini <<EOF
[windows]
10.10.10.10
10.10.10.11

[linux]
10.10.10.20
10.10.20.10

[siem]
10.10.20.10

[management]
10.10.50.10
EOF

# Ejecutar playbook
ansible-playbook -i inventory.ini scripts/ansible/monitoring.yml
```

### 8.2 Terraform

```bash
cd terraform
terraform init
terraform plan -var-file=prod.tfvars
terraform apply -var-file=prod.tfvars
```

---

## Validación Final

```bash
# Checklist post-instalación:
# [ ] Proxmox accesible
# [ ] pfSense accesible desde LAN
# [ ] Todas las VLANs configuradas
# [ ] DHCP funcionando en cada VLAN
# [ ] VMs creadas y funcionando
# [ ] Security Onion recibiendo tráfico
# [ ] Wazuh agentes conectados
# [ ] Reglas de firewall aplicadas
# [ ] Backup configurado
```
