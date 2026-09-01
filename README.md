
# 📦 Secure DM Chat  
### End‑to‑End Encrypted Terminal Messenger

A lightweight, terminal‑based **end‑to‑end encrypted direct messaging system** built with Python.  
Each client can securely establish a private encrypted channel with any other connected client using **X25519 Diffie‑Hellman** and **AES‑GCM**.

The project includes:

- A minimal TCP relay server  
- A fully interactive client with:
  - Arrow‑key user selection menu  
  - Highlight UI  
  - Encrypted DM channels  
  - Colorized terminal output  

---

## 🚀 Features

- 🔐 **End‑to‑End Encryption**
  - X25519 key exchange  
  - HKDF key derivation  
  - AES‑GCM authenticated encryption  

- 👥 **Multiple Clients**
  - Server assigns unique IDs  
  - Clients can choose a peer to chat with  

- 🎨 **Interactive UI**
  - Arrow‑key navigation  
  - Highlighted selection  
  - Colorized messages  

- ⚡ **Fast & Lightweight**
  - No external frameworks  
  - Pure Python + curses  

---

## 📁 Project Structure

---

## 🔧 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourname/secure-chat.git
cd secure-chat
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 🖥️ Running the Server

Start the relay server:

```bash
python3 server.py
```
You should see:
```Code
[+] Server listening on 0.0.0.0:5000
```

## 💬 Running the Client

Open terminal in clients and run:
```bash
python3 client.py
```

Each client receives a unique ID for Example:
```Code
[+] Your ID: 2
```
Then an interactive menu appears:
```Code
Select a client to chat with:
[ 1 ]
  3
  4
```

Use:

- ### **↑ / ↓ to navigate**

- Enter to select a peer

- Once selected, the client performs a secure key exchange and establishes an encrypted channel.

## 🔐 Encryption Details

- ### **Key Exchange**

- X25519 Diffie‑Hellman
- Shared secret derived via HKDF (SHA‑256)

- ### **Message Encryption**

- AES‑GCM (authenticated encryption)
- Random 12‑byte nonce per message
- No plaintext ever touches the server

### **Server Role**

The server never decrypts messages. It only relays encrypted packets based on to and from fields.

## 🧩 How It Works (Architecture)

- ### **Server**

- Assigns client IDs

- Maintains a list of connected clients

- Broadcasts online client list

- Relays packets between clients

- Does not inspect or decrypt messages

- ### **Client**

- Receives ID

- Displays interactive selection menu

- Performs E2E handshake with selected peer

- Encrypts outgoing messages

- Decrypts incoming messages

- Shows colorized output

## 📸 Screenshots (Placeholders)

### Client Selection Menu
```Code
Select a client to chat with:
[ 2 ]
  3
  4
```

### Encrypted Chat
```Code
🔐 Secure channel established with 2
[You → 2] hello
[2] hi there!
```

- ## **🛡️ Security Notes**

- Keys are generated per‑session

- No logs or message history stored

- Server cannot decrypt any message

- AES‑GCM ensures confidentiality + integrity

- X25519 ensures forward secrecy

## 🤝 Contributing

Pull requests are welcome!
- **If you want to add features like:**
- File transfer

- Group chats

- Persistent identities

- GUI version (Tkinter / PyQt)

- WebSocket support

Feel free to open an issue or PR.

## 📄 License

### MIT License
