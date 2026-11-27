import json
import socket
import time
from datetime import datetime, timezone

import psutil


def collect_cpu_metrics() -> dict:
    """Collect CPU utilization and load averages."""

    load_1, load_5, load_15 = psutil.getloadavg()

    return {
        "usage_percent": psutil.cpu_percent(interval=1),
        "logical_cores": psutil.cpu_count(),
        "physical_cores": psutil.cpu_count(logical=False),
        "load_average": {
            "1_min": load_1,
            "5_min": load_5,
            "15_min": load_15,
        },
    }


def collect_memory_metrics() -> dict:
    """Collect physical memory statistics."""

    memory = psutil.virtual_memory()

    return {
        "total_bytes": memory.total,
        "used_bytes": memory.used,
        "available_bytes": memory.available,
        "free_bytes": memory.free,
        "usage_percent": memory.percent,
    }


def collect_swap_metrics() -> dict:
    """Collect swap memory statistics."""

    swap = psutil.swap_memory()

    return {
        "total_bytes": swap.total,
        "used_bytes": swap.used,
        "free_bytes": swap.free,
        "usage_percent": swap.percent,
        "swap_in_bytes": swap.sin,
        "swap_out_bytes": swap.sout,
    }


def collect_disk_metrics(path: str = "/") -> dict:
    """Collect filesystem capacity and disk I/O."""

    disk = psutil.disk_usage(path)
    disk_io = psutil.disk_io_counters()

    return {
        "mount_path": path,
        "total_bytes": disk.total,
        "used_bytes": disk.used,
        "free_bytes": disk.free,
        "usage_percent": disk.percent,
        "io": {
            "read_count": disk_io.read_count,
            "write_count": disk_io.write_count,
            "read_bytes": disk_io.read_bytes,
            "write_bytes": disk_io.write_bytes,
        } if disk_io is not None else None,
    }


def collect_network_metrics() -> dict:
    """Collect cumulative network traffic counters."""

    network = psutil.net_io_counters()

    if network is None:
        return {"available": False}

    return {
        "available": True,
        "bytes_sent": network.bytes_sent,
        "bytes_received": network.bytes_recv,
        "packets_sent": network.packets_sent,
        "packets_received": network.packets_recv,
        "errors_in": network.errin,
        "errors_out": network.errout,
        "drops_in": network.dropin,
        "drops_out": network.dropout,
    }


def collect_system_metrics() -> dict:
    """Collect hostname, boot time and uptime."""

    boot_time = psutil.boot_time()

    return {
        "hostname": socket.gethostname(),
        "boot_time": datetime.fromtimestamp(
            boot_time, tz=timezone.utc
        ).isoformat(),
        "uptime_seconds": int(time.time() - boot_time),
    }


def collect_all_metrics() -> dict:
    """Combine all metrics into a structured dictionary."""

    start_time = time.perf_counter()

    metrics = {
        "schema_version": "1.0",
        "system": collect_system_metrics(),
        "cpu": collect_cpu_metrics(),
        "memory": collect_memory_metrics(),
        "swap": collect_swap_metrics(),
        "disk": collect_disk_metrics(),
        "network": collect_network_metrics(),
    }

    metrics["collected_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    metrics["collection_duration_seconds"] = round(
        time.perf_counter() - start_time, 3
    )

    return metrics


def main() -> None:
    metrics = collect_all_metrics()

    print(json.dumps(metrics, indent=4))


if __name__ == "__main__":
    main()
