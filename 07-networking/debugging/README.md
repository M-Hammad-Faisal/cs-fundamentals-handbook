# Network Debugging

Finding out why a connection is slow, refused or flaky: a layer-by-layer method, packet captures, and the everyday tools.

## Detailed lesson

- [Network debugging and packet capture](01-network-debugging-and-packet-capture.md): the climb-the-layers method, building and reading a pcap file from scratch, tcpdump and Wireshark filters, reading TCP conversations (retransmissions, resets), timing breakdowns and troubleshooting playbooks

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Symptom | Likely cause |
|---------|--------------|
| Connection refused (instant) | nothing listening: the host replied with an RST |
| Connection timed out | packets silently dropped: firewall, wrong IP, routing |
| Big requests hang, small work | MTU or Path MTU Discovery problem |
| Random resets mid-connection | idle timeout in a middlebox or mismatched keep-alive |

Related: [TCP and UDP sockets lab](../tcp-ip-osi/02-sockets-tcp-udp-lab.md), [DNS in depth](../dns-http/02-dns-in-depth.md).

Back to [networking](../README.md).
