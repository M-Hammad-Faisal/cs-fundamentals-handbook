# The Network Stack: OSI, TCP/IP, IP Addressing, TCP and UDP

## Detailed lessons (start here if you are new)

1. [Packets, addressing and subnets](01-packets-addressing-and-subnets.md): build real IP/UDP/TCP headers, checksums, CIDR, subnetting, routing
2. [Sockets lab: TCP and UDP](02-sockets-tcp-udp-lab.md): echo and chat servers, framing, UDP loss, timeouts, connection states

The rest of this page is the quick reference.

## 1. The concept

Network communication is split into **layers**, each solving one problem and hiding its details from the layer above. A layer on the sender wraps the data from the layer above in its own header (**encapsulation**); the receiver unwraps in reverse.

| OSI layer | TCP/IP layer | Job | Examples | Unit |
|-----------|--------------|-----|----------|------|
| 7 Application | Application | What the app says | HTTP, DNS, SMTP, SSH | message |
| 6 Presentation | | Encoding, encryption | TLS, JSON | |
| 5 Session | | Dialog management | | |
| 4 Transport | Transport | Process-to-process delivery | **TCP, UDP**, QUIC | segment / datagram |
| 3 Network | Internet | Host-to-host routing | **IP**, ICMP | packet |
| 2 Data link | Link | Neighbor-to-neighbor on one network | Ethernet, Wi-Fi, ARP | frame |
| 1 Physical | | Bits on a medium | cable, radio | bit |

The 4-layer TCP/IP model is what the internet really uses; the 7-layer OSI model is the common teaching vocabulary ("a layer 7 load balancer").

```text
HTTP request  ->  [TCP hdr | HTTP data]  ->  [IP hdr | TCP hdr | HTTP data]  ->  [Eth hdr | IP | TCP | data | trailer]
```

## 2. IP addressing and routing

An **IPv4** address is 32 bits (`192.168.10.40`); **IPv6** is 128 bits. **CIDR** notation `192.168.10.0/26` means the first 26 bits identify the **network** and the rest identify the host.

```python
import ipaddress

net = ipaddress.ip_network("192.168.10.0/26")
print(net.netmask, net.num_addresses, net.num_addresses - 2, net.broadcast_address)
print(ipaddress.ip_address("192.168.10.40") in net, ipaddress.ip_address("192.168.10.70") in net)
print(list(ipaddress.ip_network("10.0.0.0/24").subnets(new_prefix=26))[1])
```

- `/26` means 64 addresses; two are reserved (network and broadcast), so 62 usable hosts.
- **Private ranges** (not routable on the internet): `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`. **NAT** lets many private hosts share one public address.
- A **router** forwards a packet by matching the destination against its routing table using the **longest matching prefix**. The **default route** `0.0.0.0/0` points to the gateway.
- **ARP** maps an IP on the local network to a MAC address; **ICMP** carries errors and `ping`/`traceroute`.
- **MTU** (typically 1500 bytes on Ethernet) limits packet size; larger data is split.

## 3. TCP versus UDP

| | TCP | UDP |
|--|-----|-----|
| Connection | Yes (3-way handshake) | None |
| Delivery | Reliable, ordered, no duplicates | Best effort, may drop, reorder |
| Boundaries | **Byte stream** (no message boundaries) | Datagrams (boundaries kept) |
| Control | Flow control, congestion control | None |
| Overhead | Higher (20+ byte header, state) | 8-byte header |
| Use | Web, email, databases, SSH | DNS, video/voice, games, QUIC |

### TCP in detail

```text
Client                    Server
  | -- SYN (seq=x) ------->  |
  | <-- SYN+ACK (y, x+1) --  |      3-way handshake: both sides agree on starting numbers
  | -- ACK (y+1) --------->  |
  |   ... data + ACKs ...    |
  | -- FIN ---------------->  |      4-way teardown (each direction closes separately)
  | <-- ACK / FIN ---------   |
```

- **Reliability:** sequence numbers, acknowledgements, retransmission on timeout or duplicate ACKs.
- **Flow control:** the receiver advertises a **window** so the sender cannot overrun its buffer.
- **Congestion control:** the sender grows its congestion window (slow start, then additive increase) and backs off on loss (Reno, CUBIC, BBR).
- **TIME_WAIT:** the side that closes first keeps the connection state about 60 s to absorb stray packets; thousands of short connections can exhaust ports (reuse connections with keep-alive or pooling).
- **Head-of-line blocking:** one lost segment stalls everything behind it on the same connection (one motivation for QUIC/HTTP/3).

