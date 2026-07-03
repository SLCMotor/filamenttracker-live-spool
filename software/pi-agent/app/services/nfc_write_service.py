from __future__ import annotations

import threading
from datetime import datetime, timedelta, timezone
from typing import Any

from app.models.nfc import NfcWriteRequest
from app.services.nfc_service import write_nfc_payload

TERMINAL_STATES = {"succeeded", "failed", "timed_out", "canceled"}
CURRENT_DISPLAY_SECONDS = 4
STATUS_RETENTION_MINUTES = 10


class NFCWriteService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._active_request_id: str | None = None
        self._cancel_requested = False
        self._statuses: dict[str, dict[str, Any]] = {}

    def start_write(self, request: NfcWriteRequest) -> dict[str, Any]:
        request_id = request.requestId.strip()
        if not request_id:
            return self._error_status("bad_request", "Request ID is required.")

        if not isinstance(request.payload, dict) or not request.payload:
            return self._error_status("bad_request", "NFC payload is required.")

        timeout_seconds = max(5, min(request.timeoutSeconds, 180))
        now = self._now()

        with self._lock:
            self._purge_old_locked()

            active = self._active_status_locked()
            if active and active.get("requestId") != request_id:
                return self._busy_status(active)

            if active and active.get("requestId") == request_id:
                return dict(active)

            status = {
                "requestId": request_id,
                "state": "ready",
                "message": "Ready to Write",
                "tagId": None,
                "errorCode": None,
                "payload": request.payload,
                "display": request.display or {},
                "startedAt": now,
                "updatedAt": now,
                "finishedAt": None,
            }
            self._statuses[request_id] = status
            self._active_request_id = request_id
            self._cancel_requested = False

        thread = threading.Thread(
            target=self._run_write,
            name=f"nfc-write-{request_id[:8]}",
            args=(request_id, request.payload, timeout_seconds),
            daemon=True,
        )
        thread.start()
        return self.get_status(request_id)

    def get_status(self, request_id: str) -> dict[str, Any]:
        with self._lock:
            status = self._statuses.get(request_id.strip())
            if status is None:
                return self._not_found_status(request_id)
            return dict(status)

    def get_current_status(self) -> dict[str, Any]:
        with self._lock:
            self._purge_old_locked()

            active = self._active_status_locked()
            if active:
                return dict(active)

            latest = self._latest_terminal_locked()
            if latest and self._is_recent_current_locked(latest):
                return dict(latest)

            return self._idle_status()

    def cancel_write(self, request_id: str) -> dict[str, Any]:
        request_id = request_id.strip()
        with self._lock:
            status = self._statuses.get(request_id)
            if status is None:
                return self._not_found_status(request_id)

            if status.get("state") in TERMINAL_STATES:
                return dict(status)

            self._cancel_requested = True
            self._update_status_locked(
                request_id=request_id,
                state="canceled",
                message="Write canceled",
                error_code="canceled",
                finished=True,
            )
            self._active_request_id = None
            return dict(self._statuses[request_id])

    def _run_write(
        self,
        request_id: str,
        payload: dict[str, Any],
        timeout_seconds: int,
    ) -> None:
        result = write_nfc_payload(
            payload=payload,
            timeout_seconds=timeout_seconds,
            progress_callback=lambda state, message, tag_id: self._update_status(
                request_id=request_id,
                state=state,
                message=message,
                tag_id=tag_id,
            ),
            cancel_callback=self._should_cancel,
        )

        if result.get("success"):
            self._finish_status(
                request_id=request_id,
                state="succeeded",
                message="Write Successful",
                tag_id=result.get("tagId"),
                error_code=None,
            )
            return

        error_code = result.get("errorCode") or "write_failed"
        state = "timed_out" if error_code == "timeout" else error_code
        if state not in TERMINAL_STATES:
            state = "failed"

        self._finish_status(
            request_id=request_id,
            state=state,
            message=result.get("message") or "Write failed",
            tag_id=result.get("tagId"),
            error_code=error_code,
        )

    def _should_cancel(self) -> bool:
        with self._lock:
            return self._cancel_requested

    def _update_status(
        self,
        request_id: str,
        state: str,
        message: str,
        tag_id: str | None = None,
    ) -> None:
        with self._lock:
            self._update_status_locked(
                request_id=request_id,
                state=state,
                message=message,
                tag_id=tag_id,
            )

    def _finish_status(
        self,
        request_id: str,
        state: str,
        message: str,
        tag_id: str | None,
        error_code: str | None,
    ) -> None:
        with self._lock:
            self._update_status_locked(
                request_id=request_id,
                state=state,
                message=message,
                tag_id=tag_id,
                error_code=error_code,
                finished=True,
            )
            if self._active_request_id == request_id:
                self._active_request_id = None
            self._cancel_requested = False

    def _update_status_locked(
        self,
        request_id: str,
        state: str,
        message: str,
        tag_id: str | None = None,
        error_code: str | None = None,
        finished: bool = False,
    ) -> None:
        status = self._statuses.get(request_id)
        if status is None:
            return

        status["state"] = state
        status["message"] = message
        status["updatedAt"] = self._now()
        if tag_id is not None:
            status["tagId"] = tag_id
        if error_code is not None:
            status["errorCode"] = error_code
        if finished:
            status["finishedAt"] = self._now()

    def _active_status_locked(self) -> dict[str, Any] | None:
        if not self._active_request_id:
            return None

        status = self._statuses.get(self._active_request_id)
        if status and status.get("state") not in TERMINAL_STATES:
            return status
        return None

    def _latest_terminal_locked(self) -> dict[str, Any] | None:
        terminal = [
            status
            for status in self._statuses.values()
            if status.get("state") in TERMINAL_STATES and status.get("finishedAt")
        ]
        if not terminal:
            return None
        return max(terminal, key=lambda status: status.get("finishedAt") or "")

    def _is_recent_current_locked(self, status: dict[str, Any]) -> bool:
        finished_at = self._parse_time(status.get("finishedAt"))
        if finished_at is None:
            return False
        return datetime.now(timezone.utc) - finished_at < timedelta(seconds=CURRENT_DISPLAY_SECONDS)

    def _purge_old_locked(self) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=STATUS_RETENTION_MINUTES)
        for request_id, status in list(self._statuses.items()):
            finished_at = self._parse_time(status.get("finishedAt"))
            if finished_at and finished_at < cutoff:
                self._statuses.pop(request_id, None)

    def _idle_status(self) -> dict[str, Any]:
        return {
            "requestId": None,
            "state": "idle",
            "message": "No write request",
            "tagId": None,
            "errorCode": None,
            "payload": None,
            "display": None,
            "startedAt": None,
            "updatedAt": self._now(),
            "finishedAt": None,
        }

    def _busy_status(self, active: dict[str, Any]) -> dict[str, Any]:
        return {
            **dict(active),
            "state": "busy",
            "message": "Another NFC write is already in progress.",
            "errorCode": "writer_busy",
        }

    def _not_found_status(self, request_id: str) -> dict[str, Any]:
        return {
            **self._idle_status(),
            "requestId": request_id,
            "state": "not_found",
            "message": "NFC write request was not found.",
            "errorCode": "not_found",
        }

    def _error_status(self, error_code: str, message: str) -> dict[str, Any]:
        return {
            **self._idle_status(),
            "state": "failed",
            "message": message,
            "errorCode": error_code,
        }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _parse_time(self, value: Any) -> datetime | None:
        if not isinstance(value, str) or not value:
            return None

        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None


nfc_write_service = NFCWriteService()


def start_nfc_write(request: NfcWriteRequest) -> dict[str, Any]:
    return nfc_write_service.start_write(request)


def get_nfc_write_status(request_id: str) -> dict[str, Any]:
    return nfc_write_service.get_status(request_id)


def get_current_nfc_write_status() -> dict[str, Any]:
    return nfc_write_service.get_current_status()


def cancel_nfc_write(request_id: str) -> dict[str, Any]:
    return nfc_write_service.cancel_write(request_id)
