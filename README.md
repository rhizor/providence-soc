# Providence SOC 🏛️🔍

<p align="center">
  <img src="https://img.shields.io/badge/Proxmox-VE-8.0+-orange.svg" alt="Proxmox">
  <img src="https://img.shields.io/badge/pfSense-2.7+-blue.svg" alt="pfSense">
  <img src="https://img.shields.io/badge/Security%20Onion-2.6+-red.svg" alt="Security Onion">
  <img src="https://img.shields.io/badge/Wazuh-4.8+-green.svg" alt="Wazuh">
  <img src="https://img.shields.io/badge/Docker-24+-blue.svg" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

> *"The most merciful thing in the world, I think, is the inability of the human mind to correlate all its contents."* — H.P. Lovecraft, The Call of Cthulhu

**Providence SOC** es un proyecto de arquitectura de seguridad empresarial que implementa un mini-Centro de Operaciones de Seguridad (SOC) en un entorno virtualizado. Este proyecto demuestra habilidades avanzadas en diseño de infraestructura, segmentación de red, y gestión de seguridad.

## 📐 Arquitectura General

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                        INTERNET                                                 │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    WAN (Uplink)                                                  │
│                                    pfSense Firewall                                             │
│                              ┌────────────────────────────────┐                                   │
│                              │  📋 Interfaces:               │                                   │
│                              │  • WAN: Bridge to ISP         │                                   │
│                              │  • LAN: 192.168.1.0/24       │                                   │
│                              │  • OPT1: 10.10.10.0/24       │  (Victim Network)               │
│                              │  • OPT2: 10.0/24      10.20. │  (SIEM Network)                │
│                              │  • OPT3: 10.10.30.0/24       │  (Attacker Network)            │
│                              │  • OPT4: 10.10.40.0/24       │  (DMZ)                         │
│                              │  • OPT5: 10.10.50.0/24       │  (Management)                  │
│                              └────────────────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
         │                    │                    │                    │                    │
         ▼                    ▼                    ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   VLAN 10       │  │   VLAN 20       │  │   VLAN 30       │  │   VLAN 40       │  │   VLAN 50       │
│  Victim Network │  │  SIEM Network   │  │ Attacker Network│  │      DMZ        │  │  Management     │
│  10.10.10.0/24  │  │  10.10.20.0/24 │  │  10.10.30.0/24  │  │  10.10.40.0/24  │  │  10.10.50.0/24  │
├─────────────────┤  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤
│  • DC01         │  │  • SecurityOnion│  │  • Kali Linux   │  │  • nginx        │  │  • JumpHost     │
│  • WIN-SRV01   │  │  • Wazuh        │  │  • DVWA         │  │  • HAProxy      │  │  • Ansible      │
│  • WIN-CLIENT01│  │  • Elasticsearch │  │  • Metasploitable│ │  • Web App     │  │  • DNS Server   │
│  • UBUNTU-01   │  │  • Kibana       │  │  • C2 Server    │  │  • Reverse Proxy│ │  • NTP Server   │
│  • DVWA        │  │  • Grafana      │  │                 │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

## 🎯 Objetivos de Aprendizaje

Este proyecto demuestra las siguientes competencias:

1. **Virtualización de Nivel Enterprise** - Proxmox VE
2. **Gestión de Firewalls** - pfSense
3. **Segmentación de Red** - VLANs
4. **Detección de Intrusiones** - NIDS/SIEM
5. **Gestión de Eventos** - Log Management
6. **Automatización** - Ansible
7. **Infraestructura como Código** - Terraform
8. **Diseño de Alta Disponibilidad** - HA

## 📋 Requisitos

### Hardware Recomendado
- **CPU**: 8+ cores (AMD-V/Intel VT-x)
- **RAM**: 32 GB minimum, 64 GB recomendado
- **Disco**: 1 TB SSD
- **Red**: 2+ interfaces de red físicas

### Software Requerido
- Proxmox VE 8.0+
- pfSense 2.7+
- Security Onion 2.6+
- Wazuh 4.8+
- Docker 24+

## 🚀 quick Start

### 1. Clonar Repositorio

```bash
git clone https://github.com/rhizor/providence-soc.git
cd providence-soc
```

### 2. Desplegar Infraestructura

```bash
# Usando Terraform (recomendado)
cd terraform
terraform init
terraform plan
terraform apply

# O manualmente según docs/SETUP.md
```

## 📂 Estructura del Proyecto

```
providence-soc/
├── README.md
├── LICENSE
├── docs/
│   ├── SETUP.md                 # Guía de instalación detallada
│   ├── ARCHITECTURE.md          # Diseño de arquitectura
│   ├── VLAN_CONFIGURATION.md     # Configuración de VLANs
│   ├── SECURITY.md              # Hardening y seguridad
│   └── TROUBLESHOOTING.md       # Guía de problemas comunes
├── scripts/
│   ├── ansible/                 # Playbooks de Ansible
│   ├── powershell/              # Scripts de Windows
│   └── bash/                    # Scripts de automatización
├── configs/
│   ├── pfsense/                # Configuraciones pfSense
│   ├── proxmox/                # Configuraciones Proxmox
│   └── nginx/                  # Configuraciones Nginx
├── terraform/                  # IaC para despliegue
├── diagrams/                   # Diagramas de arquitectura
└── tests/                      # Tests y validaciones
```

