import json
import subprocess
import platform
import re
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_DIR / "reports"

REPORT_DIR.mkdir(exist_ok=True)

# Execute server health script
result = subprocess.run(
    ["bash", str(PROJECT_DIR / "scripts/server_health.sh")],
    capture_output=True,
    text=True
)

output = result.stdout

# Extract CPU usage
cpu_match = re.search(r"CPU Usage:\s*(\d+)%", output)
cpu_usage = int(cpu_match.group(1)) if cpu_match else None

# Extract memory information
memory = subprocess.check_output(
    ["free", "-b"], text=True
).splitlines()

mem_values = memory[1].split()

total_memory = int(mem_values[1])
used_memory = int(mem_values[2])
available_memory = int(mem_values[6])

memory_percent = round(
    used_memory / total_memory * 100, 2
)

# Extract disk usage
disk = subprocess.check_output(
    ["df", "-P", "/"], text=True
).splitlines()[1].split()

disk_usage = int(disk[4].replace("%", ""))

# Service status
services = {}

for service in ["ssh", "docker", "cron", "NetworkManager"]:
    check = subprocess.run(
        ["systemctl", "is-active", service],
        capture_output=True,
        text=True
    )

    services[service] = (
        "RUNNING" if check.stdout.strip() == "active"
        else "NOT_RUNNING"
    )

report = {
    "generated_at": datetime.now().astimezone().isoformat(),
    "hostname": platform.node(),

    "cpu": {
        "usage_percent": cpu_usage
    },

    "memory": {
        "total_bytes": total_memory,
        "used_bytes": used_memory,
        "available_bytes": available_memory,
        "usage_percent": memory_percent
    },

    "disk": {
        "usage_percent": disk_usage
    },

    "services": services,

    "summary": {
        "services_running": sum(
            value == "RUNNING"
            for value in services.values()
        ),
        "total_services": len(services)
    }
}

report_path = REPORT_DIR / "server_health.json"

with open(report_path, "w") as file:
    json.dump(report, file, indent=4)

print("SERVER HEALTH REPORT GENERATED")
print(json.dumps(report, indent=4))
print(f"\nReport saved to: {report_path}")
