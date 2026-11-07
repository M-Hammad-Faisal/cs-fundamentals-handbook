# Sockets Lab: TCP and UDP from Scratch

**Prerequisites:** [packets, addressing and subnets](01-packets-addressing-and-subnets.md), [processes and threads](../../06-operating-systems/processes-threads/01-processes-in-practice.md) (threads), [file descriptors](../../06-operating-systems/file-systems-io/01-file-systems-in-depth.md). **You will learn (by running everything on `localhost`):** what a **socket** is, how a **TCP server and client** work step by step, why TCP is a **byte stream** with no message boundaries (and how to add **framing**), how to serve **many clients** (threads), how **UDP** differs (datagrams can be lost and reordered), **timeouts**, and the TCP **connection states**.

## 1. In plain words

A **socket** is the operating system's handle for one end of a network conversation: "a phone you can talk into". Your program creates a socket, the OS speaks the TCP/IP protocols behind it, and you just `send` and `recv` bytes. Like files, sockets are **file descriptors**.

Two flavors:

- **`SOCK_STREAM` (TCP):** a reliable, ordered **stream of bytes** between two connected sockets (like a phone call).
- **`SOCK_DGRAM` (UDP):** independent **datagrams**, no connection, no delivery guarantee (like postcards).

## 2. The TCP server and client sequence

```text
SERVER                          CLIENT
socket()                        socket()
bind(address, port)
listen()
accept()   <---- handshake ----  connect(server address, port)
recv()     <----- data -------   send()
send()     ------ data ------>   recv()
close()                         close()
```

`listen()` puts the socket into "waiting for callers" mode; **`accept()` returns a brand-new socket for each caller**, while the original keeps listening.

## 3. Lab 1: an echo server and client

We run the server in a background thread so the whole demo is one script. Port `0` asks the OS for any free port.

```python
import socket, threading

def echo_server(ready, stop):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # allow quick restarts on the same port
        server.bind(("127.0.0.1", 0))
        server.listen()
        ready.append(server.getsockname()[1])                           # tell the main thread which port we got
        server.settimeout(0.2)
        while not stop.is_set():
            try:
                conn, addr = server.accept()                            # blocks until a client connects
            except socket.timeout:
                continue
            with conn:
                while data := conn.recv(1024):                          # b"" means the client closed the connection
                    conn.sendall(data.upper())                          # "echo" in upper case

ready, stop = [], threading.Event()
thread = threading.Thread(target=echo_server, args=(ready, stop)); thread.start()
while not ready: pass
PORT = ready[0]

with socket.create_connection(("127.0.0.1", PORT)) as client:
    client.sendall(b"hello network")
    print(client.recv(1024))                                            # b'HELLO NETWORK'
    client.sendall(b"second message")
    print(client.recv(1024))                                            # b'SECOND MESSAGE'
    print(client.getsockname()[0], client.getpeername() == ("127.0.0.1", PORT))       # 127.0.0.1 True
```

Things to notice:

- `sendall` loops until **every** byte has been handed to the OS (plain `send` may send only part).
- `recv(1024)` returns **up to** 1024 bytes, possibly fewer; `b""` means the peer closed.
- The client's source port is **ephemeral** (chosen by the OS) and the 5-tuple identifies the connection.

## 4. TCP is a stream: message boundaries do not exist

If you `send` "AAA" then "BBB", the receiver may `recv` `b"AAABBB"` in one call, or `b"AA"` and then `b"ABBB"`. TCP promises **order and completeness**, not **boundaries**. The classic beginner bug is assuming one `send` equals one `recv`.

```python
def stream_demo():
    server_sock = socket.socket(); server_sock.bind(("127.0.0.1", 0)); server_sock.listen()
    port = server_sock.getsockname()[1]
    client = socket.create_connection(("127.0.0.1", port))
    conn, _ = server_sock.accept()
    for chunk in (b"AAA", b"BBB", b"CCC"):
        client.sendall(chunk)                               # three separate sends...
    client.shutdown(socket.SHUT_WR)                         # tell the peer "I am done sending"
    received = b""
    while data := conn.recv(100):
        received += data
    client.close(); conn.close(); server_sock.close()
    return received

print(stream_demo())                                         # b'AAABBBCCC'   (one blob: the three sends merged)
```

### Fix: framing

You must mark where messages end. The three standard ways:

