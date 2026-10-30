
#!/usr/bin/env python3

import json
import shutil
import subprocess
import socket
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_DIR / "reports"


def run_command(command):
    """Execute a command and safely collect its output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        return {
            "status": "OK" if result.returncode == 0 else "ERROR",
            "output": result.stdout.strip(),
            "error": result.stderr.strip(),
        }

    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "status": "ERROR",
            "output": "",
            "error": str(exc),
        }


def collect_inventory():
    commands = {
        "interfaces": ["ip", "-br", "addr"],
        "routes": ["ip", "route"],
        "dns": ["resolvectl", "status"],
        "docker_networks": ["docker", "network", "ls"],
        "docker_containers": ["docker", "ps"],
    }

    inventory = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "hostname": socket.gethostname(),
        "python_version": run_command(
            ["python3", "--version"]
        )["output"],
        "checks": {},
        "warnings": [],
    }

    for name, command in commands.items():
        if shutil.which(command[0]) is None:
            inventory["checks"][name] = {
                "status": "UNAVAILABLE",
                "output": "",
                "error": f"{command[0]} is not installed",
            }
            inventory["warnings"].append(
                f"{name}: required command is unavailable"
            )
            continue

        result = run_command(command)
        inventory["checks"][name] = result

        if result["status"] != "OK":
            inventory["warnings"].append(
                f"{name}: command failed; check the error"
            )

    routes = inventory["checks"].get("routes", {}).get("output", "")
    has_default_route = any(
        line.split()[:1] == ["default"]
        for line in routes.splitlines()
    )

    if not has_default_route:
        inventory["warnings"].append(
            "No default route found in the main routing table"
        )

    return inventory


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    inventory = collect_inventory()
    report_path = REPORT_DIR / "network_inventory.json"

    report_path.write_text(
        json.dumps(inventory, indent=2) + "\n",
        encoding="utf-8",
    )

    print("=" * 55)
    print("NETOPS PRO - NETWORK INVENTORY")
    print("=" * 55)
    print(f"Hostname: {inventory['hostname']}")
    print(f"Python:   {inventory['python_version']}")
    print()

    for name, result in inventory["checks"].items():
        print(f"[{result['status']}] {name}")

        if result["error"]:
            print(f"  Error: {result['error']}")

    print("\nWarnings:")
    if inventory["warnings"]:
        for warning in inventory["warnings"]:
            print(f"- {warning}")
    else:
        print("- No inventory warnings detected")

    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
