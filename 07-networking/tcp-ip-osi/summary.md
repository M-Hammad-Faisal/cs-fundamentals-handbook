# The Network Stack: One-Page Summary

- **Layers:** Application (HTTP, DNS) > Transport (TCP, UDP) > Internet (IP) > Link (Ethernet, Wi-Fi). OSI adds presentation and session; "L4/L7" refers to OSI numbers. Encapsulation wraps data in headers per layer.
- **IP:** 32-bit IPv4 / 128-bit IPv6; CIDR `/n` = network bits. `/26` = 64 addresses, 62 usable. Private ranges 10/8, 172.16/12, 192.168/16; NAT shares one public IP. Routers use **longest prefix match**.
- **TCP:** connection, reliable, ordered, byte stream; 3-way handshake; flow control (receiver window), congestion control (slow start, back off on loss); TIME_WAIT; head-of-line blocking.
- **UDP:** no connection or guarantees, keeps message boundaries; DNS, real-time media, QUIC.
- **Programming:** TCP needs framing, `sendall`, loops on `recv`, timeouts, pooling.
- **Latency = round trips.** Handshakes cost RTTs; reuse connections.
- **Tools:** `ping`, `traceroute`, `ss`, `tcpdump`, Wireshark.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Packets, Addressing and Subnets](01-packets-addressing-and-subnets.md) · [Sockets Lab](02-sockets-tcp-udp-lab.md)
