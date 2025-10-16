OOP refactor with subinterpreters

- messages.py: typed protocol (Start, Stop, Datagram, Error)
- pipes.py: InterpPipe abstraction + ids export
- worker_base.py: Worker base with lifecycle helpers
- udp_receiver.py: UdpReceiverWorker binding and recv loop
- subinterp.py: bootstrap code executed inside subinterpreter without string exec of business logic
- app.py: App orchestrates subinterp worker and exposes a simple API

Usage example

from oop_subinterp.app import App
app = App(host="127.0.0.1", port=5001)
app.start()
print("status:", app.pipe_main.recv())
msg = app.recv_datagram(timeout=2)
print(msg)
app.stop()
