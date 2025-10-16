from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


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
