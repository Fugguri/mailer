import socket

# domain:5000(port)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("localhost", 5000))
server_socket.listen()


while True:
    print("Before .accept()")
    client_socket, addr = server_socket.accept()
    print(f"Connection from", addr)

    while True:
        print("Before .recv()")
        request = client_socket.recv(4069)

        if not request:
            break
        else:
            response = "HEllo world\n".encode()
            client_socket.send(response)

    print("outside while loop")
    client_socket.close()
