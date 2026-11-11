# Network Debugging: One-Page Summary

## Key facts

- **Method: climb the layers.** Link (cable, Wi-Fi) → IP (address, gateway) → DNS (name to address) → route (`traceroute`) → TCP port (`nc -vz`) → TLS (`openssl s_client`) → application (`curl -v`). Stop at the first layer that fails.
- **Refused vs timeout:** *refused* (instant) = the host answered with a reset: nothing listening, so the network is fine. *Timed out* = silence: packets dropped (firewall, route, dead host).
- **Tools:** `ping` (reachability), `dig` (DNS), `traceroute` (path), `nc` (ports), `curl -v` (HTTP), `ss`/`lsof` (what is listening), `tcpdump` and Wireshark (packets).
- **Capture:** `tcpdump -i any -w file.pcap 'tcp port 443 and host 10.0.0.5'` (BPF capture filter, applied while capturing) then analyse in Wireshark (display filters such as `tcp.analysis.retransmission`, `http.response.code == 500`). A pcap file is a 24-byte global header plus a 16-byte header per packet.
- **Reading TCP:** SYN, SYN-ACK, ACK is the handshake (one round trip); repeated sequence numbers are retransmissions (loss); `RST` is an abrupt close; `FIN` is a graceful close.
- **Timing breakdown of a request:** DNS + connect (≈ 1 RTT) + TLS + server wait (time to first byte) + download. Find the biggest piece.
- **MTU:** TCP payload (MSS) = MTU − 20 (IP) − 20 (TCP) = 1460 on Ethernet. Big transfers hanging while small ones work suggests a path MTU black hole.
- **TLS debugging:** `SSLKEYLOGFILE` lets Wireshark decrypt your own browser's traffic.
- **Always:** change one thing at a time, write down what you saw, and capture on both ends when you can.

## Pitfalls

- Changing several things at once, and not writing down what you saw.
- Mixing up "connection refused" (nothing listening) and "timed out" (packets dropped).
- Capturing on one side only; confusing capture filters (BPF) with Wireshark display filters.
- Trusting `ping`: ICMP is often blocked even when the service works.
- Sharing a capture or key-log file that contains secrets.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Network Debugging and Packet Capture](01-network-debugging-and-packet-capture.md)
