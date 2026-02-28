# Providence SOC - Hardening y Seguridad

## 1. Hardening de pfSense

### 1.1 Configuración Inicial

```bash
# Cambiar contraseña por defecto
# System > User Manager > admin > Password

# Habilitar HTTPS único
# System > Advanced > Admin Access
# Protocol: HTTPS
# SSL Certificate: Generate internal CA

# Cambiar puerto SSH
# System > Advanced > SSH
# Port: 2222
# Permit root login: No
```

### 1.2 Hardening de Red

```bash
# Desabilitar IPv6 si no se usa
# Interfaces > WAN > Disable IPv6
# Interfaces > LAN > Disable IPv6

# Bloquear spoofing de IP
# Firewall > Anti-Spoofing > Enable

# Habilitar SYN cookies
# System > Advanced > Firewall
# Enable SYN cookies: Yes
```

### 1.3 Reglas de Firewall Recomendadas

```
# Reglas WAN (Block todo por defecto)
Action: Block
Interface: WAN
Address Family: IPv4+IPv6
Log: Yes

# Reglas LAN (Trust)
Action: Pass
Interface: LAN
Source: LAN net
Destination: Any

# Reglas VLAN10 - Victim (Restrictiva)
- Allow HTTP/HTTPS to DMZ
- Allow DNS to 10.10.50.5
- Allow ICMP to all
- Block direct to Internet
- Log all denies

# Reglas VLAN20 - SIEM (Permisiva para monitoreo)
- Allow all to Victim
- Allow all to DMZ
- Allow HTTPS to Internet

# Reglas VLAN30 - Attacker (Muy restrictiva)
- Allow to DMZ only
- Allow DNS to Management
- Block to Victim (log)
- Log all traffic

# Reglas VLAN40 - DMZ
- Allow HTTP/HTTPS from WAN
- Allow to SIEM
- Block to Victim

# Reglas VLAN50 - Management
- Allow SSH/HTTPS from LAN only
- Block to Internet (except updates)
```

## 2. Hardening de Proxmox

### 2.1 Configuración de Seguridad

```bash
# Actualizar regularmente
apt update && apt upgrade -y

# Instalar fail2ban
apt install fail2ban

# Configurar firewall UFW
apt install ufw
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 8006/tcp
ufw enable

# Hardening SSH
nano /etc/ssh/sshd_config

# Cambios recomendados:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
```

### 2.2 Aislar VMs con VLANs

```bash
# Configurar bridge con VLAN filtering
nano /etc/network/interfaces

auto lo
iface lo inet loopback

# Bridge con VLANs
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

## 3. Hardening de VMs Linux

### 3.1 OS Hardening Genérico

```bash
# Actualizar sistema
apt update && apt upgrade -y

# Instalar paquetes de seguridad
apt install -y \
    auditd \
    fail2ban \
    rkhunter \
    chkrootkit \
    libpam-cracklib \
    needrestart

# Configurar auditoría
nano /etc/audit/audit.rules

# Agregar reglas:
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/group -p wa -k identity
-w /var/log/ -p wa -k logins
-w /usr/bin/ -p x -k execution

# Configurar fail2ban
nano /etc/fail2ban/jail.local

[sshd]
enabled = true
port = ssh
filter = sshd
maxretry = 3
bantime = 3600
```

### 3.2 Sysctl Hardening

```bash
# /etc/sysctl.conf

# IP Spoofing protection
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Ignore ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv6.conf.default.accept_redirects = 0

# Don't send redirects
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# Ignore ICMP ping requests
net.ipv4.icmp_echo_ignore_all = 0
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Ignore bogus ICMP errors
net.ipv4.icmp_ignore_bogus_error_responses = 1

# Enable TCP SYN cookies
net.ipv4.tcp_syncookies = 1

# Disable source packet routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0
net.ipv6.conf.default.accept_source_route = 0
```

## 4. Hardening de Windows

### 4.1 Configuración Local de Seguridad

```powershell
# PowerShell - Configurar política de ejecución
Set-ExecutionPolicy Restricted -Force

# Habilitar Windows Firewall
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True

# Configurar reglas básicas
New-NetFirewallRule -DisplayName "Allow ICMP" -Protocol ICMPv4 -Enabled True -Action Allow