### Sockets in Python

```python
import socket, struct, threading

def tcp_demo():
    srv = socket.socket(); srv.bind(("127.0.0.1", 0)); srv.listen()
    port = srv.getsockname()[1]
    def serve():
        conn, _ = srv.accept()
        with conn:
            while data := conn.recv(1024):
                conn.sendall(data.upper())
    threading.Thread(target=serve, daemon=True).start()
    with socket.create_connection(("127.0.0.1", port)) as c:
        c.sendall(b"hello tcp")
        return c.recv(1024)
print(tcp_demo())

def send_msg(sock, payload: bytes):
    sock.sendall(struct.pack("!I", len(payload)) + payload)     # length prefix
def recv_exact(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk: raise ConnectionError("closed")
        buf += chunk
    return buf
def recv_msg(sock):
    (n,) = struct.unpack("!I", recv_exact(sock, 4))
    return recv_exact(sock, n)
a, b = socket.socketpair()
send_msg(a, b"one"); send_msg(a, b"two")
print(recv_msg(b), recv_msg(b))
```

TCP is a **stream**: two `send` calls may arrive as one `recv`, or one as two. Applications must add their own **framing** (length prefix, delimiter), as `send_msg`/`recv_msg` do above.

```python
import socket

u1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); u1.bind(("127.0.0.1", 0))
u2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
u2.sendto(b"ping", u1.getsockname())
print(u1.recvfrom(100)[0])
```

UDP preserves message boundaries but gives no delivery guarantee, so the application handles loss if it matters.

## 4. Two real-world examples

### Example 1: Why "the site is slow" can be a handshake problem
A mobile client opening a new HTTPS connection pays a TCP handshake (1 round trip) plus a TLS handshake (1 more with TLS 1.3) before the first byte of HTTP. At 100 ms round-trip time that is 200 ms of pure setup. Connection reuse (keep-alive, HTTP/2), connecting to a nearby edge node, and 0-RTT/QUIC all attack this latency.

### Example 2: Video calls use UDP
For a live call, a retransmitted audio packet arrives too late to be useful, and TCP would stall everything behind it waiting for it. Apps use UDP (via RTP/WebRTC or QUIC) and conceal loss instead: they skip the missing packet, adapt the bitrate and use forward error correction.

## 5. Tips, tricks and pitfalls

- Always handle **partial reads and writes** on TCP; use `sendall` and loop on `recv`.
- Set **timeouts** on every socket; networks fail silently.
- Use **connection pooling** to avoid repeated handshakes and TIME_WAIT buildup.
- `ping` tests reachability, `traceroute` shows hops, `ss -tan` / `netstat` shows connection states, `tcpdump`/Wireshark show packets.
- "Latency" (time per round trip) and "bandwidth" (bytes per second) are different; many small round trips hurt more than a big transfer.
- Bind servers to `127.0.0.1` for local-only; `0.0.0.0` exposes all interfaces.
- IPv6 is real: do not hard-code IPv4 parsing.

## 6. Check yourself

1. Name the layers of the TCP/IP model and one protocol at each.
2. How many usable hosts are in a `/26`? What is the network address of `192.168.10.70/26`?
3. Describe the TCP 3-way handshake and why it exists.
4. TCP versus UDP: when pick each?
5. What do flow control and congestion control each protect?
6. Why must TCP applications frame their messages?
7. What is NAT?

<details>
<summary>Answers</summary>

1. Application (HTTP), Transport (TCP/UDP), Internet (IP), Link (Ethernet/Wi-Fi).
2. `2**(32-26) - 2 = 62`. `70` falls in the block `64-127`, so the network address is `192.168.10.64`.
3. SYN, SYN+ACK, ACK. It lets both sides confirm they can send and receive and agree on initial sequence numbers.
4. TCP when you need reliable ordered delivery (web, databases). UDP when low latency matters more than perfect delivery or when you build your own reliability (DNS, real-time media, QUIC).
5. Flow control protects the receiver's buffer; congestion control protects the network.
6. TCP is a byte stream with no message boundaries; reads can return partial or merged data.
7. Network address translation: a router rewrites source addresses and ports so many private hosts share one public IP.

</details>

[Exercises](exercises.md) · [Summary](summary.md)
