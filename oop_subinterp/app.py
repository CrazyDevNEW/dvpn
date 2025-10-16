from typing import Optional
from .pipes import InterpPipe
from .messages import Start, Stop, Datagram
from .subinterp import SubInterpreterWorker


class App:
    def __init__(self, host: str = "127.0.0.1", port: int = 4000) -> None:
        self.host = host
        self.port = port
        self.peer_pipe_main, self.peer_pipe_main_worker = InterpPipe.pair()
        self.peer_pipe_data, self.peer_pipe_data_worker = InterpPipe.pair()
        self.worker = SubInterpreterWorker(
            module_name="oop_subinterp.udp_receiver",
            class_name="UdpReceiverWorker",
            pipe_main=self.peer_pipe_main_worker,
            pipe_data=self.peer_pipe_data_worker,
        )

    def start(self) -> None:
        self.worker.start()
        self.peer_pipe_main.send(Start(self.host, self.port))

    def stop(self) -> None:
        self.peer_pipe_main.send(Stop())
        self.worker.close()

    #def recv_datagram(self, timeout: Optional[int] = 1) -> Optional[Datagram]:
    #    try:
    #        msg = self.peer_pipe_data.recv(timeout=timeout)
    #        if isinstance(msg, Datagram):
    #            return msg
    #        return None
    #    except Exception:
    #        return None