## 🌐 Segmentación de Red

### Esquema de VLANs

| VLAN ID | Nombre | Subred | Propósito | Dispositivos |
|---------|--------|--------|-----------|---------------|
| 10 | Victim | 10.10.10.0/24 | Red de víctimas | DCs, servidores, clientes |
| 20 | SIEM | 10.10.20.0/24 | Monitoreo | Security Onion, Wazuh, ELK |
| 30 | RedTeam | 10.10.30.0/24 | Ataques controlados | Kali, DVWA, Metasploitable |
| 40 | DMZ | 10.10.40.0/24 | Servicios expuestos | Nginx, proxies |
| 50 | Management | 10.10.50.0/24 | Administración | JumpHost, Ansible |

### Reglas de Firewall

```
# Reglas pfSense (documentadas en configs/pfsense/rules.conf)

# WAN → pfSense
- Block all incoming (default deny)

# LAN → ANY
- Allow all (trusted network)

# Victim (VLAN 10)
- Allow HTTP/HTTPS to DMZ
- Allow DNS to Management
- Allow ICMP to all
- Block direct to Internet (proxy only)

# SIEM (VLAN 20)
- Allow all to Victim (monitoring)
- Allow all to DMZ
- Allow HTTPS to Internet

# Attacker (VLAN 30)
- Allow to DMZ only
- Allow DNS to Management
- Log all traffic

# DMZ (VLAN 40)
- Allow HTTP/HTTPS from WAN
- Allow to SIEM (logging)
- Block to Victim

# Management (VLAN 50)
- Allow SSH/HTTPS to all VLANs
- Block to Internet (except updates)
```

## 🔐 Configuración de Seguridad

### Hardening del Sistema

- **OS Hardening**: CIS Benchmarks
- **Network Hardening**: Least privilege
- **Access Control**: RBAC
- **Monitoring**: 24/7 alerting
- **Backup**: Configuraciones críticas

### Autenticación

- **Local**: Active Directory
- **Network**: RADIUS
- **VPN**: OpenVPN/IPSec
- **MFA**: TOTP para management

## 📊 Componentes de Monitoreo

### SIEM Stack

```
┌─────────────────────────────────────────────────────┐
│              CAPA DE VISUALIZACIÓN                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │  Kibana  │  │  Grafana │  │  Squert  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────────┐
│              CAPA DE ANÁLISIS                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Wazuh    │  │ Suricata │  │  Zeek    │         │
│  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────┘
                      │
┌─────────────────────────────────────────────────────┐
│              CAPA DE COLECCIÓN                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │Filebeat  │  │Winlogbeat│  │  Auditd  │         │
│  └──────────┘  └──────────┘  └──────────┘         │
└─────────────────────────────────────────────────────┘
```

## 🔧 Despliegue Automatizado

### Ansible Playbooks

```bash
# Desplegar agentes Wazuh
cd scripts/ansible
ansible-playbook -i inventory wazuh_agents.yml

# Configurar monitoring
ansible-playbook -i inventory monitoring.yml

# Hardening de sistemas
ansible-playbook -i inventory hardening.yml
```

### Terraform

```bash
# Inicializar Terraform
cd terraform
terraform init

# Validar configuración
terraform validate

# Plan de despliegue
terraform plan -var-file=prod.tfvars

# Aplicar cambios
terraform apply -var-file=prod.tfvars
```

## 🧪 Validación y Testing

### Checklist de Seguridad

- [ ] pfSense instalado y configurado
- [ ] Todas las VLANs creadas
- [ ] Reglas de firewall aplicadas
- [ ] Security Onion recibiendo tráfico
- [ ] Wazuh agentes desplegados
- [ ] Logs fluyendo a SIEM
- [ ] Alertas configuradas
- [ ] Backups configurados
- [ ] Documentación completa

### Tests Automatizados

```bash
# Ejecutar tests
python3 -m pytest tests/ -v

# Validar arquitectura
python3 scripts/validate_architecture.py
```

## 📚 Documentación

- [Guía de Instalación](docs/SETUP.md)
- [Diseño de Arquitectura](docs/ARCHITECTURE.md)
- [Configuración de VLANs](docs/VLAN_CONFIGURATION.md)
- [Hardening y Seguridad](docs/SECURITY.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contribuir

1. Fork el proyecto
2. Crear branch (`git checkout -b feature/nueva-feature`)
3. Commitear cambios
4. Pushear y crear Pull Request

## 📜 Licencia

MIT License - ver LICENSE para detalles.

---

*"I have looked upon all that the universe has to hold of horror, and even the skies of spring and the flowers of summer must ever afterward be poison to me."* — H.P. Lovecraft
