import subprocess
import socket
import argparse
import platform
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(description="Simple network monitoring tool")
    parser.add_argument("--hosts", default="hosts.txt", help="Path to hosts file")
    parser.add_argument("--port", type=int, default=443, help="TCP port")
    parser.add_argument("--timeout", type=int, default=2, help="Connection timeout in seconds")
    return parser.parse_args()


def ping_host(host, timeout):
    """
    Perform ICMP ping to check if the host responds.
    Some systems may block ICMP, therefore TCP check is also used.
    Works on Windows and Linux/macOS.
    """
    system = platform.system().lower()

    try:
        if system == "windows":
            # timeout in milliseconds
            cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), host]
        else:
            # Linux/macOS
            cmd = ["ping", "-c", "1", host]

        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception:
        return False


def tcp_check(host, port, timeout):
    """
    Try to establish TCP connection to the specified port.
    Successful connection means the service is reachable.
    """
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def log(message):
    """Append monitoring result to log file."""
    with open("monitor.log", "a", encoding="utf-8") as f:
        f.write(message + "\n")


def main():
    args = parse_args()

    # Read monitoring targets
    with open(args.hosts, encoding="utf-8") as f:
        hosts = [line.strip() for line in f if line.strip()]

    # Check each host
    for host in hosts:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        icmp = ping_host(host, args.timeout)
        tcp = tcp_check(host, args.port, args.timeout)

        # If at least one method works → host is reachable
        status = "UP" if icmp or tcp else "DOWN"

        output = f"[{now}] {host} status: {status}"
        print(output)
        log(output)


if __name__ == "__main__":
    main()
