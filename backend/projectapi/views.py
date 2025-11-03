from __future__ import annotations

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from pathlib import Path
import json
from .utils import concurrent_search


@api_view(["GET"])
def health(_request):
    return JsonResponse({"status": "ok"})


@csrf_exempt
@api_view(["POST"])
@parser_classes([MultiPartParser])
def upload_files(request):
    storage_dir: Path = settings.EVENT_STORAGE_DIR  # type: ignore[attr-defined]
    saved = []
    for f in request.FILES.getlist("files"):
        dest = storage_dir / f.name
        with dest.open("wb") as out:
            for chunk in f.chunks():
                out.write(chunk)
        saved.append({"filename": f.name, "size": dest.stat().st_size})
    return JsonResponse({"saved": saved})


@csrf_exempt
@api_view(["POST"])
def search_events(request):
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # criteria: arbitrary field matches (e.g., srcaddr, dstaddr, action, account-id, etc.)
    criteria = payload.get("criteria") or {}
    if not isinstance(criteria, dict):
        return JsonResponse({"error": "criteria must be an object"}, status=400)

    # optional epoch start/end times
    start_time = payload.get("starttime")
    end_time = payload.get("endtime")
    try:
        start_time = int(start_time) if start_time is not None else None
        end_time = int(end_time) if end_time is not None else None
    except (TypeError, ValueError):
        return JsonResponse({"error": "starttime/endtime must be integers"}, status=400)

    workers = int(payload.get("workers", 8))
    max_per_file = payload.get("max_results_per_file")
    max_per_file = int(max_per_file) if max_per_file is not None else None

    storage_dir: Path = settings.EVENT_STORAGE_DIR  # type: ignore[attr-defined]
    results, elapsed = concurrent_search(
        directory=storage_dir,
        criteria=criteria,
        start_time=start_time,
        end_time=end_time,
        workers=workers,
        max_results_per_file=max_per_file,
    )

    # Compact projection for UI convenience
    compact = [
        {
            "summary": f"{r.get('srcaddr','?')} → {r.get('dstaddr','?')} | Action: {r.get('action','?')} | Log Status: {r.get('log-status','?')}",
            "file": r.get("__file__", "unknown"),
            "event": r,
        }
        for r in results
    ]

    return JsonResponse(
        {
            "count": len(compact),
            "elapsed_seconds": round(elapsed, 4),
            "results": compact,
        }
    )




