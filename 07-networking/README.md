# Networking

How computers talk to each other, from bits on a wire to a web page in your browser. Each topic has a short quick-reference lesson plus **hands-on labs that run entirely on your own computer** (sockets on `localhost`, a toy DNS server, a real local TLS handshake, a working load balancer): no internet access or special tools required beyond Python 3.10+ (the TLS lab also uses the `openssl` command).

**Prerequisites:** [Part 06 operating systems](../06-operating-systems/README.md) (processes, threads, file descriptors) and basic Python.

## Reading order

| # | Topic | Quick reference | Hands-on labs |
|---|-------|-----------------|---------------|
| 1 | The network stack: OSI, TCP/IP, IP addressing, TCP vs UDP | [lesson](tcp-ip-osi/README.md) | [packets, addressing and subnets](tcp-ip-osi/01-packets-addressing-and-subnets.md) · [sockets: TCP and UDP](tcp-ip-osi/02-sockets-tcp-udp-lab.md) |
| 2 | DNS and HTTP | [lesson](dns-http/README.md) | [HTTP from scratch](dns-http/01-http-from-scratch.md) · [DNS in depth](dns-http/02-dns-in-depth.md) |
| 3 | TLS and security basics | [lesson](tls-security/README.md) | [cryptography and TLS lab](tls-security/01-cryptography-and-tls-lab.md) |
| 4 | Load balancing, CDNs and resilience | [lesson](load-balancing-cdn/README.md) | [load balancing and resilience lab](load-balancing-cdn/01-load-balancing-and-resilience-lab.md) |

Each topic folder also has `exercises.md` and a one-page `summary.md`.

## The big picture: what happens when you open `https://example.com`

1. **DNS** turns `example.com` into an IP address (cache first, then the resolver walks root, TLD and authoritative servers). [DNS in depth](dns-http/02-dns-in-depth.md)
2. Your OS opens a **TCP connection** to that IP on port 443: the three-way handshake. [packets](tcp-ip-osi/01-packets-addressing-and-subnets.md), [sockets](tcp-ip-osi/02-sockets-tcp-udp-lab.md)
3. **TLS** negotiates keys and verifies the server's certificate. [TLS lab](tls-security/01-cryptography-and-tls-lab.md)
4. Your browser sends an **HTTP request**; a CDN or load balancer answers or forwards it to an app server. [HTTP](dns-http/01-http-from-scratch.md), [load balancing](load-balancing-cdn/01-load-balancing-and-resilience-lab.md)
5. The response comes back (maybe cached), the connection is reused for the next request.

Every packet on the way is wrapped in headers (HTTP inside TLS inside TCP inside IP inside Ethernet) and routed hop by hop by routers using longest-prefix matching.

## How to study

1. Run each lab and **change the numbers** (loss rate, TTL, quantum, weights) to see the effect.
2. Use the real tools alongside: `dig`, `curl -v`, `ss`/`netstat`, `ping`, `traceroute`, browser DevTools (Network tab).
3. Do the practice questions, then the check-yourself questions the next day.

Back to the [index](../INDEX.md).
