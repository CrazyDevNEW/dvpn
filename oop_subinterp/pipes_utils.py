from __future__ import annotations
import queue
from typing import Any, Optional, Protocol, Tuple
from dataclasses import dataclass
from concurrent import interpreters


class IPipe(Protocol):
    def send(self, obj: Any) -> None: ...
    def recv(self, timeout: Optional[float] = None) -> Any: ...
    def close(self) -> None: ...


class InterpPipe:
    def __init__(self, q_in: interpreters.Queue, q_out: interpreters.Queue) -> None:
        self._in = q_in
        self._out = q_out
        self._closed = False

    @classmethod
    def pair(cls, maxsize: int = 0) -> tuple[InterpPipe, InterpPipe]:
        q1 = interpreters.create_queue(maxsize=maxsize)
        q2 = interpreters.create_queue(maxsize=maxsize)
        return cls(q1, q2), cls(q2, q1)

    @classmethod
    def from_ids(cls, in_id: int, out_id: int) -> InterpPipe:
        return cls(interpreters.Queue(in_id), interpreters.Queue(out_id))

    @property
    def ids(self) -> tuple[int, int]:
        return self._in.id, self._out.id

    def send(self, obj: Any) -> None:
        if self._closed:
            raise RuntimeError("pipe closed")
        self._out.put(obj)

    def recv(self, timeout: Optional[int] = None) -> Any:
        try:
            return self._in.get(timeout=timeout)
        except queue.Empty:
            raise

    def close(self) -> None:
        self._closed = True


def export_ids(pipe: InterpPipe) -> tuple[int, int]:
    return pipe.ids


@dataclass(frozen=True)
class Start:
    host: str
    port: int


@dataclass(frozen=True)
class Stop:
    pass


@dataclass(frozen=True)
class Event:
    status: str
    

@dataclass(frozen=True)
class Datagram:
    data: bytes
    addr: Tuple[str, int]


@dataclass(frozen=True)
class Error:
    message: str
    details: str | None = None
