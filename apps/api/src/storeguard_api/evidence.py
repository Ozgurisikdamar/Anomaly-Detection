"""Evidence media store + short-lived authenticated URL signing.

Evidence clips are uploaded by the (separate) pipeline process and stored under a
media root on the API host, keyed by ``evidence_id``. They are NEVER served by
raw filesystem path: a client receives a short-lived URL signed with an HMAC
secret (``STOREGUARD_EVIDENCE_SECRET``) that the serving endpoint verifies before
returning the bytes. This keeps storage paths — and any RTSP credentials — off
the wire.

The HMAC scheme is demo-grade (a shared secret, not per-user auth). Real
reviewer authentication is a later hardening item; documented as such.
"""

from __future__ import annotations

import hmac
import time
from hashlib import sha256
from pathlib import Path

_EXT = ".gif"


class EvidenceStore:
    """Filesystem-backed evidence store + URL signer."""

    def __init__(self, media_dir: str | Path, secret: str, ttl_s: int = 300) -> None:
        self._dir = Path(media_dir)
        self._secret = secret.encode("utf-8")
        self._ttl_s = ttl_s

    def ensure_dir(self) -> None:
        self._dir.mkdir(parents=True, exist_ok=True)

    # --- storage ---------------------------------------------------------
    def path(self, evidence_id: str) -> Path:
        # Guard against traversal: only the basename is used.
        safe = Path(evidence_id).name
        return self._dir / f"{safe}{_EXT}"

    def exists(self, evidence_id: str) -> bool:
        return self.path(evidence_id).is_file()

    def save(self, evidence_id: str, data: bytes) -> Path:
        self.ensure_dir()
        dst = self.path(evidence_id)
        dst.write_bytes(data)
        return dst

    # --- signing ---------------------------------------------------------
    def _sig(self, evidence_id: str, exp: int) -> str:
        msg = f"{evidence_id}:{exp}".encode()
        return hmac.new(self._secret, msg, sha256).hexdigest()

    def sign_url(self, evidence_id: str, now: float | None = None) -> tuple[str, int]:
        """Return a short-lived signed path for ``evidence_id`` and its expiry."""
        exp = int(now if now is not None else time.time()) + self._ttl_s
        sig = self._sig(evidence_id, exp)
        url = f"/api/v1/evidence/{evidence_id}?exp={exp}&sig={sig}"
        return url, exp

    def verify(
        self, evidence_id: str, exp: int, sig: str, now: float | None = None
    ) -> bool:
        """True if the token signature is valid and not expired."""
        current = now if now is not None else time.time()
        if exp < current:
            return False
        expected = self._sig(evidence_id, exp)
        return hmac.compare_digest(expected, sig)
