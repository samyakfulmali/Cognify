import base64
import hashlib
import hmac
import json
import time
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from app.config import SECRET_KEY, TEACHER_PIN


def _base64url_encode(data: bytes) -> str:
    """Base64 URL-safe encoding without padding."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _base64url_decode(data: str) -> bytes:
    """Base64 URL-safe decoding with auto-padding."""
    padding = "=" * (4 - len(data) % 4) if len(data) % 4 != 0 else ""
    return base64.urlsafe_b64decode((data + padding).encode("utf-8"))


def create_access_token(
    role: str,
    student_id: Optional[str] = None,
    name: Optional[str] = None,
    expires_in_seconds: int = 86400 * 7,
) -> str:
    """
    Creates a signed JWT-compatible session token signed with HMAC-SHA256.
    Payload contains role ('student' or 'teacher'), student_id, name, and expiration.
    """
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": student_id or "teacher",
        "role": role,
        "student_id": student_id,
        "name": name,
        "iat": now,
        "exp": now + expires_in_seconds,
    }

    header_b64 = _base64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}"

    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    sig_b64 = _base64url_encode(signature)

    return f"{signing_input}.{sig_b64}"


def verify_token(token: str) -> dict:
    """
    Verifies token signature and expiration, returning decoded payload dictionary.
    Raises HTTPException(401) on failure.
    """
    parts = token.strip().split(".")
    if len(parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format: expected 3 dot-separated segments.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}"

    expected_sig = hmac.new(
        SECRET_KEY.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    try:
        actual_sig = _base64url_decode(sig_b64)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token signature.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not hmac.compare_digest(expected_sig, actual_sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload_bytes = _base64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token payload.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    now = int(time.time())
    if "exp" in payload and payload["exp"] < now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    FastAPI dependency that reads and verifies the Bearer token from the Authorization header.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header. Authentication is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]
    return verify_token(token)


def require_teacher(current_user: dict = Depends(get_current_user)) -> dict:
    """
    FastAPI dependency requiring teacher role. Returns 403 Forbidden for students.
    """
    role = current_user.get("role")
    if role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Only teachers can access class-wide resources and analytics.",
        )
    return current_user


def verify_student_access(target_student_id: str, current_user: dict) -> None:
    """
    Enforces that students may ONLY access their own data.
    Teachers are permitted to view or update any student's data.
    """
    role = current_user.get("role")
    if role == "teacher":
        return

    if role == "student":
        token_student_id = current_user.get("student_id")
        if token_student_id != target_student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Student '{token_student_id}' is not authorized to access data for '{target_student_id}'.",
            )
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied: Unauthorized role.",
    )
