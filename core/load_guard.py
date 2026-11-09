import os
import threading
from functools import wraps

from flask import Response, jsonify


class LoadGuard:
    def __init__(self, max_concurrent=None, saturation_threshold=None):
        limit = (
            max_concurrent
            if max_concurrent is not None
            else int(os.environ.get("MAX_CONCURRENT_AI_REQUESTS", "5"))
        )

        threshold = (
            saturation_threshold
            if saturation_threshold is not None
            else int(os.environ.get("LOAD_FAILURE_THRESHOLD", "3"))
        )

        if limit < 1 or threshold < 1:
            raise ValueError("Параметры защиты должны быть не меньше 1")

        self.limit = limit
        self.saturation_threshold = threshold
        self._semaphore = threading.BoundedSemaphore(limit)
        self._lock = threading.Lock()
        self._rejections = 0
        self._saturation_notified = False
        self.on_saturation = None

    def protect(self, function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if not self._semaphore.acquire(blocking=False):
                activate = False

                with self._lock:
                    self._rejections += 1

                    if (
                        self._rejections >= self.saturation_threshold
                        and not self._saturation_notified
                    ):
                        self._saturation_notified = True
                        activate = True

                if activate and self.on_saturation:
                    self.on_saturation(
                        "Повторяющиеся отказы из-за нагрузки"
                    )

                response = jsonify({
                    "error": "Flint временно перегружен. Попробуйте позже."
                })
                response.status_code = 503
                response.headers["Retry-After"] = "10"
                return response

            with self._lock:
                self._rejections = 0
                self._saturation_notified = False

            release_here = True
            try:
                result = function(*args, **kwargs)

                if isinstance(result, Response):
                    result.call_on_close(self._semaphore.release)
                    release_here = False

                return result
            finally:
                if release_here:
                    self._semaphore.release()

        return wrapper


load_guard = LoadGuard()
