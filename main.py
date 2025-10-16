import time
import socket
import threading
import textwrap as tw
from concurrent import interpreters
from typing import Callable
from utils import Pipe, PipeConn

from random import randint

sock_addr = ("0.0.0.0", randint(3000, 5000))

def _test_pipes(interp, pipe: PipeConn, message) -> None:
    interp.exec(tw.dedent(f"""
        import workers
        workers.worker_pipe({pipe}, "{message}")
        """))

def _run_recive_peer(interp: interpreters.Interpreter, **kwargs) -> None:
    interp.exec(tw.dedent(f"""
        import workers
        workers.worker_recive_peer(
            {kwargs.get("pipe_main")},
            {kwargs.get("pipe_data")}
        )
        """))

#class SubInterp:
#    def __init__(self) -> None:
#        self.interp = interpreters.create()
#        self.pipe, _ = Pipe()
#        self.thread = None
#
#    def run(self, target: Callable):
#        self.thread = threading.Thread(
#                target=target,
#                args=[self.interp, self.pipe.another_pipe_id],
#                kwargs={
#                    "pipe": self.main_pipe.queue_ids(),
#                    "pipe_data": self.data_pipe.queue_ids(),
#                },
#                )



def main() -> None:
    interp_recive_peer = interpreters.create()
    interp_tun = interpreters.create()

    pipe_recive_peer_main, _= Pipe()
    pipe_recive_peer_data, _= Pipe()

    pipe_tun_main, _= Pipe()
    pipe_tun_data, _= Pipe()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(sock_addr)
    print(sock)

    recive_peer = threading.Thread(
            target=_run_recive_peer, 
            args=(interp_recive_peer,),
            kwargs={
                "pipe_main": pipe_recive_peer_main.another_pipe_id,
                "pipe_data": pipe_recive_peer_data.another_pipe_id,
                },
            daemon=True)


    _worker_data = {
            "is_run": True,
            "sock_fd": (sock.fileno(), sock.family, sock.type),
            }
    pipe_recive_peer_main.send(_worker_data)

    sock.sendto(b"r1", sock_addr)
    sock.sendto(b"r2", sock_addr)
    sock.close()
    #tun = threading.Thread(
    #        target=_run_recive_peer, 
    #        args=(interp_tun,),
    #        kwargs={
    #            "pipe_main": pipe_tun_main.queue_ids(),
    #            "pipe_data": pipe_tun_data.queue_ids(),
    #            },
    #        daemon=True)

    recive_peer.start()
    recive_peer.join()
    #tun.start()
    #tun.join()

if __name__ == "__main__":
    main()
