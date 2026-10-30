
# NetOps-Pro

NetOps-Pro is a Linux server monitoring
and automation platform.

## Current Features

### 1. Connectivity Diagnostics
- DNS resolution checks
- ICMP ping checks
- TCP port connectivity checks
- HTTP endpoint checks
- JSON connectivity reports

### 2. Network Inventory
- Network interface information
- Routing table collection
- DNS resolver information
- Docker network inventory
- Docker container inventory
- Default route validation

## Technologies
- Ubuntu Linux
- Python 3
- Git and GitHub
- Linux networking utilities
- JSON

## Project Structure

```text
NetOps-Pro/
├── README.md
├── .gitignore
├── scripts/
│   ├── connectivity_check.py
│   └── network_inventory.py
├── reports/
└── config/
```

## Execution

Run connectivity diagnostics:

```bash
python3 scripts/connectivity_check.py
```

Collect network inventory:

```bash
python3 scripts/network_inventory.py
```

## Future Enhancements
- Bash automation
- CPU, RAM and disk monitoring
- Linux service monitoring
- Log analysis
- Python REST API monitoring
- Automated JSON reporting

## Upcoming Features

- CPU monitoring
- Memory monitoring
- Disk utilization monitoring
