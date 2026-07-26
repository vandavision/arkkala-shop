#!/usr/bin/env python
import sys
import urllib.request

URL: str = "http://127.0.0.1:8000/healthz/"
TIMEOUT: int = 4

try:
    with urllib.request.urlopen(URL, timeout=TIMEOUT) as response:
        if response.status == 200:
            sys.exit(0)
        sys.exit(1)
except Exception:
    sys.exit(1)