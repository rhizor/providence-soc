# Providence SOC - Troubleshooting

## 1. Problemas de Conectividad

### 1.1 No hay conectividad entre VLANs

**Síntomas:**
- VMs en diferentes VLANs no pueden comunicarse
- No hay ping entre gateways

**Diagnóstico:**
```bash
# 1. Verificar que las VLANs están configuradas en pfSense
# Interfaces > Assignments > VLANs

# 2. Verificar interfaces VLAN
ifconfig | grep vlan

# 3. Ver reglas de firewall
# Firewall > Rules > Revisar que haya reglas allow

# 4. Test de conectividad
ping -c 3 10.10.10.1  # Test gateway VLAN10
tcpdump -i vlan10 -n  # Ver tráfico
```

**Solución:**
```bash
# 1. Habilitar VLAN en pfSense
# Interfaces > Assignments > VLANs > Add
# Parent: LAN, Tag: 10

# 2. Asignar interfaz
# Interfaces > Assignments > Add

# 3. Habilitar interfaz
# Interfaces > VLAN10 > Enable > Save

# 4. Aplicar cambios
# Click "Apply Changes"
```

### 1.2 DHCP no funciona en VLAN

**Síntomas:**
- VMs no obtienen IP automáticamente
- IP asignada es incorrecta

**Diagnóstico:**
```bash
# 1. Ver estado del servicio DHCP
# Services > DHCP Server > Ver habilitado

# 2. Ver logs
tail -f /var/log/dhificar estácpd.log

# 3. Verificar pool de IPs
# Services > DHCP Server > VLANX > Rango
```

**Solución:**
```bash
# 1. Verificar rango DHCP no esté vacío
# Services > DHCP Server > VLANX
# Range: 10.10.10.100 - 10.10.10.200

# 2. Verificar gateway
# Gateway debe ser la IP de la interfaz VLAN

# 3. Reiniciar servicio DHCP
# Services > DHCP Server > Restart
```

## 2. Problemas de pfSense

### 2.1 pfSense no inicia

**Síntomas:**
- Servidor no responde después de reinicio

**Diagnóstico:**
```bash
# 1. Acceder por consola
# Ver mensajes de error en boot

# 2. Verificar disco
# Proxmox > Hardware > Disk > SMART test

# 3. Verificar recursos
# Proxmox > Summary > CPU/RAM
```

**Solución:**
```bash
# 1. Boot en modo seguro
# Seleccionar "Boot Single User"

# 2. Verificar sistema de archivos
/sbin/fsck -y

# 3. Reiniciar
reboot
```

### 2.2 Reglas de firewall no funcionan

**Síntomas:**
- Tráfico bloqueado que debería pasar
- Tráfico permitido que debería bloquearse

**Diagnóstico:**
```bash
# 1. Verificar orden de reglas
# Firewall > Rules > Las reglas se procesan top-down

# 2. Habilitar logging en reglas
# Regla > Log > Enable

# 3. Ver firewall logs
# Firewall > Logs > Packet Captures
```

**Solución:**
```bash
# 1. Mover regla específica arriba de regla general
# Arrastrar regla arriba en la lista

# 2. Verificar interfaz correcta
# La regla debe estar en la interfaz correcta (WAN/LAN/VLANX)

# 3. Aplicar cambios
# Click "Apply Changes"

# 4. Testear después de aplicar
```

## 3. Problemas de Proxmox

### 3.1 VM no inicia

**Síntomas:**
- Error al iniciar VM
- VM queda en estado "stopped"

**Diagnóstico:**
```bash
# 1. Verificar recursos
qm status <vmid>
qm info <vmid>

# 2. Verificar disco
qm rescan

# 3. Ver logs
tail -f /var/log/pveproxy/access.log
```

**Solución:**
```bash
# 1. Liberar recursos
# Cerrar otras VMs que no se usen

# 2. Verificar storage
pvesm status

# 3. Mover VM a otro storage
qm move_disk <vmid> scsi0 local-lvm
```

### 3.2 Red no funciona en VM

**Síntomas:**
- VM no tiene conectividad
- No puede hacer ping al gateway

**Diagnóstico:**
```bash
# 1. Verificar VLAN tag
qm config <vmid> | grep net0

# 2. Test de conectividad
ip addr show
ip route show
ping -c 3 8.8.8.8
```

**Solución:**
```bash
# 1. Verificar bridge config
bridge vlan

# 2. Recargar red
systemctl restart networking

# 3. Verificar MAC address
# No debe haber duplicados
```

## 4. Problemas de SIEM

### 4.1 Security Onion no recibe tráfico

**Síntomas:**
- No aparecen logs en Kibana
- Alertas no se generan

**Diagnóstico:**
```bash
# 1. Verificar estado de servicios
sudo so-status

# 2. Verificar captura
sudo tcpdump -i ensXXX -c 10

# 3. Ver logs de Zeek
tail -f /nsm/zeek/logs/current/conn.log
```

**Solución:**
```bash
# 1. Habilitar interfaz de monitoreo
# Network > Monitor Mode > Enable

# 2. Verificar que Suricata esté corriendo
sudo so-suricata-status

# 3. Reiniciar servicios
sudo so-restart
```

