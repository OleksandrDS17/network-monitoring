import subprocess
import socket
from datetime import datetime

# Default TCP port used for connectivity tests
TCP_PORT = 443


def ping_host(host):
    """
    Perform ICMP ping to check if the host responds.
    Note: some devices may block ICMP, so TCP check is also required.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "1", host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception:
        return False


def tcp_check(host, port):
    """
    Try to establish TCP connection to the specified port.
    Successful connection means the service is reachable.
    """
    try:
        with socket.create_connection((host, port), timeout=2):
            return True
    except Exception:
        return False


def log(message):
    """
    Append monitoring result to log file.
    """
    with open("monitor.log", "a") as f:
        f.write(message + "\n")


def main():
    # Read hosts defined for monitoring
    with open("hosts.txt") as f:
        hosts = [line.strip() for line in f if line.strip()]

    # Iterate through each host and perform checks
    for host in hosts:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        icmp = ping_host(host)
        tcp = tcp_check(host, TCP_PORT)

        # If at least one check works → host considered reachable
        status = "UP" if icmp or tcp else "DOWN"

        output = f"[{now}] {host} status: {status}"
        print(output)
        log(output)


if __name__ == "__main__":
    main()


