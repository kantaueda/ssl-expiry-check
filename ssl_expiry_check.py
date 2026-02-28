import argparse
import socket
import ssl
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Tuple


@dataclass
class Result:
    host: str
    ok: bool
    days_left: int | None
    not_after_utc: str | None
    error: str | None


def read_targets(path: str) -> List[str]:
    hosts: List[str] = []
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            hosts.append(s)
    return hosts


def fetch_cert_not_after(host: str, port: int, timeout: float) -> datetime:
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            cert = ssock.getpeercert()
            not_after = cert.get("notAfter")
            if not not_after:
                raise RuntimeError("Certificate has no notAfter field")

            not_after = not_after.replace(" GMT", "")
            dt = datetime.strptime(not_after, "%b %d %H:%M:%S %Y").replace(tzinfo=timezone.utc)
            return dt


def check_host(host: str, port: int, timeout: float) -> Result:
    try:
        dt = fetch_cert_not_after(host, port, timeout)
        now = datetime.now(timezone.utc)
        days_left = (dt - now).days
        return Result(
            host=host,
            ok=True,
            days_left=days_left,
            not_after_utc=dt.isoformat(),
            error=None,
        )
    except Exception as e:
        return Result(
            host=host,
            ok=False,
            days_left=None,
            not_after_utc=None,
            error=str(e),
        )


def print_table(results: List[Result], warn_days: int) -> Tuple[bool, bool]:
    has_error = False
    has_warn = False

    print(f"{'HOST':30} {'DAYS_LEFT':>9}  STATUS  EXPIRES_UTC / ERROR")
    print("-" * 90)

    for r in results:
        if not r.ok:
            has_error = True
            print(f"{r.host:30} {'-':>9}  ERROR   {r.error}")
            continue

        status = "OK"
        if r.days_left is not None and r.days_left < 0:
            has_error = True
            status = "EXPIRED"
        elif r.days_left is not None and r.days_left <= warn_days:
            has_warn = True
            status = "WARN"

        print(f"{r.host:30} {r.days_left:>9}  {status:6} {r.not_after_utc}")

    return has_error, has_warn


def main() -> int:
    parser = argparse.ArgumentParser(description="Check SSL certificate expiry for hosts.")
    parser.add_argument("targets_file", help="Path to targets.txt (one host per line)")
    parser.add_argument("--port", type=int, default=443)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--warn-days", type=int, default=30, help="Warn if days_left <= warn-days")
    args = parser.parse_args()

    hosts = read_targets(args.targets_file)
    if not hosts:
        print("No targets found.", file=sys.stderr)
        return 2

    results = [check_host(h, args.port, args.timeout) for h in hosts]
    has_error, has_warn = print_table(results, args.warn_days)

    if has_error:
        return 2
    if has_warn:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
