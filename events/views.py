import time
from typing import Dict, Any, List

from django.db import transaction
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .models import Event
from .serializers import EventSerializer


def _to_int(value: str):
    try:
        return int(value)
    except Exception:
        return None


def parse_event_line(line: str) -> Dict[str, Any]:
    # Expect '|' separated fields; trim and map to model fields
    parts = [p.strip() for p in line.strip().split('|') if p.strip() != '']
    if len(parts) < 10:
        return {}

    # Heuristic mapping by likely positions
    mapping: Dict[str, Any] = {}
    try:
        # Common columns seen in the sample description (order may vary). We guard with bounds checks.
        # We'll attempt to find fields by simple heuristics; unknowns remain None.
        def at(i):
            return parts[i] if i < len(parts) else None

        mapping["serialno"] = _to_int(at(0) or "")
        mapping["version"] = _to_int(at(1) or "")
        mapping["account_id"] = at(2)
        mapping["instance_id"] = at(3)
        mapping["srcaddr"] = at(4)
        mapping["dstaddr"] = at(5)
        mapping["protocol"] = at(6)
        mapping["packets"] = _to_int(at(7) or "")
        mapping["bytes"] = _to_int(at(8) or "")
        mapping["starttime"] = _to_int(at(9) or "")
        mapping["endtime"] = _to_int(at(10) or "")
        mapping["action"] = at(11)
        mapping["log_status"] = at(12)
        mapping["srcport"] = _to_int(at(13) or "")
        mapping["dstport"] = _to_int(at(14) or "")
    except Exception:
        return {}
    return mapping


class UploadEventsView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        files = request.FILES.getlist('files')
        if not files:
            return Response({"detail": "No files provided. Use 'files' as the field name."}, status=status.HTTP_400_BAD_REQUEST)

        storage = FileSystemStorage(location=str(request._request.META.get("MEDIA_ROOT", None) or None))
        # Use settings.MEDIA_ROOT
        from django.conf import settings

        storage = FileSystemStorage(location=str(settings.MEDIA_ROOT))
        saved_files: List[str] = []
        total_saved = 0
        total_parsed = 0

        for f in files:
            filename = storage.save(f.name, f)
            filepath = settings.MEDIA_ROOT / filename
            saved_files.append(str(filename))
            # Parse and bulk insert
            to_create: List[Event] = []
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as fh:
                    for raw in fh:
                        raw_stripped = raw.strip()
                        if not raw_stripped:
                            continue
                        # Skip header lines likely containing non-numeric fields heavily
                        if raw_stripped.lower().startswith("serialno") or raw_stripped.lower().startswith("| serialno"):
                            continue
                        data = parse_event_line(raw)
                        if not data:
                            continue
                        ev = Event(
                            file_name=filename,
                            raw_line=raw_stripped,
                            **data,
                        )
                        to_create.append(ev)
                        if len(to_create) >= 1000:
                            Event.objects.bulk_create(to_create, ignore_conflicts=True)
                            total_parsed += len(to_create)
                            to_create = []
                if to_create:
                    Event.objects.bulk_create(to_create, ignore_conflicts=True)
                    total_parsed += len(to_create)
                total_saved += 1
            except Exception as e:
                return Response({"detail": f"Error processing {filename}: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "saved_files": saved_files,
            "files_uploaded": total_saved,
            "events_parsed": total_parsed,
        })


class SearchEventsView(APIView):
    def post(self, request, *args, **kwargs):
        start = time.perf_counter()

        # Support both formats:
        # 1) { search: "field=value" | "term", earliest, latest }
        # 2) { criteria: {field: value}, starttime, endtime }
        search = (request.data.get('search') or '').strip()
        earliest = request.data.get('earliest')
        latest = request.data.get('latest')

        criteria = request.data.get('criteria') or {}
        starttime_alt = request.data.get('starttime')
        endtime_alt = request.data.get('endtime')

        if starttime_alt is not None:
            earliest = starttime_alt
        if endtime_alt is not None:
            latest = endtime_alt

        qs = Event.objects.all()

        if earliest is not None:
            try:
                earliest_i = int(earliest)
                qs = qs.filter(endtime__gte=earliest_i)
            except Exception:
                pass

        if latest is not None:
            try:
                latest_i = int(latest)
                qs = qs.filter(starttime__lte=latest_i)
            except Exception:
                pass

        if criteria and isinstance(criteria, dict):
            # Field-based filtering
            field_map = {
                'account-id': 'account_id',
                'account_id': 'account_id',
                'instance-id': 'instance_id',
                'instance_id': 'instance_id',
                'srcaddr': 'srcaddr',
                'dstaddr': 'dstaddr',
                'action': 'action',
                'protocol': 'protocol',
                'srcport': 'srcport',
                'dstport': 'dstport',
                'file': 'file_name',
            }
            filters = {}
            for k, v in criteria.items():
                k2 = field_map.get(k, k)
                filters[k2] = v
            try:
                qs = qs.filter(**filters)
            except Exception:
                pass
        elif search:
            # Allow field-specific queries: field=value or generic search across key fields
            if '=' in search:
                field, value = [s.strip() for s in search.split('=', 1)]
                field_map = {
                    'account-id': 'account_id',
                    'account_id': 'account_id',
                    'instance-id': 'instance_id',
                    'instance_id': 'instance_id',
                    'srcaddr': 'srcaddr',
                    'dstaddr': 'dstaddr',
                    'action': 'action',
                    'protocol': 'protocol',
                    'srcport': 'srcport',
                    'dstport': 'dstport',
                    'file': 'file_name',
                }
                field = field_map.get(field, field)
                if field in {"srcport", "dstport"}:
                    try:
                        value = int(value)
                    except Exception:
                        value = None
                try:
                    qs = qs.filter(**{f"{field}": value})
                except Exception:
                    # Fallback to icontains on common text fields
                    qs = qs.filter(Q(srcaddr__icontains=search) | Q(dstaddr__icontains=search) | Q(action__icontains=search) | Q(account_id__icontains=search))
            else:
                qs = qs.filter(
                    Q(srcaddr__icontains=search)
                    | Q(dstaddr__icontains=search)
                    | Q(action__icontains=search)
                    | Q(account_id__icontains=search)
                    | Q(instance_id__icontains=search)
                )

        qs = qs.order_by('-starttime')[:1000]
        # Prepare simplified result objects for frontend
        simplified = []
        for e in qs:
            summary = f"{e.srcaddr}  {e.dstaddr} | Action: {e.action or ''} | Log Status: {e.log_status or ''}".replace('\u0011', '\u2192')
            simplified.append({
                "summary": summary,
                "file": e.file_name,
            })
        elapsed = time.perf_counter() - start

        return Response({
            "results": simplified,
            "count": qs.count(),
            "elapsed_seconds": round(elapsed, 4),
        })


# Create your views here.
