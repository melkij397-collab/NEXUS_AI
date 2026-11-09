import os
import threading
import time


class EmergencyShield:
    def __init__(self, recovery_seconds=None):
        self.recovery_seconds = (
            recovery_seconds
            if recovery_seconds is not None
            else int(os.environ.get("EMERGENCY_RECOVERY_SECONDS", "60"))
        )

        if self.recovery_seconds < 1:
            raise ValueError("Время восстановления должно быть не меньше 1 секунды")

        self._lock = threading.Lock()
        self._active = False
        self._reason = None
        self._activated_at = None

    def activate(self, reason="Высокая нагрузка"):
        with self._lock:
            self._active = True
            self._reason = str(reason)[:200]
            self._activated_at = time.monotonic()
            return True

    def deactivate(self):
        with self._lock:
            self._active = False
            self._reason = None
            self._activated_at = None
            return True

    def is_active(self):
        with self._lock:
            if (
                self._active
                and self._activated_at is not None
                and time.monotonic() - self._activated_at
                >= self.recovery_seconds
            ):
                self._active = False
                self._reason = None
                self._activated_at = None

            return self._active

    def status(self):
        with self._lock:
            if (
                self._active
                and self._activated_at is not None
                and time.monotonic() - self._activated_at
                >= self.recovery_seconds
            ):
                self._active = False
                self._reason = None
                self._activated_at = None

            return {
                "active": self._active,
                "reason": self._reason if self._active else None
            }


emergency_shield = EmergencyShield()
