from django.db import connections
from django.db.utils import OperationalError
from django.http import JsonResponse
from django.http.request import HttpRequest


def healthz(request: HttpRequest) -> JsonResponse:
    """
    Health-check endpoint for verifying database connectivity.
    """
    db_ok: bool = True
    db_error: str | None = None

    try:
        conn = connections["default"]
        conn.cursor()
    except OperationalError as exc:
        db_ok = False
        db_error = str(exc)

    payload: dict[str, str] = {
        "status": "ok" if db_ok else "error",
        "database": "ok" if db_ok else "unreachable",
    }
    
    if db_error:
        payload["error"] = db_error

    return JsonResponse(payload, status=200 if db_ok else 503)