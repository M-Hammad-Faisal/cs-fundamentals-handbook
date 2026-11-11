# Part 07: Networking

How computers talk to each other, from bits on a wire to a web page in your browser. Each topic has a short quick-reference lesson plus **hands-on labs that run entirely on your own computer** (sockets on `localhost`, a toy DNS server, a real local TLS handshake, a working load balancer): no internet access or special tools required beyond Python 3.10+ (the TLS lab also uses the `openssl` command).

**Prerequisites:** [Part 06 operating systems](../06-operating-systems/README.md) (processes, threads, file descriptors) and basic Python.

## Topics in this part

Read the topics in this order. Each has an overview, detailed lessons, exercises with solutions and a one-page summary (the full map is in the [index](../INDEX.md)).

<!-- topics:start -->
| Topic | Lessons | Exercises | Summary |
|-------|---------|-----------|---------|
| The Network Stack | [overview](tcp-ip-osi/README.md)<br>[Packets, Addressing and Subnets](tcp-ip-osi/01-packets-addressing-and-subnets.md)<br>[Sockets Lab](tcp-ip-osi/02-sockets-tcp-udp-lab.md) | [ex](tcp-ip-osi/exercises.md) | [sum](tcp-ip-osi/summary.md) |
| Routing | [overview](routing/README.md)<br>[Routing Protocols](routing/01-routing-protocols.md) | [ex](routing/exercises.md) | [sum](routing/summary.md) |
| DNS and HTTP | [overview](dns-http/README.md)<br>[HTTP from Scratch](dns-http/01-http-from-scratch.md)<br>[DNS in Depth](dns-http/02-dns-in-depth.md)<br>[HTTP/2 and HTTP/3 Internals](dns-http/03-http2-and-http3-internals.md) | [ex](dns-http/exercises.md) | [sum](dns-http/summary.md) |
| TLS and Security Basics | [overview](tls-security/README.md)<br>[Cryptography and TLS Lab](tls-security/01-cryptography-and-tls-lab.md) | [ex](tls-security/exercises.md) | [sum](tls-security/summary.md) |
| Load Balancing, Proxies, CDNs and Resilience | [overview](load-balancing-cdn/README.md)<br>[Load Balancing and Resilience Lab](load-balancing-cdn/01-load-balancing-and-resilience-lab.md) | [ex](load-balancing-cdn/exercises.md) | [sum](load-balancing-cdn/summary.md) |
| APIs and Real-Time Communication | [overview](apis-realtime/README.md)<br>[REST APIs, Server-Sent Events and WebSockets](apis-realtime/01-rest-apis-and-websockets-lab.md) | [ex](apis-realtime/exercises.md) | [sum](apis-realtime/summary.md) |
| Network Debugging | [overview](debugging/README.md)<br>[Network Debugging and Packet Capture](debugging/01-network-debugging-and-packet-capture.md) | [ex](debugging/exercises.md) | [sum](debugging/summary.md) |
<!-- topics:end -->

## The big picture: what happens when you open `https://example.com`

1. **DNS** turns `example.com` into an IP address (cache first, then the resolver walks root, TLD and authoritative servers). [DNS in depth](dns-http/02-dns-in-depth.md)
2. Your OS opens a **TCP connection** to that IP on port 443: the three-way handshake. [packets](tcp-ip-osi/01-packets-addressing-and-subnets.md), [sockets](tcp-ip-osi/02-sockets-tcp-udp-lab.md)
3. **TLS** negotiates keys and verifies the server's certificate. [TLS lab](tls-security/01-cryptography-and-tls-lab.md)
4. Your browser sends an **HTTP request** (often to a [REST API](apis-realtime/01-rest-apis-and-websockets-lab.md), sometimes upgrading to a WebSocket); a CDN or load balancer answers or forwards it to an app server. [HTTP](dns-http/01-http-from-scratch.md), [load balancing](load-balancing-cdn/01-load-balancing-and-resilience-lab.md)
5. The response comes back (maybe cached), the connection is reused for the next request.

Every packet on the way is wrapped in headers (HTTP inside TLS inside TCP inside IP inside Ethernet) and routed hop by hop by routers using longest-prefix matching.

## How to study

1. Run each lab and **change the numbers** (loss rate, TTL, quantum, weights) to see the effect.
2. Use the real tools alongside: `dig`, `curl -v`, `ss`/`netstat`, `ping`, `traceroute`, browser DevTools (Network tab).
3. Do the practice questions, then the check-yourself questions the next day.

Back to the [handbook home](../README.md) · [index](../INDEX.md).
