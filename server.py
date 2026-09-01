import socket, threading, json

HOST = "0.0.0.0"
PORT = 5000

clients = {}  
next_id = 1

def send_packet(conn, packet):
    data = json.dumps(packet).encode() + b"\n"
    conn.send(data)

def broadcast(packet):
    data = json.dumps(packet).encode() + b"\n"
    for cid, conn in clients.items():
        try:
            conn.send(data)
        except:
            pass

def send_online_list():
    packet = {
        "type": "online_list",
        "list": list(clients.keys())
    }
    broadcast(packet)

def handle_client(conn, addr):
    global next_id
    client_id = next_id
    next_id += 1
    clients[client_id] = conn

    print(f"[+] Client {client_id} connected from {addr}")

    send_packet(conn, {"type": "assign_id", "id": client_id})
    send_online_list()

    buffer = ""

    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break

            buffer += data.decode()

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue

                packet = json.loads(line)
                to_id = packet.get("to")

                if to_id in clients:
                    send_packet(clients[to_id], packet)

    finally:
        print(f"[-] Client {client_id} disconnected")
        del clients[client_id]
        conn.close()
        send_online_list()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    print(f"[+] Server listening on {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
