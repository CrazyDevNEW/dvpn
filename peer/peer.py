import socket
from typing import Optional


class PeerControl:
    def __init__(self) -> None:
        self.sock = None
        self.peer_id = None
        self.DADDR2ID: dict[tuple[str, int], str] = {}
        self.ID2DADDR: dict[str, tuple[str, int]] = {}
