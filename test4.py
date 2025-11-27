import socket
import threading

# Configurations
HOST = 'localhost'
TCP_PORT = 6000
UDP_PORT = 6001
INTER_HOST = 'localhost'
INTER_PORT = 5002

tcp_clients = []  # List of TCP client sockets
udp_clients = set()  # Set of UDP client addresses (ip, port)
lock = threading.Lock()  # For thread-safe access

def broadcast_local(message, udp_sock):
    with lock:
        tcp_copy = tcp_clients[:]
        udp_copy = udp_clients.copy()
    for client in tcp_copy:
        try:
            client.send((message + "\n").encode())
        except:
            with lock:
                if client in tcp_clients:
                    tcp_clients.remove(client)
    for addr in udp_copy:
        udp_sock.sendto((message + "\n").encode(), addr)

def handle_tcp_client(client_sock, udp_sock, inter_sock):
    while True:
        try:
            data = client_sock.recv(1024)
            if not data:
                break
            message = data.decode().strip()
            if not message.startswith("JOIN "):
                broadcast_local(message, udp_sock)
                inter_sock.send((message + "\n").encode())
        except:
            break
    with lock:
        if client_sock in tcp_clients:
            tcp_clients.remove(client_sock)
    client_sock.close()

def handle_udp(udp_sock, inter_sock):
    while True:
        data, addr = udp_sock.recvfrom(1024)
        message = data.decode().strip()
        with lock:
            if addr not in udp_clients:
                udp_clients.add(addr)
        if not message.startswith("JOIN "):
            broadcast_local(message, udp_sock)
            inter_sock.send((message + "\n").encode())

def handle_inter(inter_sock, udp_sock):
    while True:
        try:
            data = inter_sock.recv(1024)
            if not data:
                break
            message = data.decode().strip()
            broadcast_local(message, udp_sock)
        except:
            break

# Setup sockets
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.bind((HOST, TCP_PORT))
tcp_sock.listen(5)

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((HOST, UDP_PORT))

# Connect to Server 1's inter-server
inter_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
inter_sock.connect((INTER_HOST, INTER_PORT))
print("Server 2 started. Connected to inter-server.")

# Start threads
threading.Thread(target=handle_inter, args=(inter_sock, udp_sock), daemon=True).start()
threading.Thread(target=handle_udp, args=(udp_sock, inter_sock), daemon=True).start()

# TCP accept loop
while True:
    client_sock, _ = tcp_sock.accept()
    with lock:
        tcp_clients.append(client_sock)
    threading.Thread(target=handle_tcp_client, args=(client_sock, udp_sock, inter_sock), daemon=True).start()