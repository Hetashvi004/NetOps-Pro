
#!/usr/bin/env python3

import json
import socket
import subprocess
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_DIR / "reports"


def check_dns(domain):
    try:
        addresses = sorted({
            result[4][0]
            for result in socket.getaddrinfo(
                domain, None, type=socket.SOCK_STREAM
            )
        })

        return {
            "test": "DNS",
            "target": domain,
            "status": "PASS",
            "details": addresses,
        }
    except socket.gaierror as exc:
        return {
            "test": "DNS",
            "target": domain,
            "status": "FAIL",
            "details": str(exc),
        }


def check_ping(ip):
    try:
        result = subprocess.run(
            ["ping", "-c", "3", "-W", "2", ip],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        return {
            "test": "PING",
            "target": ip,
            "status": "PASS" if result.returncode == 0 else "FAIL",
            "details": result.stdout.strip() or result.stderr.strip(),
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "test": "PING",
            "target": ip,
            "status": "ERROR",
            "details": str(exc),
        }



def check_tcp(host, port):
    import socket

    target = f"{host}:{port}"

    try:
        with socket.create_connection((host, port), timeout=3):
            return {
                "test": "TCP",
                "target": target,
                "status": "PASS",
                "details": "TCP connection established",
                "diagnosis": "Service is accepting TCP connections",
            }

    except ConnectionRefusedError:
        return {
            "test": "TCP",
            "target": target,
            "status": "FAIL",
            "details": "Connection refused",
            "diagnosis": (
                "No service is listening, or the destination "
                "actively rejected the connection"
            ),
        }

    except TimeoutError:
        return {
            "test": "TCP",
            "target": target,
            "status": "FAIL",
            "details": "Connection timed out",
            "diagnosis": (
                "No response before timeout; investigate routing, "
                "filtering, and destination availability"
            ),
        }

    except OSError as exc:
        return {
            "test": "TCP",
            "target": target,
            "status": "ERROR",
            "details": str(exc),
            "diagnosis": "Inspect the network error and target configuration",
        }



def check_http(url):
    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "NetOps-Pro/1.0"},
        )

        with urllib.request.urlopen(
            request, timeout=5
        ) as response:
            status_code = response.status

            return {
                "test": "HTTP",
                "target": url,
                "status": (
                    "PASS"
                    if 200 <= status_code < 400
                    else "FAIL"
                ),
                "details": f"HTTP status {status_code}",
            }

    except urllib.error.HTTPError as exc:
        return {
            "test": "HTTP",
            "target": url,
            "status": "FAIL",
            "details": f"HTTP status {exc.code}",
        }
    except (OSError, TimeoutError, ValueError) as exc:
        return {
            "test": "HTTP",
            "target": url,
            "status": "FAIL",
            "details": str(exc),
        }


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    results = [
        check_dns("example.com"),
        check_ping("192.168.240.20"),
        check_tcp("127.0.0.1", 8080),
        check_http("http://127.0.0.1:8080/"),
        check_tcp("127.0.0.1", 65000),
    ]


    report = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "results": results,
        "summary": {
            "passed": sum(
                item["status"] == "PASS" for item in results
            ),
            "failed": sum(
                item["status"] == "FAIL" for item in results
            ),
            "errors": sum(
                item["status"] == "ERROR" for item in results
            ),
        },
    }

    report_path = REPORT_DIR / "connectivity_report.json"
    report_path.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("=" * 55)
    print("NETOPS PRO - CONNECTIVITY DIAGNOSTICS")
    print("=" * 55)


    for result in results:
        print(
            f"[{result['status']}] "
            f"{result['test']} - {result['target']}"
        )
        print(f"  {result['details']}")

        if "diagnosis" in result:
            print(f"  Diagnosis: {result['diagnosis']}")

    print("\nSummary:", report["summary"])
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