1. **Fixed length** messages.
2. A **delimiter** (HTTP headers end with a blank line; Redis uses `\r\n`).
3. A **length prefix**: send the size first, then the data (most robust; used by many binary protocols).

```python
import struct

def send_message(sock, payload: bytes):
    sock.sendall(struct.pack("!I", len(payload)) + payload)          # 4-byte big-endian length, then the bytes

def recv_exactly(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("connection closed mid-message")
        buf += chunk
    return buf

def recv_message(sock):
    (length,) = struct.unpack("!I", recv_exactly(sock, 4))
    return recv_exactly(sock, length)

a, b = socket.socketpair()                                           # two connected stream sockets in one process
for text in (b"first", b"", b"third message is longer"):
    send_message(a, text)
print([recv_message(b) for _ in range(3)])                          # [b'first', b'', b'third message is longer']
a.close(); b.close()
```

## 5. Lab 2: a chat-style server for many clients (threads)

A server must keep `accept`ing while talking to existing clients. The simplest approach is **one thread per connection**. (For thousands of connections use [`asyncio` or `selectors`](../../06-operating-systems/file-systems-io/01-file-systems-in-depth.md).)

```python
import threading, socket

class ChatServer:
    def __init__(self):
        self.server = socket.socket()
        self.server.bind(("127.0.0.1", 0)); self.server.listen()
        self.port = self.server.getsockname()[1]
        self.clients, self.lock = [], threading.Lock()
        self.running = True
        threading.Thread(target=self.accept_loop, daemon=True).start()

    def accept_loop(self):
        while self.running:
            try:
                conn, _ = self.server.accept()
            except OSError:
                return                                              # the server socket was closed
            with self.lock:
                self.clients.append(conn)
            threading.Thread(target=self.serve, args=(conn,), daemon=True).start()

    def serve(self, conn):
        try:
            while line := conn.recv(1024):
                with self.lock:
                    for other in list(self.clients):
                        if other is not conn:
                            other.sendall(line)                     # broadcast to everyone else
        except OSError:
            pass
        finally:
            with self.lock:
                if conn in self.clients:
                    self.clients.remove(conn)
            conn.close()

    def close(self):
        self.running = False
        self.server.close()
        with self.lock:
            for c in self.clients: c.close()

chat = ChatServer()
alice = socket.create_connection(("127.0.0.1", chat.port))
bob = socket.create_connection(("127.0.0.1", chat.port))
carol = socket.create_connection(("127.0.0.1", chat.port))
import time; time.sleep(0.1)                                         # let the server register all three
alice.sendall(b"hi from alice")
bob.settimeout(1); carol.settimeout(1)
print(bob.recv(100), carol.recv(100))                               # b'hi from alice' b'hi from alice'
alice.settimeout(0.2)
try:
    alice.recv(100)
except socket.timeout:
    print("alice does not receive her own message")                # alice does not receive her own message
for s in (alice, bob, carol): s.close()
chat.close()
```

The lock protects the shared `clients` list from the races described in [synchronization](../../06-operating-systems/concurrency-deadlocks/01-race-conditions-and-synchronization.md).

## 6. Lab 3: UDP

UDP has no `listen`/`accept`/`connect`: a socket just `sendto`s and `recvfrom`s datagrams. Each `recvfrom` returns exactly **one datagram** (message boundaries are preserved, unlike TCP).

```python
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("127.0.0.1", 0))
udp_port = server.getsockname()[1]

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for msg in (b"one", b"two", b"three"):
    client.sendto(msg, ("127.0.0.1", udp_port))                      # no connection, no handshake

server.settimeout(1)
received = []
for _ in range(3):
    data, sender = server.recvfrom(1024)
    received.append(data)
print(received)                                                      # [b'one', b'two', b'three']   (boundaries preserved)

server.sendto(b"reply", sender)                                       # answer the sender's address and port
client.settimeout(1)
print(client.recvfrom(1024)[0])                                      # b'reply'
```

On loopback UDP is reliable in practice; **on real networks datagrams can be lost, duplicated or reordered**, and the sender is never told. We can simulate loss to see why protocols built on UDP add their own acknowledgements:

