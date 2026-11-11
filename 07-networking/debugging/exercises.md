# Network Debugging: Exercises

Work through these after [Network debugging and packet capture](01-network-debugging-and-packet-capture.md). The code parts use only the standard library and run on one machine.

1. **Probe a port.** Write `probe(host, port, timeout=1.0)` returning `"open"`, `"refused"` or `"timeout"`. Test it against a port you open yourself and against a closed local port. What does each result tell you about *where* the problem is?
2. **Internet checksum.** Implement the 16-bit one's-complement checksum used by IPv4, TCP and UDP, and check it on the IPv4 header `45 00 00 73 00 00 40 00 40 11 [checksum] c0 a8 00 01 c0 a8 00 c7`, where the real checksum is `0xb861`.
3. **MSS and MTU.** Write `mss(mtu, ip_header=20, tcp_header=20)`. What is the largest TCP payload on a 1500-byte Ethernet link, and on a 1492-byte PPPoE link? Why can a too-large MTU make big downloads hang while small requests work?
4. **Timing breakdown.** A capture shows: DNS query sent at 0.000 s, DNS answer at 0.030, SYN at 0.031, SYN-ACK at 0.081, GET request sent at 0.082, first response byte at 0.382, last byte at 0.482. Compute DNS, connect, server wait (time to first byte) and download times. Where is the problem?
5. **Find retransmissions.** Given a list of `(time, seq, payload_length)` data segments from one sender, write `find_retransmissions(segments)` returning those whose sequence number was already sent.
6. **Write capture filters.** Write a tcpdump (BPF) capture filter for each: (a) HTTPS traffic to or from host 10.0.0.5, (b) only TCP SYN packets, (c) DNS traffic, (d) everything except SSH, and a Wireshark display filter for (e) TCP retransmissions, (f) HTTP responses with status 500.
7. **Climb the layers.** A user says "the website is down". List the checks you would run, in order from the bottom of the stack to the top, with one command for each.
8. **Interpret the symptom.** For each symptom name the most likely cause: (a) connection refused instantly, (b) connection times out after 30 s, (c) the page loads for small requests but large downloads stall, (d) a name works on your laptop but not on a server, (e) a connection resets after exactly 60 s idle.

<details>
<summary>Solutions</summary>

**1.**
```python
import socket

def probe(host, port, timeout=1.0):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return "open"
    except ConnectionRefusedError:
        return "refused"                      # the host answered with a reset: nothing is listening there
    except (TimeoutError, socket.timeout):
        return "timeout"                      # no answer at all: packets are being dropped (firewall, wrong route)

server = socket.socket()
server.bind(("127.0.0.1", 0))
server.listen()
open_port = server.getsockname()[1]
closed = socket.socket(); closed.bind(("127.0.0.1", 0)); closed_port = closed.getsockname()[1]; closed.close()   # a port that nobody listens on

print(probe("127.0.0.1", open_port), probe("127.0.0.1", closed_port))
server.close()
# open refused
```
**Refused** means the packet reached the machine and the operating system said nobody is listening: the network path is fine, the service is not (stopped, wrong port). **Timeout** means no answer: something is silently dropping packets (a firewall, a wrong route, a dead host). They point at completely different layers.

**2.**
```python
def internet_checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    total = sum((data[i] << 8) | data[i + 1] for i in range(0, len(data), 2))
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)       # fold the carries back in
    return ~total & 0xFFFF

header = bytes.fromhex("4500 0073 0000 4000 4011 0000 c0a8 0001 c0a8 00c7".replace(" ", ""))
checksum = internet_checksum(header)
filled = header[:10] + checksum.to_bytes(2, "big") + header[12:]
print(hex(checksum), internet_checksum(filled))
# 0xb861 0
```
Computing the checksum over a header that already contains a correct checksum gives 0: that is how receivers verify it.

**3.**
```python
def mss(mtu, ip_header=20, tcp_header=20):
    return mtu - ip_header - tcp_header

print(mss(1500), mss(1492))
# 1460 1452
```
If a sender uses 1500-byte packets on a path with a smaller MTU and the "fragmentation needed" ICMP messages are blocked by a firewall, large segments vanish silently (**a path MTU black hole**) while small requests, which fit, work fine.

**4.**
```python
events = {"dns_sent": 0.000, "dns_answer": 0.030, "syn": 0.031, "syn_ack": 0.081, "request": 0.082, "first_byte": 0.382, "last_byte": 0.482}
breakdown = {
    "dns": events["dns_answer"] - events["dns_sent"],
    "connect": events["syn_ack"] - events["syn"],
    "server wait (ttfb)": events["first_byte"] - events["request"],
    "download": events["last_byte"] - events["first_byte"],
}
print({k: round(v * 1000) for k, v in breakdown.items()})
# {'dns': 30, 'connect': 50, 'server wait (ttfb)': 300, 'download': 100}
```
DNS (30 ms) and connect (50 ms, one round trip) are normal; the **300 ms wait for the first byte** is the server thinking (slow application or database), so look at the server, not the network.

**5.**
```python
def find_retransmissions(segments):
    seen, repeats = set(), []
    for time, seq, length in segments:
        if length > 0 and seq in seen:
            repeats.append((time, seq, length))
        seen.add(seq)
    return repeats

capture = [(0.00, 1000, 100), (0.01, 1100, 100), (0.02, 1200, 100), (0.30, 1100, 100), (0.31, 1300, 100)]
print(find_retransmissions(capture))
# [(0.3, 1100, 100)]
```
The segment starting at sequence 1100 was sent again 290 ms later, probably after a timeout: a sign of packet loss on the path.

**6.** (a) `tcp port 443 and host 10.0.0.5` (b) `tcp[tcpflags] & (tcp-syn) != 0 and tcp[tcpflags] & (tcp-ack) = 0` (SYN without ACK: the first packet of a connection) (c) `udp port 53 or tcp port 53` (d) `not port 22` (e) Wireshark: `tcp.analysis.retransmission` (f) Wireshark: `http.response.code == 500`. Capture filters (BPF) are applied while capturing and use a different, simpler syntax than display filters (Wireshark), which are applied afterwards to what was captured.

**7.** (1) Link: `ifconfig` or `ip link` (is the interface up, do I have a cable or Wi-Fi?). (2) IP: `ip addr` / `ping 127.0.0.1` then `ping <gateway>` (do I have an address and reach the router?). (3) DNS: `dig example.com` or `nslookup` (does the name resolve to the right address?). (4) Route: `traceroute example.com` (where do packets stop?). (5) TCP port: `nc -vz example.com 443` (is something accepting connections?). (6) TLS: `openssl s_client -connect example.com:443` (does the handshake and certificate check succeed?). (7) Application: `curl -v https://example.com/` (what status and headers come back?). Stop at the first layer that fails: that is where the problem is.

**8.** (a) Nothing listening on that port (service down or wrong port), or a firewall actively rejecting. (b) Packets silently dropped: firewall, security group, wrong route or a dead host. (c) A path MTU problem (ICMP blocked), or a middlebox mangling large packets. (d) Different DNS resolvers or a stale cache or a missing `/etc/hosts` entry on one of the machines. (e) An idle timeout in a middlebox (load balancer, NAT or firewall) closing the connection: use keep-alives shorter than the timeout.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Network Debugging and Packet Capture](01-network-debugging-and-packet-capture.md)
