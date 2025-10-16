import socket
from typing import Any
from utils import Pipe


def worker_pipe(pipe: tuple[int, int], message) -> None:
    my_pipe, _ = Pipe(pipe)
    my_pipe.send(message)
    print(my_pipe.recv())


def worker_recive_peer(pipe_ids: tuple[int, int]) -> None:
    pipe, _ = Pipe(pipe_ids)
    worker_data : dict[str, Any] = main_p.recv() # type: ignore
    __workder_data = ["is_run"]
    if worker_data.keys() in __workder_data:
         is_run = True

    sock = socket.fromfd(*worker_data["sock_fd"])

    pipe.send(sock.recvfrom(65507))