```python
import random

def unreliable_send(sock, data, addr, loss_rate, rng):
    if rng.random() >= loss_rate:                                    # drop some packets "in the network"
        sock.sendto(data, addr)

rng = random.Random(3)
server2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); server2.bind(("127.0.0.1", 0))
addr = server2.getsockname()
sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_with_retries(seq):                                           # a tiny "stop-and-wait" reliability protocol
    attempts = 0
    while True:
        attempts += 1
        unreliable_send(sender, f"{seq}".encode(), addr, 0.5, rng)
        server2.settimeout(0.05)
        try:
            data, _ = server2.recvfrom(100)                           # the receiver got it...
        except socket.timeout:
            continue                                                  # ...or not: no packet arrived, so retry
        return attempts

attempts = [send_with_retries(i) for i in range(10)]
print(sum(attempts) > 10, max(attempts) > 1)                         # True True   (with 50% loss, many messages needed retries)
```

This is the essence of what TCP does for you (sequence numbers, acknowledgements, retransmission timers, plus congestion control) and what **QUIC** (HTTP/3) re-implements on top of UDP.

| Use UDP when | Use TCP when |
|--------------|--------------|
| Latency matters more than perfection: voice/video, games, live telemetry | Every byte must arrive in order: web pages, files, databases, email |
| Small request/response: DNS | Long-lived conversations |
| You are building your own protocol (QUIC) | You want the OS to handle reliability and congestion |

## 7. Timeouts and error handling

Network calls **block forever** by default. Always set timeouts and handle failures: connections get refused, reset, or stall.

```python
# connect to a port nobody listens on
dead = socket.socket(); dead.bind(("127.0.0.1", 0)); free_port = dead.getsockname()[1]; dead.close()
try:
    socket.create_connection(("127.0.0.1", free_port), timeout=1)
except ConnectionRefusedError as e:
    print("refused:", e.errno is not None)                           # refused: True   (nobody is listening on that port)

# a read that never completes
a, b = socket.socketpair()
a.settimeout(0.1)
try:
    a.recv(10)                                                       # the other end never sends
except socket.timeout:
    print("timed out waiting for data")                              # timed out waiting for data
a.close(); b.close()

# a peer that closes the connection yields b"" from recv
a, b = socket.socketpair(); b.close()
print(a.recv(10))                                                    # b''   (end of stream: the peer closed cleanly)
a.close()

# a name that does not resolve
try:
    socket.getaddrinfo("this-name-does-not-exist.invalid", 80)
except socket.gaierror:
    print("name resolution failed")                                  # name resolution failed
```

Rules: set a timeout on connect **and** on reads; **retry with exponential back-off** for transient errors; close sockets with `with`; treat `b""` from `recv` as end of stream; never assume a single `recv` returns a whole message.

## 8. TCP connection states (what `netstat`/`ss` shows)

```text
 client                                          server
 CLOSED                                          LISTEN
 SYN_SENT    ----- SYN ---------------------->   SYN_RECEIVED
 ESTABLISHED <---- SYN, ACK ------------------
             ----- ACK ---------------------->   ESTABLISHED
             ... data both ways ...
 FIN_WAIT_1  ----- FIN ---------------------->   CLOSE_WAIT
 FIN_WAIT_2  <---- ACK ------------------------
 TIME_WAIT   <---- FIN ------------------------  LAST_ACK
             ----- ACK ---------------------->   CLOSED
 (waits about 60 s, then CLOSED)
```

- **`TIME_WAIT`:** the side that closes first lingers for about a minute so late packets from the old connection cannot be mistaken for a new one. Thousands of short connections can pile up in `TIME_WAIT`: reuse connections (HTTP keep-alive, connection pools).
- **`SO_REUSEADDR`** lets a restarted server bind its port while old connections linger.

```bash
ss -tan state established     # Linux: list established TCP connections
netstat -an | grep LISTEN     # macOS/Linux: which ports are in LISTEN state
lsof -i :8080                 # which process owns a port
```

## 9. Socket options worth knowing

```python
s = socket.socket()
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)             # disable Nagle's algorithm: send small writes immediately (low latency)
s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)             # probe idle connections to detect dead peers
print(s.getsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY) != 0)    # True
print(s.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) > 0)        # True   (kernel receive buffer size in bytes)
s.close()
```

**Nagle's algorithm** batches tiny writes to save packets; for request/response protocols with small messages (interactive, RPC) enable `TCP_NODELAY`.

## 10. Wrapping up: stop the echo server

