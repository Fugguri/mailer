import socket
from select import selectors


selector = selectors.DefaultSelector()


def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(("localhost", 5000))
    server_socket.listen()

    selector.register(fileonj=server_socket,
                      events=selectors.EVENT_READ, data=accept_connection)


def accept_connection(server_socket):
    client_socket, addr = server_socket.accept()
    print(f"Connection from", addr)
    selector.register(fileonj=client_socket,
                      events=selectors.EVENT_READ, data=send_message)


def send_message(client_socket):
    request = client_socket.recv(4069)
    if request:
        response = "HEllo world\n".encode()
        client_socket.send(response)
    else:
        selector.unregister(client_socket)
        client_socket.close()


def event_loop():
    print("start loop")
    server()
    while True:
        events = selector.select()
        for key, _ in events:
            callback = key.data
            callback(key.fileobj)


if __name__ == '__main__':

    event_loop()
