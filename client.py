import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('127.0.0.1', 2022))
s.listen(10)
while True:
    c, addr = s.accept()  # 一直等待客户端的连接
    # c.recv(1024)
    print("hello")