```python
stop.set(); thread.join()
print("echo server stopped:", not thread.is_alive())                # echo server stopped: True
```

## 11. Two real-world examples

**Example 1: Redis and databases.** `redis-cli` opens a TCP socket to port 6379 and sends text commands like `PING\r\n` (delimiter framing); PostgreSQL uses length-prefixed binary messages. Both rely on the stream-and-framing pattern from this lab, and on connection pools to avoid the cost of repeated handshakes.

**Example 2: Online games and video calls.** Position updates in a game are sent over UDP many times per second: if one packet is lost, the next one makes it obsolete, so waiting for retransmission (TCP) would only add lag. WebRTC calls and QUIC follow the same philosophy.

## 12. Common mistakes

- Assuming one `send` equals one `recv` (no message boundaries in TCP).
- Using `send` and ignoring the return value instead of `sendall`.
- No timeouts: one dead peer hangs the program forever.
- Treating `recv() == b""` as "no data yet" (it means the peer closed).
- Binding to `0.0.0.0` accidentally (exposes the service to the whole network); use `127.0.0.1` for local-only.
- Forgetting to close sockets (file descriptor leak: `Too many open files`).
- Not using `SO_REUSEADDR` and getting `Address already in use` after restarts.
- Assuming UDP messages arrive, arrive once, or arrive in order.

## 13. Practice

1. What does `accept()` return, and why a new socket?
2. Send the three messages `"a"`, `"bc"`, `"def"` with the length-prefix helpers and receive them back.
3. Why might `recv(1024)` return only 10 bytes when the peer sent 100?
4. Write a client that connects to the echo server (use `PORT` if it is still running, otherwise start your own), sends a line and prints the response. (Hint: reuse the lab code.)
5. What changes in the chat server if you want a username for each client? (Describe, do not code.)
6. Why is `TIME_WAIT` useful, and what practice avoids piling up connections in that state?
7. Which transport would you use for: (a) file download, (b) DNS lookup, (c) live video, (d) bank transfer API?

<details>
<summary>Solutions</summary>

1. A new connected socket dedicated to that client; the listening socket stays free to accept more callers.
2. ```python
   a, b = socket.socketpair()
   for m in (b"a", b"bc", b"def"):
       send_message(a, m)
   print([recv_message(b) for _ in range(3)])                         # [b'a', b'bc', b'def']
   a.close(); b.close()
   ```
3. TCP delivers a stream; the kernel hands over whatever has arrived so far (up to the size you asked for). Loop until you have the full message.
4. ```python
   stop2, ready2 = threading.Event(), []
   t2 = threading.Thread(target=echo_server, args=(ready2, stop2)); t2.start()
   while not ready2: pass
   with socket.create_connection(("127.0.0.1", ready2[0])) as c:
       c.sendall(b"ping"); print(c.recv(100))                        # b'PING'
   stop2.set(); t2.join()
   ```
5. Define a first-message protocol (for example `NAME alice\n`), store a `{socket: name}` dict instead of a list, and prefix broadcasts with the sender's name; frame messages by lines.
6. It prevents delayed packets of a closed connection from corrupting a new one that reuses the same 5-tuple. Reuse connections (keep-alive, pools) so you open far fewer.
7. (a) TCP, (b) UDP, (c) UDP (or QUIC/WebRTC), (d) TCP (reliability and TLS).

</details>

## 14. Check yourself

1. List the server-side socket calls for TCP in order.
2. Why does TCP need framing in your protocol?
3. What does `recv` returning `b""` mean?
4. How do UDP datagrams differ from TCP data on the receiving side?
5. Why set timeouts on every network call?
6. What does `TCP_NODELAY` do?

<details>
<summary>Answers</summary>

1. `socket`, `bind`, `listen`, `accept`, then `recv`/`send`, and `close`.
2. TCP delivers a byte stream without message boundaries, so the protocol must mark where messages end (fixed size, delimiter or length prefix).
3. The peer closed the connection (end of stream).
4. Each `recvfrom` returns one whole datagram (boundaries preserved), but datagrams may be lost, duplicated or reordered.
5. Otherwise a stalled or dead peer blocks the program indefinitely.
6. Disables Nagle's algorithm so small writes are sent immediately, lowering latency.

</details>

[Back to TCP/IP and OSI](README.md) · Previous: [packets, addressing and subnets](01-packets-addressing-and-subnets.md)