# Deshabilitar servicios innecesarios
Stop-Service -Name "TelnetService" -Force
Set-Service -Name "TelnetService" -StartupType Disabled

# Habilitar Windows Defender
Set-MpPreference -DisableRealtimeMonitoring $false
Set-MpPreference -DisableScriptScanning $false
```

### 4.2 Politicas de Grupo Locales

```
# Configuración de seguridad local
secpol.msc

# Politicas de cuenta:
- Longitud mínima de contraseña: 14 caracteres
- Historial de contraseñas: 24
- Bloqueo de cuenta: 5 intentos fallidos

# Politicas locales:
- Auditoría de acceso: Success, Failure
- Apagar sistema: solo Administrators
```

## 5. Hardening de SIEM

### 5.1 Security Onion

```bash
# Configurar actualización de reglas
sudo so-rule-update

# Habilitar todas las reglas de ET
sudo so-allow

# Configurar captura de tráfico
sudo so-elastic-restart

# Hardening de Elasticsearch
# /etc/elasticsearch/elasticsearch.yml
xpack.security.enabled: true
xpack.security.http.ssl.enabled: true
```

### 5.2 Wazuh

```bash
# Configurar autenticación
# /var/ossec/etc/ossec.conf
<auth>
    <use_password>yes</use_password>
    <force_insert>yes</force_insert>
    <use_source_ip>no</use_source_ip>
</auth>

# Habilitar SSL
<ssl>
    <tls>yes</tls>
</ssl>
```

## 6. Autenticación y Acceso

### 6.1 Autenticación Multi-Factor

```bash
# Configurar 2FA para pfSense
# Install: System > Package Manager > Available > squidGuard
# Configure 2FA with Google Authenticator

# Configurar 2FA para SSH
apt install libpam-google-authenticator

# Editar /etc/pam.d/sshd
auth required pam_google_authenticator.so

# Editar /etc/ssh/sshd_config
ChallengeResponseAuthentication yes
AuthenticationMethods password,keyboard-interactive
```

### 6.2 VPN con pfSense

```
# Install OpenVPN
# VPN > OpenVPN > Wizards

# Configurar:
- User Authentication: Local Database
- Certificate: Create new CA
- Server: 10.10.50.0/24
- DNS: 10.10.50.5
- Firewall: Add rules for OpenVPN
```

## 7. Monitoreo de Seguridad

### 7.1 Configurar Alertas

```yaml
# /etc/elastalert/rules/providence_alerts.yaml

name: Providence SOC Critical Alerts
es_host: localhost
es_port: 9200
index: logstash-*

filter:
- term:
    severity: "critical"

alert:
- type: slack
  slack_webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK"
  
- type: email
  email:
    - "admin@providence.local"
```

### 7.2 Dashboard de Seguridad

```
# Kibana - Crear dashboards para:

1. Network Traffic Overview
   - Traffic by source/destination
   - Top talkers
   - Protocol distribution

2. Threat Detection
   - Alerts by severity
   - Top attack vectors
   - Geographic distribution

3. Compliance Status
   - ISO 27001 controls
   - Policy violations
   - Remediation status
```

## 8. Backup y Recuperación

### 8.1 Backup de Configuración

```bash
# pfSense backup
# System > Backup & Restore > Backup

# Proxmox backup
# Datacenter > Backup > Add Job

# Automatizar con cron
0 2 * * * /usr/local/bin/proxmox-backup.sh
```

### 8.2 Verificación de Integridad

```bash
# Configurar AIDE
apt install aide
aideinit

# Configurar verificación diaria
crontab -e
0 3 * * * /usr/bin/aide --check
```

## 9. Checklist de Hardening

### Pre-Despliegue
- [ ] pfSense instalado y configurado
- [ ] Todas las VLANs creadas
- [ ] Reglas de firewall aplicadas
- [ ] Certificados SSL firmados

### Post-Despliegue
- [ ] Contraseñas cambiadas por defecto
- [ ] SSH hardening aplicado
- [ ] fail2ban configurado
- [ ] Auditoría habilitada
- [ ] Backup automatizado configurado
- [ ] Alertas configuradas
- [ ] Logs centralizados

### Verificación Mensual
- [ ] Revisar logs de auditoría
- [ ] Verificar actualizaciones de seguridad
- [ ] Testear restore de backups
- [ ] Revisar alertas falsas
- [ ] Actualizar reglas de SIEM
