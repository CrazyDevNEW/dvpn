import queue
from typing import Optional
from concurrent import interpreters


class PipeConn:
    def __init__(self, q_input: interpreters.Queue, q_output:interpreters.Queue) -> None:
        self.q_input = q_input
        self.q_output = q_output

    def recv(self, timeout: Optional[int] = None):
        try:
            return self.q_input.get(timeout=timeout)
        except queue.Empty:
            raise queue.Empty

    def send(self, item):
        return self.q_output.put(item)
    
    @property
    def this_pipe_id(self) -> tuple[int, int]:
        return self.q_output.id, self.q_input.id

    @property
    def another_pipe_id(self) -> tuple[int, int]:
        return (self.q_input.id, self.q_output.id)
    
    def empty(self):
        return self.q_input.empty()


class Pipe:
    def __new__(cls, queue_ids: Optional[tuple[int, int]] = None, maxsize: int = 0) -> tuple[PipeConn, PipeConn]:
        if queue_ids is None:
            q1 = interpreters.create_queue(maxsize=maxsize)
            q2 = interpreters.create_queue(maxsize=maxsize)
            return PipeConn(q1, q2), PipeConn(q2, q1)
        elif isinstance(queue_ids, tuple):
            q1 = interpreters.Queue(queue_ids[1])
            q2 = interpreters.Queue(queue_ids[0])
            return PipeConn(q1, q2), PipeConn(q2, q1)