### 4.2 Wazuh agentes no conectan

**Síntomas:**
- Agentes aparecen como "Disconnected"
- No hay eventos en dashboard

**Diagnóstico:**
```bash
# 1. Verificar servicio en agente
systemctl status wazuh-agent

# 2. Ver configuración
cat /var/ossec/etc/ossec.conf

# 3. Test de conectividad
telnet 10.10.20.20 1514
```

**Solución:**
```bash
# 1. Verificar Manager IP en agente
# /var/ossec/etc/ossec.conf
<client>
    <server>
        <address>10.10.20.20</address>
    </server>
</client>

# 2. Reiniciar agente
systemctl restart wazuh-agent

# 3. Verificar registro
/var/ossec/bin/agent-auth -m 10.10.20.20 -p 1515 -A <agent-name>
```

## 5. Problemas de Red

### 5.1 No hay internet desde VLAN

**Síntomas:**
- VMs pueden hacer ping a gateway pero no a internet

**Diagnóstico:**
```bash
# 1. Verificar NAT
# Firewall > NAT > Outbound

# 2. Verificar DNS
# Services > DNS Resolver

# 3. Test de DNS
nslookup google.com
```

**Solución:**
```bash
# 1. Configurar NAT
# Firewall > NAT > Outbound
# Mode: Automatic outbound NAT rule generation

# 2. Configurar DNS
# Services > DNS Resolver
# Enable: Yes
# Network Interfaces: All (lan)

# 3. Verificar gateway
# System > Routing > Gateways
# Default gateway debe estar UP
```

### 5.2 VLAN no puede acceder a otra VLAN

**Síntomas:**
- Victim no puede acceder a SIEM
- Error de timeout

**Diagnóstico:**
```bash
# 1. Ver reglas entre VLANs
# Firewall > Rules > Inter-VLAN

# 2. Test con ping
ping -c 3 10.10.20.10

# 3. Ver logs de firewall
# Firewall > Logs
```

**Solución:**
```bash
# 1. Crear regla allow en pfSense
# Firewall > Rules > VLAN10 > Add
# Action: Pass
# Interface: VLAN10
# Source: VLAN10 net
# Destination: VLAN20 net
# Protocol: Any

# 2. Click "Apply Changes"

# 3. Verificar con ping
```

## 6. Problemas de Rendimiento

### 6.1 Alto uso de CPU en pfSense

**Síntomas:**
- pfSense lento
- Alto load average

**Diagnóstico:**
```bash
# 1. Ver procesos
top -b | head -20

# 2. Verificar conexiones
pfctl -si

# 3. Contadores de estado
pfctl -s states
```

**Solución:**
```bash
# 1. Aumentar hardware (CPU cores)
# Proxmox > Hardware > CPU > Add more

# 2. Optimizar reglas
# Eliminar reglas redundantes

# 3. Deshabilitar servicios no usados
# Services > Unbound DNS > Disable if not needed
```

### 6.2 Alto uso de disco en SIEM

**Síntomas:**
- Elasticsearch sin espacio
- Logs no se almacenan

**Diagnóstico:**
```bash
# 1. Ver uso de disco
df -h

# 2. Ver tamaño de índices
curl -s 'localhost:9200/_cat/indices?v' | head -20

# 3. Ver logs
tail -f /var/log/elasticsearch/*.log
```

**Solución:**
```bash
# 1. Reducir retención
# Dev Tools > 
POST /logstash-*/_forcemerge?max_num_segments=1

# 2. Eliminar índices antiguos
DELETE /logstash-2024.01.*

# 3. Configurar ILM
# Index Lifecycle Policies
```

## 7. Comandos de Diagnóstico

### 7.1 Comandos de Red

```bash
# Ver interfaces
ip addr
ifconfig -a

# Ver tablas de enrutamiento
ip route
netstat -rn

# Ver conexiones
ss -tunapl
netstat -an

# Ver firewall
iptables -L -n
pfctl -sa
```

### 7.2 Comandos de Logs

```bash
# Ver logs de sistema
journalctl -xe
dmesg | tail

# Ver logs de autenticación
tail -f /var/log/auth.log

# Ver logs de kernel
tail -f /var/log/kern.log
```

### 7.3 Comandos de Servicios

```bash
# Estado de servicios
systemctl status networking
systemctl status sshd
systemctl status fail2ban

# Reiniciar servicio
systemctl restart networking
systemctl restart wazuh-agent
```

## 8. Contacto de Emergencia

### Checklist de Escalamiento

1. **Nivel 1** (Auto-solución)
   - Revisar documentación
   - Verificar cables y питание
   - Reiniciar servicio

2. **Nivel 2** (30 min)
   - Revisar logs
   - Verificar configuración
   - Consultar documentación oficial

3. **Nivel 3** (Escalamiento)
   - pfSense: https://forum.netgate.com/
   - Proxmox: https://forum.proxmox.com/
   - Wazuh: https://groups.google.com/forum/#!forum/wazuh

### Información para Soporte

```markdown
## Reportar Problema

**Fecha/Hora:**
**Componente:**
**Descripción:**
**Pasos para reproducir:**
**Comandos ejecutados:**
**Logs relevantes:**
```
