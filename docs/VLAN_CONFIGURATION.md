# Providence SOC - Configuración de VLANs

## Resumen de VLANs

| VLAN ID | Nombre | Subred | Gateway | DHCP Range | Propósito |
|---------|--------|--------|---------|------------|-----------|
| 10 | Victim | 10.10.10.0/24 | .1 | .100-.200 | DCs, servidores, clientes |
| 20 | SIEM | 10.10.20.0/24 | .1 | .100-.150 | Monitoreo y seguridad |
| 30 | Attacker | 10.10.30.0/24 | .1 | .100-.200 | Red Team / CTF |
| 40 | DMZ | 10.10.40.0/24 | .1 | .50-.100 | Servicios expuestos |
| 50 | Management | 10.10.50.0/24 | .1 | .10-.50 | Administración |

## Configuración en pfSense

### Crear VLANs en pfSense

```
# Web UI: Interfaces > Assignments > VLANs

1. Click "Add" para cada VLAN:
   - Parent Interface: LAN (em1)
   - VLAN Tag: 10
   - Priority: 0
   - Description: Victim Network
   
2. Repetir para VLANs 20, 30, 40, 50
```

### Asignar Interfaces a VLANs

```
# Interfaces > Assignments

VLAN10 -> opt1 (em1_vlan10)
VLAN20 -> opt2 (em1_vlan20)
VLAN30 -> opt3 (em1_vlan30)
VLAN40 -> opt4 (em1_vlan40)
VLAN50 -> opt5 (em1_vlan50)
```

### Configurar IPs

```
# Cada interfaz VLAN:

VLAN10 (opt1):
- Enable: ✓
- IPv4: 10.10.10.1/24
- IPv6: None

VLAN20 (opt2):
- Enable: ✓
- IPv4: 10.10.20.1/24

VLAN30 (opt3):
- Enable: ✓
- IPv4: 10.10.30.1/24

VLAN40 (opt4):
- Enable: ✓
- IPv4: 10.10.40.1/24

VLAN50 (opt5):
- Enable: ✓
- IPv4: 10.10.50.1/24
```

## Configuración DHCP por VLAN

### VLAN 10 - Victim

```
Services > DHCP Server > VLAN10

Enable: ✓
Range: 10.10.10.100 - 10.10.10.200
Gateway: 10.10.10.1
DNS: 10.10.50.5
Domain: providence.local
NTP: 10.10.50.5

Options:
- Deny unknown clients: No
- Enable static ARP entries: No
```

### VLAN 20 - SIEM

```
Services > DHCP Server > VLAN20

Enable: ✓
Range: 10.10.20.100 - 10.10.20.150
Gateway: 10.10.20.1
DNS: 10.10.50.5
Domain: providence.siem
```

### VLAN 30 - Attacker

```
Services > DHCP Server > VLAN30

Enable: ✓
Range: 10.10.30.100 - 10.10.30.200
Gateway: 10.10.30.1
DNS: 10.10.50.5
```

### VLAN 40 - DMZ

```
Services > DHCP Server > VLAN40

Enable: ✓
Range: 10.10.40.50 - 10.10.40.100
Gateway: 10.10.40.1
DNS: 10.10.50.5
```

### VLAN 50 - Management

```
Services > DHCP Server > VLAN50

Enable: ✓
Range: 10.10.50.10 - 10.10.50.50
Gateway: 10.10.50.1
DNS: 10.10.50.5 (self)
```

## Configuración de Switch

### Switch Cisco

```cisco
! Crear VLANs
vlan 10
 name Victim
vlan 20
 name SIEM
vlan 30
 name Attacker
vlan 40
 name DMZ
vlan 50
 name Management

! Configurar puertos trunk
interface GigabitEthernet1/0/1
 description Trunk to pfSense
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,50

! Puertos de acceso
interface GigabitEthernet1/0/10
 description Victim Network
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast

interface GigabitEthernet1/0/20
 description SIEM Network
 switchport mode access
 switchport access vlan 20
```

### Switch HP/ProCurve

```hp
vlan 10
   name "Victim"
   untagged 1-10
vlan 20
   name "SIEM"
   untagged 11-15
vlan 30
   name "Attacker"
   untagged 16-20
vlan 40
   name "DMZ"
   untagged 21-25
vlan 50
   name "Management"
   untagged 26-30

! Trunk
trunk 47-48 trk1 lacp
```

## Verificación

### Verificar VLANs en pfSense

```bash
# Via CLI en pfSense
pfSensectl -v

# Ver interfaces
ifconfig | grep vlan
```

### Verificar Conectividad

```bash
# Test desde cada VLAN
ping -c 3 10.10.10.1  # Victim gateway
ping -c 3 10.10.20.1  # SIEM gateway
ping -c 3 10.10.30.1  # Attacker gateway
ping -c 3 10.10.40.1  # DMZ gateway
ping -c 3 10.10.50.1  # Management gateway

# Test de aislamiento
# Desde Victim -> Attacker debe estar bloqueado
ping -c 1 10.10.30.1  # Should fail

# Desde SIEM -> Todas las VLANs
ping -c 1 10.10.10.1  # Should work
ping -c 1 10.10.30.1  # Should work
```

## Tabla de Servicios por VLAN

| Servicio | IP | VLAN | Notas |
|----------|-----|------|-------|
| DC01 | 10.10.10.10 | 10 | Domain Controller |
| WIN-SRV01 | 10.10.10.11 | 10 | File Server |
| WIN-CLIENT01 | DHCP | 10 | Workstation |
| Security Onion | 10.10.20.10 | 20 | NIDS |
| Wazuh | 10.10.20.20 | 20 | HIDS |
| Kali Linux | 10.10.30.100 | 30 | Attacker |
| DVWA | 10.10.30.110 | 30 | Vulnerable Web |
| Nginx Proxy | 10.10.40.10 | 40 | Reverse Proxy |
| JumpHost | 10.10.50.10 | 50 | Admin Access |
| DNS/NTP | 10.10.50.5 | 50 | Services |
