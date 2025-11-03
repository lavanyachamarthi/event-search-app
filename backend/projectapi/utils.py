from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import json
import time
from typing import Dict, Iterable, List, Optional, Tuple


DEFAULT_HEADERS = [
    "serialno",
    "version",
    "account-id",
    "instance-id",
    "srcaddr",
    "dstaddr",
    "protocol",
    "packets",
    "bytes",
    "starttime",
    "endtime",
    "action",
    "log-status",
    "srcport",
    "dstport",
]


def parse_event_line(line: str) -> Optional[Dict[str, str]]:
    line = line.strip()
    if not line:
        return None
    # Try JSON first
    if line.startswith("{") and line.endswith("}"):
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                return {str(k): str(v) for k, v in obj.items()}
        except json.JSONDecodeError:
            pass
    # Fallback: pipe-delimited with optional leading/trailing pipes
    raw = [p.strip() for p in line.strip("|").split("|")]
    # Heuristic: accept if at least 6 columns
    if len(raw) >= 6:
        result: Dict[str, str] = {}
        for idx, val in enumerate(raw):
            key = DEFAULT_HEADERS[idx] if idx < len(DEFAULT_HEADERS) else f"col{idx}"
            if val:
                result[key] = val
        return result if result else None
    return None


def event_matches(
    event: Dict[str, str],
    criteria: Dict[str, str],
    start_time: Optional[int],
    end_time: Optional[int],
) -> bool:
    # Field criteria: all provided key/value pairs must match (string equality)
    for key, expected in criteria.items():
        actual = event.get(key)
        if actual is None or str(actual) != str(expected):
            return False
    # Time window intersects [start_time, end_time]
    if start_time is not None or end_time is not None:
        try:
            ev_start = int(event.get("starttime", event.get("start", "0")))
            ev_end = int(event.get("endtime", event.get("end", "0")))
        except ValueError:
            return False
        if start_time is not None and ev_end < start_time:
            return False
        if end_time is not None and ev_start > end_time:
            return False
    return True


def scan_file_for_events(
    file_path: Path,
    criteria: Dict[str, str],
    start_time: Optional[int],
    end_time: Optional[int],
    max_results: Optional[int] = None,
) -> List[Dict[str, str]]:
    matches: List[Dict[str, str]] = []
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                ev = parse_event_line(line)
                if ev and event_matches(ev, criteria, start_time, end_time):
                    ev_copy = dict(ev)
                    ev_copy["__file__"] = file_path.name
                    matches.append(ev_copy)
                    if max_results and len(matches) >= max_results:
                        break
    except Exception:
        # Ignore bad files
        return matches
    return matches


def concurrent_search(
    directory: Path,
    criteria: Dict[str, str],
    start_time: Optional[int],
    end_time: Optional[int],
    workers: int = 8,
    max_results_per_file: Optional[int] = None,
) -> Tuple[List[Dict[str, str]], float]:
    t0 = time.perf_counter()
    files = [p for p in directory.glob("**/*") if p.is_file()]
    results: List[Dict[str, str]] = []
    if not files:
        return results, 0.0
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                scan_file_for_events,
                p,
                criteria,
                start_time,
                end_time,
                max_results_per_file,
            )
            for p in files
        ]
        for fut in as_completed(futures):
            try:
                results.extend(fut.result())
            except Exception:
                continue
    dt = time.perf_counter() - t0
    return results, dt




