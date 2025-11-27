import socket
import threading
import sys

# Configurations
HOST = 'localhost'
SERVER1_TCP_PORT = 5000
SERVER1_UDP_PORT = 5001
SERVER2_TCP_PORT = 6000
SERVER2_UDP_PORT = 6001

def receive_tcp(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print(data.decode().strip())
        except:
            break
    print("TCP connection closed.")
    sys.exit(0)

def receive_udp(sock):
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            print(data.decode().strip())
        except:
            break
    print("UDP reception stopped.")
    sys.exit(0)

# Startup inputs
username = input("Enter username: ")
protocol = input("Enter protocol (tcp/udp): ").lower()
selection_mode = input("Enter server selection mode (manual/roundrobin): ").lower()

if selection_mode == "manual":
    server_num = int(input("Enter server (1/2): "))
elif selection_mode == "roundrobin":
    user_id = int(input("Enter user ID (e.g., 1-4): "))
    server_num = (user_id - 1) % 2 + 1
    print(f"Assigned to server {server_num} via round-robin.")
else:
    print("Invalid selection mode.")
    sys.exit(1)

if server_num == 1:
    tcp_port = SERVER1_TCP_PORT
    udp_port = SERVER1_UDP_PORT
elif server_num == 2:
    tcp_port = SERVER2_TCP_PORT
    udp_port = SERVER2_UDP_PORT
else:
    print("Invalid server.")
    sys.exit(1)

server_addr = (HOST, tcp_port) if protocol == "tcp" else (HOST, udp_port)

if protocol == "tcp":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_addr)
    sock.send(("JOIN " + username + "\n").encode())
    threading.Thread(target=receive_tcp, args=(sock,), daemon=True).start()
    print("Connected to server via TCP. Enter messages:")
    while True:
        message = input("")
        if message:
            sock.send((username + ": " + message + "\n").encode())
elif protocol == "udp":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, 0))  # Random port for receiving
    sock.sendto(("JOIN " + username + "\n").encode(), server_addr)
    threading.Thread(target=receive_udp, args=(sock,), daemon=True).start()
    print("Registered with server via UDP. Enter messages:")
    while True:
        message = input("")
        if message:
            sock.sendto((username + ": " + message + "\n").encode(), server_addr)
else:
    print("Invalid protocol.")
    sys.exit(1)