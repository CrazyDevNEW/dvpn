from __future__ import annotations
import threading
from typing import Callable, Optional, Iterable, Any
from .pipes_utils import InterpPipe


class Worker:
    """Synchronous worker base for execution inside a subinterpreter thread.
    Do not spawn threads here; implement run() as a blocking loop.
    """

    def __init__(self, name: str) -> None:
        self.name = name

    def run(self, pipe_main: InterpPipe, pipe_data: InterpPipe, *args, **kwargs) -> None:  # pragma: no cover
        raise NotImplementedError


class StopToken:
    def __init__(self, event: threading.Event) -> None:
        self._e = event

    def is_set(self) -> bool:
        return self._e.is_set()

    def wait(self, timeout: Optional[float] = None) -> bool:
        return self._e.wait(timeout)


class ThreadGroup:
    """Lightweight thread group to be used INSIDE a subinterpreter.
    - spawn(): run a function with StopToken
    - stop(): request stop for all threads
    - join(): wait threads to finish
    """

    def __init__(self, name: str = "tg") -> None:
        self._name = name
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._threads: list[threading.Thread] = []

    @property
    def stop_token(self) -> StopToken:
        return StopToken(self._stop)

    def spawn(self, target: Callable[[StopToken, ...], Any], *args: Any, name: Optional[str] = None, daemon: bool = True, **kwargs: Any) -> threading.Thread:
        def runner() -> None:
            try:
                target(self.stop_token, *args, **kwargs)
            except Exception:
                # Let the worker handle/report; keep group alive
                pass
        t = threading.Thread(target=runner, name=name or f"{self._name}:worker", daemon=daemon)
        with self._lock:
            self._threads.append(t)
        t.start()
        return t

    def spawn_periodic(self, interval: float, func: Callable[[], Any], name: Optional[str] = None, daemon: bool = True) -> threading.Thread:
        def loop(token: StopToken) -> None:
            while not token.is_set():
                func()
                token.wait(interval)
        return self.spawn(loop, name=name or f"{self._name}:periodic", daemon=daemon)

    def stop(self) -> None:
        self._stop.set()

    def join(self, timeout: Optional[float] = None) -> None:
        with self._lock:
            threads = list(self._threads)
        for t in threads:
            t.join(timeout)


class ThreadedWorker(Worker):
    """Worker base that manages a ThreadGroup; implement run_main().
    The run() method ensures graceful stop/join of sub-threads.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._tg = ThreadGroup(name)

    def run(self, pipe_main: InterpPipe, pipe_data: InterpPipe, *args, **kwargs) -> None:  # type: ignore[override]
        try:
            self.run_main(self._tg, pipe_main, pipe_data, *args, **kwargs)
        finally:
            self._tg.stop()
            self._tg.join()

    def run_main(self, tg: ThreadGroup, pipe_main: InterpPipe, pipe_data: InterpPipe, *args, **kwargs) -> None:  # pragma: no cover
        raise NotImplementedError


