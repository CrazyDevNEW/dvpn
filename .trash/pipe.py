import os
import threading
import textwrap as tw
from concurrent import interpreters

BUF_SIZE = 64


def _write_allv(fd: int, parts: list[bytes]) -> None:
    views = [memoryview(p) for p in parts if p]
    while views:
        n = os.writev(fd, views)
        wrote = n
        i = 0
        while i < len(views) and wrote >= len(views[i]):
            wrote -= len(views[i])
            i += 1
        views = views[i:]
        if views and wrote:
            views[0] = views[0][wrote:]


def _run_in_subinterpreter(interp, r_fd: int, w_fd: int, bufsize: int) -> None:
    interp.exec(tw.dedent(f"""
        import os
        r_fd={r_fd}; w_fd={w_fd}; bufsize={bufsize}
        try:
            buf = bytearray(bufsize)
            n = os.readv(r_fd, [buf])
            print(buf[:n].decode())
            os.close(r_fd)
            os.writev(w_fd, [b'World Hello'])
        finally:
            try: os.close(w_fd)
            except OSError: pass
        """))


def main() -> None:
    interp = interpreters.create()
    r1, s1 = os.pipe()
    r2, s2 = os.pipe()

    t = threading.Thread(
        target=_run_in_subinterpreter, args=(interp, r1, s2, BUF_SIZE), daemon=True
    )
    t.start()

    try:
        print('before')
        _write_allv(s1, [b'Hello ', b'World', b'World', b'World', b'World', b'World', b'World', b'World'])
        os.close(s1)  # signal EOF to reader
        print('during A')

        buf = bytearray(BUF_SIZE)
        n = os.readv(r2, [buf])
        print(buf[:n].decode())
        print('after')
    finally:
        for fd in (r1, s1, r2, s2):
            try:
                os.close(fd)
            except OSError:
                pass
        t.join(timeout=5)


if __name__ == '__main__':
    main()
