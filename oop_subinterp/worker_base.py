import threading
from typing import Optional
from .pipes import InterpPipe


class Worker:
    def __init__(self, name: str) -> None:
        self.name = name
        self._thread: Optional[threading.Thread] = None
        self._stopped = threading.Event()

    def start(self, pipe_main: InterpPipe, pipe_data: InterpPipe, *args, **kwargs) -> None:
        self._thread = threading.Thread(target=self.run, args=(pipe_main, pipe_data, *args), kwargs=kwargs, name=self.name, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stopped.set()

    def join(self, timeout: Optional[float] = None) -> None:
        if self._thread:
            self._thread.join(timeout)

    def should_stop(self) -> bool:
        return self._stopped.is_set()

    def run(self, pipe_main: InterpPipe, pipe_data: InterpPipe, *args, **kwargs) -> None:  # pragma: no cover
        raise NotImplementedError
