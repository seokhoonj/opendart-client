"""OpenDART domain exceptions.

``DartError`` is the base; the subclasses map the OpenDART status codes into the
kinds of failure a caller actually branches on (bad key, rate limit, bad field,
server down). ``error_for`` picks the subclass from a status code. Status ``013``
(no data) is NOT an error -- it is an expected empty and is handled in the session,
never raised.
"""

from __future__ import annotations


class DartError(RuntimeError):
    """An OpenDART API failure (a non-000, non-013 status, or a transport error).

    Carries the status code and message, plus the guide URL of the endpoint that
    failed, so the traceback points straight at the spec.
    """

    def __init__(self, status: str, message: str, guide_url: str | None = None) -> None:
        detail = f"OpenDART status {status}: {message}"
        if guide_url:
            detail = f"{detail} ({guide_url})"
        super().__init__(detail)
        self.status = status
        self.message = message
        self.guide_url = guide_url


class AuthError(DartError):
    """Key rejected or not permitted (010/011/012/101/901)."""


class RateLimitError(DartError):
    """Request quota exceeded (020/021)."""


class ValidationError(DartError):
    """A field value the API rejected (100)."""


class ServerError(DartError):
    """OpenDART is down or returned an undefined error (800/900)."""


_STATUS_TO_ERROR: dict[str, type[DartError]] = {
    "010": AuthError,
    "011": AuthError,
    "012": AuthError,
    "101": AuthError,
    "901": AuthError,
    "020": RateLimitError,
    "021": RateLimitError,
    "100": ValidationError,
    "800": ServerError,
    "900": ServerError,
}


def error_for(status: str, message: str, guide_url: str | None = None) -> DartError:
    """Build the most specific DartError subclass for an OpenDART status code."""
    return _STATUS_TO_ERROR.get(status, DartError)(status, message, guide_url)
