#!/usr/bin/env python3
"""
Simple load-testing script for nightly performance baselines.

Usage:
    python load_test.py --base-url http://localhost:5000 --duration 30 --concurrency 10
"""

import argparse
import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import Request, urlopen
from urllib.error import URLError


ENDPOINTS = [
    ("GET", "/health"),
    ("GET", "/health/ready"),
    ("GET", "/api/v1/accounts?page=1&per_page=10"),
    ("GET", "/api/v1/transactions?page=1&per_page=10"),
    ("GET", "/api/v1/reports/summary"),
]


def make_request(base_url: str, method: str, path: str) -> dict:
    """Execute a single HTTP request and return timing info."""
    url = f"{base_url}{path}"
    start = time.monotonic()
    try:
        req = Request(url, method=method)
        with urlopen(req, timeout=10) as resp:
            elapsed = time.monotonic() - start
            return {
                "url": url,
                "status": resp.status,
                "latency_ms": round(elapsed * 1000, 2),
                "success": True,
            }
    except (URLError, OSError) as exc:
        elapsed = time.monotonic() - start
        return {
            "url": url,
            "status": 0,
            "latency_ms": round(elapsed * 1000, 2),
            "success": False,
            "error": str(exc),
        }


def run_load_test(
    base_url: str,
    duration_seconds: int,
    concurrency: int,
) -> dict:
    """Run load test for the given duration."""
    results = []
    errors = 0
    start_time = time.monotonic()

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        while time.monotonic() - start_time < duration_seconds:
            futures = []
            for method, path in ENDPOINTS:
                futures.append(pool.submit(make_request, base_url, method, path))

            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                if not result["success"]:
                    errors += 1

    elapsed = time.monotonic() - start_time
    latencies = [r["latency_ms"] for r in results if r["success"]]

    return {
        "total_requests": len(results),
        "successful": len(results) - errors,
        "failed": errors,
        "error_rate_pct": round((errors / max(len(results), 1)) * 100, 2),
        "duration_seconds": round(elapsed, 2),
        "requests_per_second": round(len(results) / elapsed, 2),
        "latency_ms": {
            "min": round(min(latencies), 2) if latencies else 0,
            "max": round(max(latencies), 2) if latencies else 0,
            "mean": round(statistics.mean(latencies), 2) if latencies else 0,
            "median": round(statistics.median(latencies), 2) if latencies else 0,
            "p95": round(
                sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0, 2
            ),
            "p99": round(
                sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0, 2
            ),
        },
        "concurrency": concurrency,
    }


def main():
    parser = argparse.ArgumentParser(description="Load test runner")
    parser.add_argument("--base-url", required=True, help="Base URL of the API")
    parser.add_argument("--duration", type=int, default=30, help="Test duration in seconds")
    parser.add_argument("--concurrency", type=int, default=5, help="Number of concurrent workers")
    parser.add_argument("--output", default=None, help="Output JSON file path")
    args = parser.parse_args()

    print(f"Running load test against {args.base_url}")
    print(f"  Duration: {args.duration}s | Concurrency: {args.concurrency}")
    print("-" * 60)

    report = run_load_test(args.base_url, args.duration, args.concurrency)

    print(f"\nResults:")
    print(f"  Total requests:     {report['total_requests']}")
    print(f"  Successful:         {report['successful']}")
    print(f"  Failed:             {report['failed']}")
    print(f"  Error rate:         {report['error_rate_pct']}%")
    print(f"  Requests/sec:       {report['requests_per_second']}")
    print(f"  Latency (median):   {report['latency_ms']['median']}ms")
    print(f"  Latency (p95):      {report['latency_ms']['p95']}ms")
    print(f"  Latency (p99):      {report['latency_ms']['p99']}ms")

    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to {args.output}")

    if report["error_rate_pct"] > 5:
        print("\nWARNING: Error rate exceeds 5% threshold!")
        sys.exit(1)


if __name__ == "__main__":
    main()
