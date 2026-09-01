import socket
import threading
import json
import os
import time
import curses
from curses import wrapper
from colorama import Fore, Style, init

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization

init(autoreset=True)

HOST = "127.0.0.1"
PORT = 5000

private_key = x25519.X25519PrivateKey.generate()
public_key = private_key.public_key()
my_id = None
session_keys = {}
pending_handshake = {}
online_clients = []
selected_peer = None
buffer = ""

def derive_key(shared_secret: bytes) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"dm-chat-e2e",
    )
    return hkdf.derive(shared_secret)

def encrypt_for(peer_id, msg):
    aes = session_keys.get(peer_id)
    if aes is None:
        return None

    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, msg.encode(), None)

    return {
        "type": "msg",
        "from": my_id,
        "to": peer_id,
        "nonce": nonce.hex(),
        "ct": ct.hex()
    }

def decrypt_packet(packet):
    global session_keys, online_clients

    if packet["type"] == "pubkey":
        peer_id = packet["from"]
        peer_pub_bytes = bytes.fromhex(packet["pub"])
        peer_pub = x25519.X25519PublicKey.from_public_bytes(peer_pub_bytes)

        shared = private_key.exchange(peer_pub)
        key = derive_key(shared)
        session_keys[peer_id] = AESGCM(key)

        print(Fore.GREEN + f"\n🔐 Secure channel established with {peer_id}")
        print("> ", end="", flush=True)
        return

    if packet["type"] == "msg":
        peer_id = packet["from"]
        aes = session_keys.get(peer_id)
        if aes is None:
            print(Fore.RED + f"\n[!] Message from {peer_id} but no key!")
            return

        nonce = bytes.fromhex(packet["nonce"])
        ct = bytes.fromhex(packet["ct"])
        msg = aes.decrypt(nonce, ct, None).decode()

        print(Fore.CYAN + f"\n[{peer_id}] {msg}")
        print("> ", end="", flush=True)
        return

    if packet["type"] == "online_list":
        online_clients = [cid for cid in packet["list"] if cid != my_id]
        return


def send_pubkey(sock, peer_id):
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    pending_handshake[peer_id] = pub_bytes

    packet = {
        "type": "pubkey",
        "from": my_id,
        "to": peer_id,
        "pub": pub_bytes.hex()
    }
    sock.send((json.dumps(packet) + "\n").encode())

def receiver(sock):
    global my_id, online_clients, buffer

    while True:
        try:
            data = sock.recv(4096)
            if not data:
                print(Fore.RED + "\n[!] Disconnected from server")
                break

            buffer += data.decode()

            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue

                try:
                    packet = json.loads(line)
                except Exception as e:
                    print(Fore.RED + f"[!] JSON error: {e}")
                    continue

                if packet["type"] == "assign_id":
                    my_id = packet["id"]
                    print(Fore.YELLOW + f"[+] Your ID: {my_id}")
                    print("> ", end="", flush=True)
                    continue

                decrypt_packet(packet)

        except Exception as e:
            print(Fore.RED + f"[!] Error: {e}")
            break

def client_selector(stdscr):
    global selected_peer
    curses.curs_set(0)
    stdscr.clear()
    selected_peer = online_clients[0] if online_clients else None
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Select a client to chat with:", curses.A_BOLD)

        for idx, cid in enumerate(online_clients):
            if cid == selected_peer:
                stdscr.addstr(idx + 2, 0, f"[ {cid} ]", curses.A_REVERSE)
            else:
                stdscr.addstr(idx + 2, 0, f"  {cid}  ")

        key = stdscr.getch()

        if key == curses.KEY_UP:
            pos = online_clients.index(selected_peer)
            selected_peer = online_clients[max(0, pos - 1)]

        elif key == curses.KEY_DOWN:
            pos = online_clients.index(selected_peer)
            selected_peer = online_clients[min(len(online_clients) - 1, pos + 1)]

        elif key in [10, 13]:  
            return selected_peer

        stdscr.refresh()

def main():
    global selected_peer

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    threading.Thread(target=receiver, args=(sock,), daemon=True).start()

    print(Fore.MAGENTA + "Waiting for online client list...")

    while not online_clients:
        time.sleep(0.1)
    chosen = wrapper(client_selector)
    print(Fore.YELLOW + f"\n[*] Selected peer: {chosen}")
    send_pubkey(sock, chosen)
    while True:
        text = input("> ").strip()
        if not text:
            continue
        packet = encrypt_for(chosen, text)
        if packet is None:
            print(Fore.RED + "[!] No secure channel yet!")
            continue

        sock.send((json.dumps(packet) + "\n").encode())
        print(Fore.GREEN + f"[You → {chosen}] {text}")

if __name__ == "__main__":
    main()
