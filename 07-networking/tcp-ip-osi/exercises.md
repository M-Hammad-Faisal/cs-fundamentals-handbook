# The Network Stack: Exercises

1. Split `10.0.0.0/24` into four equal subnets. List each network and its usable range.
2. For `172.16.5.130/25`, give the network address, broadcast address and number of usable hosts.
3. A packet to `10.1.2.3` matches routes `10.0.0.0/8` (gateway A) and `10.1.0.0/16` (gateway B). Which is used and why?
4. Write a TCP client and server where the client sends three messages quickly and the server prints each one separately (use length-prefix framing).
5. Show that two UDP `sendto` calls arrive as two separate datagrams.
6. Explain slow start and what happens to throughput after a packet loss.
7. Why can a server with many short-lived client connections run out of ports even though few are active?
8. A call to `recv(1024)` returned only half of a 2 KB message. Is that a bug? What do you change?

<details>
<summary>Solutions</summary>

**1.** `/26` subnets: `10.0.0.0/26` (hosts .1 to .62), `10.0.0.64/26` (.65 to .126), `10.0.0.128/26` (.129 to .190), `10.0.0.192/26` (.193 to .254).
```python
import ipaddress
for s in ipaddress.ip_network("10.0.0.0/24").subnets(new_prefix=26):
    hosts = list(s.hosts()); print(s, hosts[0], hosts[-1])
```

**2.** `/25` blocks of 128: `.130` is in `172.16.5.128/25`. Network `172.16.5.128`, broadcast `172.16.5.255`, usable hosts `126`.
```python
n = ipaddress.ip_network("172.16.5.130/25", strict=False); print(n.network_address, n.broadcast_address, n.num_addresses - 2)
```

**3.** Gateway B: routers use the **longest prefix match**, and `/16` is more specific than `/8`.

**4.** Use `send_msg`/`recv_msg` from the lesson: the client calls `send_msg` three times; the server loops `recv_msg` and prints each, getting exactly three separate messages even if TCP delivered them in one chunk.

**5.**
```python
import socket
r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); r.bind(("127.0.0.1", 0))
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(b"one", r.getsockname()); s.sendto(b"two", r.getsockname())
print(r.recvfrom(100)[0], r.recvfrom(100)[0])    # b'one' b'two'
```

**6.** Slow start starts the congestion window small and roughly doubles it each round trip until a threshold or loss. On loss, TCP treats it as congestion: it cuts the window (for example halves it in classic Reno/CUBIC) and increases more slowly afterwards, so throughput dips and recovers.

**7.** Each closed connection leaves the closer in TIME_WAIT (about 60 s) holding a (source IP, source port, destination IP, destination port) tuple; with a limited ephemeral port range (about 28k to 60k ports) toward the same server, thousands per second exhaust it. Fix: connection pooling or keep-alive, let the server close first where sensible, widen the port range, or spread across more destination addresses.

**8.** Not a bug: TCP does not preserve message boundaries and `recv` returns whatever is available up to the limit. Loop until you have all the bytes (`recv_exact`), using a length prefix or delimiter to know when the message ends.

</details>

[Lesson](README.md) · [Summary](summary.md)
