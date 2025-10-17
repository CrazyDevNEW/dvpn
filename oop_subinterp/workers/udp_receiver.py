import socket
from .worker_base import Worker
from .messages import Start, Stop, Datagram, Error
from .pipes import InterpPipe


class UdpReceiverWorker(Worker):
    def __init__(self) -> None:
        super().__init__(name="udp-recv")

    def run(self, pipe_main: InterpPipe, pipe_data: InterpPipe) -> None:
        cfg = pipe_main.recv()
        if isinstance(cfg, Stop):
            return
        if not isinstance(cfg, Start):
            pipe_main.send(Error("Invalid start message"))
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.bind((cfg.host, cfg.port))
            pipe_main.send({"status": "bound", "addr": sock.getsockname()})
            sock.settimeout(0.3)
            while True:
                # Check for Stop on control pipe (non-blocking)
                try:
                    ctrl = pipe_main.recv(timeout=0)
                    if isinstance(ctrl, Stop):
                        break
                except Exception:
                    pass
                try:
                    data, addr = sock.recvfrom(65507)
                    pipe_data.send(Datagram(data=data, addr=addr))
                except TimeoutError:
                    pass
                except OSError as e:
                    pipe_main.send(Error(str(e)))
                    break
        finally:
            try:
                sock.close()
            except Exception:
                pass
            pipe_main.send({"status": "stopped"})
