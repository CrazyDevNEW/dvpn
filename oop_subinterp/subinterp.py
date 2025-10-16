import textwrap as tw
from concurrent import interpreters  # type: ignore
from .pipes import InterpPipe


BOOTSTRAP = tw.dedent(
    """
    import importlib
    import interpreters
    from oop_subinterp.pipes import InterpPipe

    def main(module_name: str, class_name: str, pipe_main_ids: tuple[int,int], pipe_data_ids: tuple[int,int]):
        mod = importlib.import_module(module_name)
        cls = getattr(mod, class_name)
        pipe_main = InterpPipe.from_ids(*pipe_main_ids)
        pipe_data = InterpPipe.from_ids(*pipe_data_ids)
        worker = cls()
        worker.run(pipe_main, pipe_data)
    """
)


class SubInterpreterWorker:
    def __init__(self, module_name: str, class_name: str, pipe_main: InterpPipe, pipe_data: InterpPipe) -> None:
        self._module_name = module_name
        self._class_name = class_name
        self._pipe_main = pipe_main
        self._pipe_data = pipe_data
        self._interp = interpreters.create()

    def start(self) -> None:
        code = tw.dedent(f"""
        import importlib
        from oop_subinterp.pipes import InterpPipe
        mod = importlib.import_module({self._module_name!r})
        cls = getattr(mod, {self._class_name!r})
        pipe_main = InterpPipe.from_ids(*{self._pipe_main.ids!r})
        pipe_data = InterpPipe.from_ids(*{self._pipe_data.ids!r})
        worker = cls()
        worker.run(pipe_main, pipe_data)
        """)
        self._interp.exec(code)

    def close(self) -> None:
        try:
            self._interp.close()
        except Exception:
            pass
