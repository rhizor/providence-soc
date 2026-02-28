# Providence SOC - Diseño de Arquitectura

## Tabla de Contenidos

1. [Principios de Diseño](#1-principios-de-diseño)
2. [Patrones de Arquitectura](#2-patrones-de-arquitectura)
3. [Diseño de Red](#3-diseño-de-red)
4. [Diseño de Seguridad](#4-diseño-de-seguridad)
5. [Diseño de Alta Disponibilidad](#5-diseño-de-alta-disponibilidad)
6. [Diseño de Monitoreo](#6-diseño-de-monitoreo)

---

## 1. Principios de Diseño

### 1.1 Principios Fundamentales

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRINCIPIOS DE DISEÑO                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │    DEFENSE   │  │  ZERO TRUST  │  │  LAYERED     │        │
│  │    IN DEPTH  │  │              │  │  SECURITY    │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │    LEAST     │  │   FAIL       │  │   AUDIT      │        │
│  │   PRIVILEGE  │  │    SECURE    │  │   EVERYTHING │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Principios Aplicados

| Principio | Implementación en Providence SOC |
|-----------|--------------------------------|
| Defense in Depth | Múltiples capas: Firewall → VLANs → SIEM → Hardening |
| Zero Trust | No confiar en ninguna red por defecto, verificar todo |
| Least Privilege | RBAC, permisos mínimos, segmentation |
| Fail Secure | pfSense bloquea por defecto, fail-closed |
| Audit Everything | Logs en todos los componentes |

---

## 2. Patrones de Arquitectura

### 2.1 Patrón: Three-Tier Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION TIER                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Kibana    │  │   Grafana   │  │  Squert    │            │
│  │  Dashboard  │  │  Dashboard  │  │  Web UI    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      APPLICATION TIER                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Wazuh     │  │  Suricata   │  │    Zeek    │            │
│  │  Manager    │  │   IDS/IPS   │  │   Analyzer │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                        DATA TIER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │Elasticsearch│  │    MySQL    │  │    Redis    │            │
│  │   (Logs)    │  │  (Config)   │  │  (Cache)    │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Patrón: Pipeline de Procesamiento de Eventos

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ Collect │ -> │  Parse  │ -> │  Enrich │ -> │  Store │ -> │Visualize│
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │              │
  ┌──▼──┐       ┌──▼──┐       ┌──▼──┐       ┌──▼──┐       ┌──▼──┐
  │File │       │Grok  │       │GeoIP│       │ES   │       │Kibana│
  │beat │       │Filter│       │TI   │       │Index│       │      │
  │Winlog│      │      │       │AD   │       │     │       │      │
  │Audit│      │      │       │     │       │     │       │      │
  │d    │       │      │       │     │       │     │       │      │
  └─────┘       └──────┘       └─────┘       └──────┘       └──────┘
```

### 2.3 Patrón: Observer para Alertas

```
┌─────────────────────────────────────────────────────────────────┐
│                    OBSERVER PATTERN                             │
│                                                                 │
│  ┌─────────────┐                        ┌─────────────────────┐ │
│  │  Subject    │                        │     Observers       │ │
│  │ (Events)    │                        │                     │ │
│  ├─────────────┤    notify()           │  ┌───────────────┐  │ │
│  │ + attach()  │ ──────────────────────│─▶│  Slack        │  │ │
│  │ + detach()  │                        │  ├───────────────┤  │ │
│  │ + notify()  │                        │  │  Email        │  │ │
│  │             │                        │  ├───────────────┤  │ │
│  │  events[]   │                        │  │  Telegram     │  │ │
│  └─────────────┘                        │  ├───────────────┤  │ │
│                                        │  │  Jira         │  │ │
│                                        │  └───────────────┘  │ │
│                                        └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.4 Patrón: Factory para VMs

```
┌─────────────────────────────────────────────────────────────────┐
│                     FACTORY PATTERN                              │
│                                                                 │
│                    ┌─────────────────┐                          │
│                    │   VMFactory     │                          │
│                    ├─────────────────┤                          │
│                    │ + create_vm()   │                          │
│                    │ + configure()   │                          │
│                    │ + validate()    │                          │
│                    └────────┬────────┘                          │
│                             │                                   │
│              ┌──────────────┼──────────────┐                   │
│              ▼              ▼              ▼                    │
│     ┌────────────┐  ┌────────────┐  ┌────────────┐          │
│     │WinServerVM │  │  LinuxVM   │  │  RouterVM  │          │
│     │ Template   │  │  Template  │  │  Template  │          │
│     └────────────┘  └────────────┘  └────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.5 Patrón: Strategy para Reglas de Firewall

```
┌─────────────────────────────────────────────────────────────────┐
│                    STRATEGY PATTERN                              │
│                                                                 │
│  ┌──────────────────┐      ┌──────────────────┐                │
│  │   FirewallContext│─────▶│  FirewallStrategy│                │
│  ├──────────────────┤      ├──────────────────┤                │
│  │ - strategy       │      │ + evaluate()    │                │
│  │ + setStrategy()  │      └────────┬─────────┘                │
│  │ + evaluate()     │               │                          │
│  └──────────────────┘        ┌─────┴─────┬─────┐              │
│                               ▼           ▼                     │
│                      ┌────────────┐ ┌────────────┐             │
│                      │BlockStrategy│ │AllowStrategy│            │
│                      │(pfSense)   │ │(Internal)   │             │
│                      └────────────┘ └────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Diseño de Red

### 3.1 Modelo de Capas

```
┌─────────────────────────────────────────────────────────────────┐
│                     CAPA 7 - APPLICATION                        │
│                 (Servicios, Aplicaciones)                       │
├─────────────────────────────────────────────────────────────────┤
│                     CAPA 3-4 - NETWORK                          │
│                    (Enrutamiento, Firewalls)                    │
├─────────────────────────────────────────────────────────────────┤
│                     CAPA 2 - DATA LINK                          │
│                      (VLANs, Switches)                           │
├─────────────────────────────────────────────────────────────────┤
│                     CAPA 1 - PHYSICAL                           │
│                   (Cables, Interfaces)                          │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Flujo de Tráfico

```
                    INTERNET
                        │
                        ▼
                ┌─────────────┐
                │    WAN      │
                │  pfSense    │
                └──────┬──────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │  VLAN10 │   │  VLAN20 │   │  VLAN30 │
   │ Victim  │   │  SIEM   │   │Attacker │
   └────┬────┘   └────┬────┘   └────┬────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
                ┌──────▼──────┐
                │   SIEM      │
                │  (logging)   │
                └─────────────┘
```

---

## 4. Diseño de Seguridad

### 4.1 Defense in Depth

```
┌─────────────────────────────────────────────────────────────────┐
│                     DEFENSE IN DEPTH                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CAPA 5: Applications                                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • WAF (Web Application Firewall)                         │  │
│  │ • Input Validation                                        │  │
│  │ • SQL Injection Prevention                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  CAPA 4: Host Security                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Endpoint Protection (Wazuh)                            │  │
│  │ • OS Hardening                                           │  │
│  │ • Patch Management                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  CAPA 3: Network Security                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • IDS/IPS (Suricata)                                     │  │
│  │ • Segmentation (VLANs)                                  │  │
│  │ • Firewall Rules                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  CAPA 2: Perimeter                                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • pfSense Firewall                                       │  │
│  │ • VPN                                                    │  │
│  │ • NAT                                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Matriz de Controles

| Capa | Control | Tecnología | Implementación |
|------|---------|------------|----------------|
| Perimeter | Firewall | pfSense | Block all by default |
| Perimeter | VPN | OpenVPN | MFA required |
| Network | Segmentation | VLANs | 5 isolated networks |
| Network | IDS | Suricata | Inline mode |
| Network | Monitoring | Zeek | Full packet capture |
| Host | EDR | Wazuh | Agent-based |
| Host | Hardening | Ansible | CIS Benchmarks |
| Application | WAF | Nginx | Rule-based |

---

## 5. Diseño de Alta Disponibilidad

### 5.1 Arquitectura HA

```
┌─────────────────────────────────────────────────────────────────┐
│                    HA DESIGN                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│    ┌─────────────┐        ┌─────────────┐                       │
│    │  pfSense-1  │◀─────▶│  pfSense-2  │                       │
│    │   (Active)  │  CARP │   (Backup)  │                       │
│    └──────┬──────┘        └──────┬──────┘                       │
│           │                      │                              │
│           │      Load Balancer   │                              │
│           │◀─────────────────────▶│                              │
│           │                      │                              │
│           ▼                      ▼                              │
│    ┌─────────────┐        ┌─────────────┐                       │
│    │  SIEM-1     │◀─────▶│   SIEM-2    │                       │
│    │  (Primary)  │  HA    │  (Replica)  │                       │
│    └─────────────┘        └─────────────┘                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Flujo de Failover

```
┌─────────────────────────────────────────────────────────────────┐
│                    FAILOVER FLOW                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Normal Operation:                                            │
│   User ─▶ pfSense-1 ─▶ Services ─▶ pfSense-1 ─▶ User         │
│                                                                  │
│   pfSense-1 Fails:                                             │
│   User ─▶ pfSense-2 (CARP takeover) ─▶ Services ─▶ User       │
│                                                                  │
│   Recovery:                                                    │
│   pfSense-1 returns ─▶ Sync config ─▶ Return to Active        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Diseño de Monitoreo

### 6.1 Stack de Monitoreo

```
┌─────────────────────────────────────────────────────────────────┐
│                    MONITORING STACK                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    DASHBOARDS                            │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│  │  │ Kibana  │  │ Grafana │  │ Squert  │  │  Wazuh  │   │   │
│  │  │(Logs)   │  │(Metrics)│  │(Alerts) │  │(HIDS)  │   │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    ANALYTICS                             │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │   │
│  │  │Suricata │  │  Zeek   │  │ Wazuh   │  │ ElastAl │    │   │
│  │  │(NIDS)   │  │(Traffic)│  │(HIDS)   │  │(Alert)  │    │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    COLLECTION                            │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │   │
│  │  │ Filebeat │  │Winlogbeat│ │  Auditd │  │  Zeek   │    │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 KPIs de Monitoreo

| Métrica | Descripción | Objetivo |
|---------|-------------|----------|
| MTTD | Mean Time To Detect | < 5 minutos |
| MTTR | Mean Time To Respond | < 30 minutos |
| Coverage | Log coverage | 100% |
| False Positives | Alertas falsas | < 5% |
| Uptime | Disponibilidad | 99.9% |

---

## 7. Componentes de Red

### 7.1 Diagrama de Red Detallado

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              WAN                                        │
│                           203.0.113.0/30                                │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │      pfSense          │
                    │   WAN: 203.0.113.2    │
                    │   LAN: 192.168.1.1    │
                    │   OPT1-5: VLANs       │
                    └───────────┬────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
   ┌─────────┐            ┌─────────┐            ┌─────────┐
   │ VLAN10  │            │ VLAN20  │            │ VLAN30  │
   │ Victim  │            │  SIEM   │            │Attacker │
   │ /24     │            │  /24    │            │  /24    │
   └────┬────┘            └────┬────┘            └────┬────┘
        │                       │                       │
   ┌────┴────┐            ┌────┴────┐            ┌────┴────┐
   │ DC01    │            │SecOnion │            │  Kali   │
   │ 10.10   │            │ 10.10   │            │ 10.10   │
   │ .10.10  │            │ .20.10  │            │ .30.100 │
   └─────────┘            └─────────┘            └─────────┘
```

---

## 8. Servicios y Puertos

### 8.1 Matriz de Puertos

| Servicio | IP | Puerto | Protocolo | Acceso |
|----------|-----|--------|-----------|--------|
| pfSense GUI | 192.168.1.1 | 443 | HTTPS | LAN only |
| pfSense SSH | 192.168.1.1 | 22 | SSH | LAN only |
| Security Onion | 10.10.20.10 | 5601 | HTTPS | Management |
| Kibana | 10.10.20.10 | 5601 | HTTPS | Management |
| Wazuh API | 10.10.20.20 | 55000 | HTTPS | Management |
| Elasticsearch | 10.10.20.10 | 9200 | HTTPS | SIEM VLAN |
| DC01 | 10.10.10.10 | 3389 | RDP | Victim |
| JumpHost | 10.10.50.10 | 22 | SSH | Management |
| DNS | 10.10.50.5 | 53 | DNS/UDP | All VLANs |
| NTP | 10.10.50.5 | 123 | NTP | All VLANs |

---

## 9. Diseño de Backup

### 9.1 Estrategia de Backup

```
┌─────────────────────────────────────────────────────────────────┐
│                    BACKUP STRATEGY                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Configuration Backups:                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ pfSense: Daily auto-backup to off-site                    │  │
│  │ Proxmox: Weekly snapshot of all VMs                       │  │
│  │ Ansible: Config backed to Git                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Log Retention:                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Hot: 7 days (SSD)                                        │  │
│  │ Warm: 30 days (HDD)                                      │  │
│  │ Cold: 1 year (Archive)                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  VM Snapshots:                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Daily: Retain 7 days                                     │  │
│  │ Weekly: Retain 4 weeks                                   │  │
│  │ Monthly: Retain 12 months                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```
