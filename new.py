from oop_subinterp import App
import socket, time

app = App(host='127.0.0.1', port=5556)
app.start()

print('MAIN STATUS:', app.peer_pipe_main.recv(timeout=3))


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b'test', ('127.0.0.1', 5556))
time.sleep(0.3)
msg = app.recv_datagram(timeout=1)
print('DATAGRAM:', msg)
app.stop()
print('STOP STATUS:', app.peer_pipe_data.recv(timeout=3))
