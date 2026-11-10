# Network Debugging and Packet Capture (tcpdump, Wireshark and Python)

**Prerequisites:** [packets, addressing and subnets](../tcp-ip-osi/01-packets-addressing-and-subnets.md) (headers and checksums), [sockets lab](../tcp-ip-osi/02-sockets-tcp-udp-lab.md), [DNS in depth](../dns-http/02-dns-in-depth.md), [HTTP from scratch](../dns-http/01-http-from-scratch.md), [TLS lab](../tls-security/01-cryptography-and-tls-lab.md). **You will learn:** a **systematic method** for finding network problems (work up the layers); how a **packet capture** (`.pcap`) file is structured (you will **write one from scratch** and read it back); how to read a **TCP conversation** (handshake, flags, sequence numbers, retransmissions, resets); how to **measure** where time goes (DNS, connect, first byte); the everyday toolbox (**`curl -v`, `dig`, `nc`, `ss`, `traceroute`, `openssl s_client`, `tcpdump`, Wireshark**); and playbooks for the usual symptoms. The capture file we build is decoded by the real `tcpdump` too, which proves the packets are valid.

## 1. In plain words

When "the network is broken", the cause could be anywhere between your code and the other machine: your app, DNS, the route, a firewall, TLS, the server, or a flaky link. Guessing wastes hours. **Debugging means narrowing down**: test one layer at a time, and when you cannot see what is happening, **look at the actual packets**, the ground truth that logs and libraries only summarize.

A packet capture is a tape recording of the wire: every packet with its exact bytes and time. Reading one is like reading the conversation instead of someone's description of it.

## 2. The method: climb the layers

Start at the bottom and move up; stop at the first layer that fails.

```text
 7  Application   does the server answer correctly? (curl -v, logs)
 6  TLS           does the handshake complete? valid certificate? (openssl s_client)
 4  Transport     can I open a TCP connection to that port? (nc -vz host port, ss)
 3  Network       is there a route? what is the path? (ping, traceroute, ip route)
 3  Name          does the name resolve to the right address? (dig)
 2  Link/local    is my interface up, do I have an IP, gateway reachable? (ip addr, arp -a)
```

| Check | Command | What a failure means |
|-------|---------|----------------------|
| Interface and IP | `ip addr` (Linux), `ifconfig` / `ipconfig getifaddr en0` (macOS) | no address: DHCP or Wi-Fi problem |
| Gateway reachable | `ping 192.168.1.1` | local network problem |
| Internet reachable by IP | `ping 1.1.1.1` | routing or ISP problem |
| Name resolution | `dig example.com +short` | DNS problem (try `dig @1.1.1.1 ...` to bypass your resolver) |
| Port reachable | `nc -vz example.com 443` | closed port, firewall, or service down |
| TLS | `openssl s_client -connect example.com:443 -servername example.com` | certificate or protocol problem |
| HTTP | `curl -v https://example.com/` | application-level problem |
| Path | `traceroute example.com` / `mtr example.com` | where latency or loss begins |

**Distinguish the failure types by *how* they fail**, because each points to a different cause:

| Symptom | Meaning |
|---------|---------|
| **"Connection refused"** (immediate) | the host answered with a **TCP RST**: nothing is listening on that port (or a firewall actively rejects) |
| **"Connection timed out"** (after a long wait) | packets are **silently dropped**: a firewall, a wrong IP, a down host or a routing black hole |
| **"Name or service not known"** | DNS failed before any connection was tried |
| **"Connection reset by peer"** | the other side (or a middlebox) sent a RST **mid-connection** |
| **TLS "certificate verify failed" / "handshake failure"** | name mismatch, expired or untrusted certificate, or no common protocol/cipher |
| **Works for some users or sometimes** | intermittent loss, MTU/fragmentation, load balancing to one bad backend, DNS caching |

You can see "refused" versus "timeout" yourself without any network:

```python
import socket, time

def probe(host, port, timeout=0.5):
    start = time.perf_counter()
    try:
        socket.create_connection((host, port), timeout=timeout).close()
        return "open"
    except ConnectionRefusedError:
        return f"refused after {1000 * (time.perf_counter() - start):.0f} ms"        # an RST came straight back
    except socket.timeout:
        return f"timed out after {1000 * (time.perf_counter() - start):.0f} ms"       # nothing came back at all

closed = socket.socket(); closed.bind(("127.0.0.1", 0)); closed_port = closed.getsockname()[1]; closed.close()
print(probe("127.0.0.1", closed_port))                          # refused after a few ms   (loopback: nothing listens, the kernel replies RST at once)
```

On a real network the same experiment against a firewalled address shows the other behaviour (a **timeout**), which is why a hanging connection and a refused one lead you in opposite directions.

## 3. The structure of a capture file

The classic **pcap** format is simple, which is why tools everywhere read it:

```text
Global header (24 bytes, once):  magic 0xA1B2C3D4 | version 2.4 | timezone | accuracy | snaplen | link type (1 = Ethernet)
Per packet:  record header (16 bytes): timestamp seconds | timestamp microseconds | captured length | original length
             then the captured bytes of the packet exactly as seen on the wire (Ethernet frame, headers and payload)
```

Newer **pcapng** adds blocks for multiple interfaces, comments and decryption secrets, but the idea is the same.

To produce a realistic file we need real packets: build the Ethernet, IP, UDP and TCP headers (with correct checksums; the [packets lesson](../tcp-ip-osi/01-packets-addressing-and-subnets.md) explained the formats), then script a conversation: a **DNS lookup**, a **TCP handshake**, an **HTTP request and response**, and a **close**.

```python
import struct, socket, os, tempfile

def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF

def mac(text):
    return bytes(int(x, 16) for x in text.split(":"))

def ethernet(src, dst, payload, ethertype=0x0800):
    return mac(dst) + mac(src) + struct.pack("!H", ethertype) + payload

def ipv4(src, dst, proto, payload, ident=1, ttl=64):
    header = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + len(payload), ident, 0x4000, ttl, proto, 0, socket.inet_aton(src), socket.inet_aton(dst))
    header = header[:10] + struct.pack("!H", checksum(header)) + header[12:]
    return header + payload

def udp(src_ip, dst_ip, sport, dport, payload):
    length = 8 + len(payload)
    pseudo = socket.inet_aton(src_ip) + socket.inet_aton(dst_ip) + struct.pack("!BBH", 0, 17, length)      # the checksum covers a "pseudo header" too
    header = struct.pack("!HHHH", sport, dport, length, 0)
    return struct.pack("!HHHH", sport, dport, length, checksum(pseudo + header + payload) or 0xFFFF) + payload

FIN, SYN, RST, PSH, ACK = 0x01, 0x02, 0x04, 0x08, 0x10

def tcp(src_ip, dst_ip, sport, dport, seq, ack, flags, payload=b"", window=65535):
    header = struct.pack("!HHIIBBHHH", sport, dport, seq, ack, 5 << 4, flags, window, 0, 0)
    pseudo = socket.inet_aton(src_ip) + socket.inet_aton(dst_ip) + struct.pack("!BBH", 0, 6, len(header) + len(payload))
    return header[:16] + struct.pack("!H", checksum(pseudo + header + payload)) + header[18:] + payload

def dns_name(name):
    return b"".join(bytes([len(label)]) + label.encode() for label in name.split(".")) + b"\x00"

CLIENT, RESOLVER, SERVER = "192.168.1.10", "192.168.1.1", "93.184.216.34"
CMAC, RMAC, SMAC = "aa:bb:cc:00:00:10", "aa:bb:cc:00:00:01", "aa:bb:cc:00:00:02"

def conversation(retransmit_response=False, reset_instead_of_close=False):
    packets, clock = [], [1_700_000_000.0]
    def add(delay, frame):
        clock[0] += delay
        packets.append((clock[0], frame))
    def from_client(proto_payload, proto, ident):
        return ethernet(CMAC, SMAC, ipv4(CLIENT, SERVER, proto, proto_payload, ident=ident))
    def from_server(proto_payload, proto, ident):
        return ethernet(SMAC, CMAC, ipv4(SERVER, CLIENT, proto, proto_payload, ident=ident))

    query = struct.pack("!HHHHHH", 0x1234, 0x0100, 1, 0, 0, 0) + dns_name("example.com") + struct.pack("!HH", 1, 1)
    add(0.0, ethernet(CMAC, RMAC, ipv4(CLIENT, RESOLVER, 17, udp(CLIENT, RESOLVER, 53100, 53, query), ident=1)))
    answer = (struct.pack("!HHHHHH", 0x1234, 0x8180, 1, 1, 0, 0) + dns_name("example.com") + struct.pack("!HH", 1, 1)
              + b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, 300, 4) + socket.inet_aton(SERVER))
    add(0.024, ethernet(RMAC, CMAC, ipv4(RESOLVER, CLIENT, 17, udp(RESOLVER, CLIENT, 53, 53100, answer), ident=2)))

    c, s = 1000, 5000                                           # initial sequence numbers
    add(0.001, from_client(tcp(CLIENT, SERVER, 51000, 80, c, 0, SYN), 6, 3))
    add(0.050, from_server(tcp(SERVER, CLIENT, 80, 51000, s, c + 1, SYN | ACK), 6, 4))
    add(0.001, from_client(tcp(CLIENT, SERVER, 51000, 80, c + 1, s + 1, ACK), 6, 5))
    request = b"GET / HTTP/1.1\r\nHost: example.com\r\nConnection: close\r\n\r\n"
    body = b"<html>hello</html>"
    response = b"HTTP/1.1 200 OK\r\nContent-Length: " + str(len(body)).encode() + b"\r\nContent-Type: text/html\r\n\r\n" + body
    add(0.001, from_client(tcp(CLIENT, SERVER, 51000, 80, c + 1, s + 1, PSH | ACK, request), 6, 6))
    add(0.050, from_server(tcp(SERVER, CLIENT, 80, 51000, s + 1, c + 1 + len(request), ACK), 6, 7))
    response_frame = from_server(tcp(SERVER, CLIENT, 80, 51000, s + 1, c + 1 + len(request), PSH | ACK, response), 6, 8)
    add(0.010, response_frame)
    if retransmit_response:                                     # the client never ACKed: after a timeout (200 ms) the server resends the SAME bytes
        add(0.200, from_server(tcp(SERVER, CLIENT, 80, 51000, s + 1, c + 1 + len(request), PSH | ACK, response), 6, 9))
    if reset_instead_of_close:                                  # a middlebox or the client aborts the connection
        add(0.050, from_client(tcp(CLIENT, SERVER, 51000, 80, c + 1 + len(request), 0, RST), 6, 10))
    else:
        add(0.050, from_client(tcp(CLIENT, SERVER, 51000, 80, c + 1 + len(request), s + 1 + len(response), FIN | ACK), 6, 11))
        add(0.050, from_server(tcp(SERVER, CLIENT, 80, 51000, s + 1 + len(response), c + 2 + len(request), FIN | ACK), 6, 12))
        add(0.050, from_client(tcp(CLIENT, SERVER, 51000, 80, c + 2 + len(request), s + 2 + len(response), ACK), 6, 13))
    return packets

def write_pcap(path, packets):
    with open(path, "wb") as f:
        f.write(struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))        # magic, version 2.4, timezone, accuracy, snaplen, link type 1 = Ethernet
        for timestamp, frame in packets:
            seconds = int(timestamp)
            microseconds = int(round((timestamp - seconds) * 1_000_000))
            f.write(struct.pack("<IIII", seconds, microseconds, len(frame), len(frame)) + frame)

capture_path = os.path.join(tempfile.mkdtemp(), "demo.pcap")
write_pcap(capture_path, conversation())
print(os.path.getsize(capture_path), "bytes;", len(conversation()), "packets")      # 982 bytes; 11 packets
print(open(capture_path, "rb").read(24).hex())                                    # d4c3b2a1020004000000000000000000ffff000001000000
```

The first 24 bytes spell the header (`d4c3b2a1` is the magic written little-endian, then version 2.4, snaplen `ffff` = 65535, link type 1).

## 4. Reading a capture: your own dissector

A **dissector** peels the layers: Ethernet, then IP (using the protocol field), then TCP or UDP. Here is a compact one in Python, producing lines in the style of `tcpdump`:

```python
def read_pcap(path):
    data = open(path, "rb").read()
    assert struct.unpack("<I", data[:4])[0] == 0xA1B2C3D4, "not a little-endian pcap file"
    pos, packets = 24, []
    while pos < len(data):
        seconds, microseconds, captured, original = struct.unpack("<IIII", data[pos:pos + 16])
        pos += 16
        packets.append((seconds + microseconds / 1e6, data[pos:pos + captured]))
        pos += captured
    return packets

FLAG_NAMES = [(SYN, "S"), (FIN, "F"), (RST, "R"), (PSH, "P")]

def dissect(frame):
    ethertype = struct.unpack("!H", frame[12:14])[0]
    if ethertype != 0x0800:
        return {"proto": f"ethertype {ethertype:#06x}"}
    ip = frame[14:]
    ihl = (ip[0] & 0x0F) * 4
    proto = ip[9]
    info = {"src": socket.inet_ntoa(ip[12:16]), "dst": socket.inet_ntoa(ip[16:20]), "ttl": ip[8],
            "ip_checksum_ok": checksum(ip[:ihl]) == 0}
    segment = ip[ihl:struct.unpack("!H", ip[2:4])[0]]
    pseudo_len = len(segment)
    if proto == 6:
        sport, dport, seq, ack, offset, flags, window = struct.unpack("!HHIIBBH", segment[:16])
        header_len = (offset >> 4) * 4
        pseudo = ip[12:20] + struct.pack("!BBH", 0, 6, pseudo_len)
        info.update(proto="TCP", sport=sport, dport=dport, seq=seq, ack=ack, window=window, payload=segment[header_len:],
                    flags="".join(n for bit, n in FLAG_NAMES if flags & bit) + ("." if flags & ACK else ""),
                    transport_checksum_ok=checksum(pseudo + segment) == 0)
    elif proto == 17:
        sport, dport, length, _ = struct.unpack("!HHHH", segment[:8])
        pseudo = ip[12:20] + struct.pack("!BBH", 0, 17, pseudo_len)
        info.update(proto="UDP", sport=sport, dport=dport, payload=segment[8:length], transport_checksum_ok=checksum(pseudo + segment) == 0)
    return info

def summarize(packets):
    start = packets[0][0]
    lines = []
    for timestamp, frame in packets:
        p = dissect(frame)
        base = f"{timestamp - start:7.3f}s  {p['src']}.{p['sport']} > {p['dst']}.{p['dport']}"
        if p["proto"] == "TCP":
            lines.append(f"{base}  TCP [{p['flags']}] seq={p['seq']} ack={p['ack']} len={len(p['payload'])}")
        else:
            lines.append(f"{base}  UDP len={len(p['payload'])}")
    return lines

packets = read_pcap(capture_path)
for line in summarize(packets):
    print(line)
#   0.000s  192.168.1.10.53100 > 192.168.1.1.53  UDP len=29
#   0.024s  192.168.1.1.53 > 192.168.1.10.53100  UDP len=45
#   0.025s  192.168.1.10.51000 > 93.184.216.34.80  TCP [S] seq=1000 ack=0 len=0
#   0.075s  93.184.216.34.80 > 192.168.1.10.51000  TCP [S.] seq=5000 ack=1001 len=0
#   0.076s  192.168.1.10.51000 > 93.184.216.34.80  TCP [.] seq=1001 ack=5001 len=0
#   0.077s  192.168.1.10.51000 > 93.184.216.34.80  TCP [P.] seq=1001 ack=5001 len=56
#   0.127s  93.184.216.34.80 > 192.168.1.10.51000  TCP [.] seq=5001 ack=1057 len=0
#   0.137s  93.184.216.34.80 > 192.168.1.10.51000  TCP [P.] seq=5001 ack=1057 len=82
#   0.187s  192.168.1.10.51000 > 93.184.216.34.80  TCP [F.] seq=1057 ack=5083 len=0
#   0.237s  93.184.216.34.80 > 192.168.1.10.51000  TCP [F.] seq=5083 ack=1058 len=0
#   0.287s  192.168.1.10.51000 > 93.184.216.34.80  TCP [.] seq=1058 ack=5084 len=0
print(all(dissect(f)["ip_checksum_ok"] and dissect(f)["transport_checksum_ok"] for _, f in packets))       # True    every IP, TCP and UDP checksum verifies
```

Compare with what the real tool says about the same file. `tcpdump -nn -t -r demo.pcap` (`-nn` no name lookups, `-t` no timestamps, `-r` read a file; reading a file needs no special privileges):

```python
import subprocess, shutil

if shutil.which("tcpdump"):
    out = subprocess.run(["tcpdump", "-nn", "-t", "-r", capture_path], capture_output=True, text=True).stdout.splitlines()
    for line in out[:6]:
        print(line)
    # IP 192.168.1.10.53100 > 192.168.1.1.53: 4660+ A? example.com. (29)
    # IP 192.168.1.1.53 > 192.168.1.10.53100: 4660 1/0/0 A 93.184.216.34 (45)
    # IP 192.168.1.10.51000 > 93.184.216.34.80: Flags [S], seq 1000, win 65535, length 0
    # IP 93.184.216.34.80 > 192.168.1.10.51000: Flags [S.], seq 5000, ack 1001, win 65535, length 0
    # IP 192.168.1.10.51000 > 93.184.216.34.80: Flags [.], ack 1, win 65535, length 0
    # IP 192.168.1.10.51000 > 93.184.216.34.80: Flags [P.], seq 1:57, ack 1, win 65535, length 56: HTTP: GET / HTTP/1.1
    verbose = subprocess.run(["tcpdump", "-nn", "-t", "-v", "-r", capture_path, "tcp and port 80", "-c", "1"], capture_output=True, text=True).stdout
    print("(correct)" in verbose)                                # True   tcpdump itself confirms our TCP checksum is valid
else:
    print("tcpdump not installed here")
```

`tcpdump` shows **relative** sequence numbers after the first packets (`seq 1:57, ack 1`) to make them readable; Wireshark does the same by default. Note the DNS line: tcpdump decodes the query (`A? example.com.`) and the answer (`1/0/0 A 93.184.216.34`: one answer, zero authority, zero additional).

## 5. Reading a TCP conversation

```text
[S]    SYN      "I want to open a connection; my first sequence number is X"
[S.]   SYN-ACK  "OK; mine is Y, and I expect your byte X+1 next"      ('.' means the ACK flag is set)
[.]    ACK      "got it"; with data in front it is [P.] = PSH+ACK ("deliver this data now")
[F.]   FIN-ACK  "I am done sending"
[R] / [R.]  RST "abort, I do not recognize this connection" (or nothing listens)
```

What to read from a capture:

| You see | It means |
|---------|----------|
| `[S]` repeated with no `[S.]` | the SYN is dropped: firewall, wrong IP, host down (looks like a **timeout** to the application) |
| `[S]` immediately answered by `[R.]` | nothing is listening on that port: **connection refused** |
| `[S]`, `[S.]`, `[.]` quickly | healthy handshake; the time between `[S]` and `[S.]` is **one RTT** |
| the same `seq` sent again after a pause | a **retransmission**: the receiver's ACK never arrived (loss somewhere) |
| many duplicate ACKs (`ack` not advancing) | a gap: later segments arrived but one is missing (triggers **fast retransmit**) |
| `win 0` (zero window) | the receiver's buffer is full: the **application is not reading** fast enough |
| `[R]` in the middle of a conversation | an abort by one side or a **middlebox** (firewall, load balancer) |
| the server's `[F.]` first, then data from the client | normal close ordering; many `FIN_WAIT` leftovers hint at an app not closing sockets |

### Measuring from a capture

With the dissector, ordinary questions become short programs: handshake RTT, DNS latency, time to first byte, bytes sent:

```python
def analyze(packets):
    start = packets[0][0]
    parsed = [(t, dissect(f)) for t, f in packets]
    result = {}
    dns = [(t, p) for t, p in parsed if p["proto"] == "UDP" and 53 in (p["sport"], p["dport"])]
    result["dns_ms"] = round((dns[1][0] - dns[0][0]) * 1000)                     # query to answer
    syn = next(t for t, p in parsed if p["proto"] == "TCP" and p["flags"] == "S")
    synack = next(t for t, p in parsed if p["proto"] == "TCP" and p["flags"] == "S.")
    result["handshake_rtt_ms"] = round((synack - syn) * 1000)                    # SYN to SYN-ACK = one round trip to the server
    request = next(t for t, p in parsed if p["proto"] == "TCP" and p["payload"].startswith(b"GET "))
    first_data = next(t for t, p in parsed if p["proto"] == "TCP" and p["payload"].startswith(b"HTTP/"))
    result["time_to_first_byte_ms"] = round((first_data - request) * 1000)       # request sent to response received
    result["bytes_c2s"] = sum(len(p["payload"]) for _, p in parsed if p["proto"] == "TCP" and p["dport"] == 80)
    result["bytes_s2c"] = sum(len(p["payload"]) for _, p in parsed if p["proto"] == "TCP" and p["sport"] == 80)
    result["total_ms"] = round((parsed[-1][0] - start) * 1000)
    return result

print(analyze(packets))
# {'dns_ms': 24, 'handshake_rtt_ms': 50, 'time_to_first_byte_ms': 60, 'bytes_c2s': 56, 'bytes_s2c': 82, 'total_ms': 287}
```

The page took 287 ms in total, of which DNS was 24 ms, the handshake needed 50 ms (the RTT to the server), and the server took about 60 ms to start answering. A capture turns "it feels slow" into numbers you can act on.

### Spotting a retransmission automatically

Capture a conversation where the server's response is lost and resent, and detect it by looking for the **same sequence number with data seen twice**:

```python
def find_retransmissions(packets):
    seen, retransmits = set(), []
    for timestamp, frame in packets:
        p = dissect(frame)
        if p["proto"] == "TCP" and p["payload"]:
            key = (p["src"], p["sport"], p["seq"], len(p["payload"]))
            if key in seen:
                retransmits.append((round(timestamp - packets[0][0], 3), p["src"], p["seq"]))
            seen.add(key)
    return retransmits

lossy = os.path.join(tempfile.mkdtemp(), "lossy.pcap")
write_pcap(lossy, conversation(retransmit_response=True))
print(find_retransmissions(read_pcap(capture_path)))             # []
print(find_retransmissions(read_pcap(lossy)))                    # [(0.337, '93.184.216.34', 5001)]      the server resent seq 5001 200 ms after the first try
```

Wireshark highlights these automatically (black rows: `tcp.analysis.retransmission`). A few retransmits are normal; **a steady 1 to 2 percent or bursts** point to a flaky link, Wi-Fi interference, an overloaded device or a bad cable.

### Spotting a reset

```python
reset_file = os.path.join(tempfile.mkdtemp(), "reset.pcap")
write_pcap(reset_file, conversation(reset_instead_of_close=True))
rst_packets = [(round(t - packets[0][0], 3), dissect(f)["src"]) for t, f in read_pcap(reset_file) if dissect(f)["proto"] == "TCP" and "R" in dissect(f)["flags"]]
print(rst_packets)                                               # [(0.187, '192.168.1.10')]    the client aborted instead of closing politely
```

Find out **who** sent the RST and **when** (right after a request? after a long idle period? always after exactly 60 seconds?): that points to the culprit (an application crash, an idle timeout in a firewall or load balancer, or an intrusion-prevention device).

## 6. tcpdump and Wireshark in practice

**Capturing needs privileges** (it puts the interface in a mode where you see all packets): `sudo tcpdump ...` on Linux/macOS, an administrator on Windows (Wireshark uses Npcap). **Capture only on networks you own or are authorized to monitor**, and treat captures as **sensitive**: they contain cookies, tokens and private data (unless encrypted).

```bash
sudo tcpdump -i any -nn -w capture.pcap port 443          # record all HTTPS traffic to a file (-w) for later analysis
sudo tcpdump -i en0 -nn -s 0 host 93.184.216.34           # live view, whole packets (-s 0), only traffic to or from one host
sudo tcpdump -i any -nn 'tcp[tcpflags] & (tcp-syn|tcp-rst) != 0'     # only SYN and RST packets: connection attempts and resets
sudo tcpdump -i any -nn udp port 53                       # all DNS traffic
sudo tcpdump -i any -nn -A port 80                        # print the ASCII payload (plain HTTP only!)
sudo tcpdump -i any -nn -c 100 -G 3600 -w 'cap-%H%M.pcap' # 100 packets / rotate a new file hourly
tcpdump -nn -r capture.pcap                               # read a file back (no sudo needed)
```

**BPF capture filters** (kernel-level, efficient, set *before* capturing):

| Filter | Matches |
|--------|---------|
| `host 10.0.0.5`, `src host ...`, `dst host ...` | traffic to/from an address |
| `net 10.0.0.0/24` | a subnet |
| `port 443`, `tcp port 80`, `udp port 53`, `portrange 8000-8100` | ports |
| `tcp`, `udp`, `icmp`, `arp` | protocols |
| `host A and port 443`, `not port 22`, `(tcp or udp) and port 53` | combinations (`and`, `or`, `not`, parentheses) |
| `tcp[tcpflags] & tcp-syn != 0` | packets with the SYN flag |
| `greater 1000` | packets longer than 1000 bytes |

**Wireshark** is the graphical analyzer: it dissects hundreds of protocols, colors problems, follows streams and graphs RTT and throughput. Its **display filters** (applied after capture, a different syntax from BPF) are very readable:

| Display filter | Shows |
|----------------|-------|
| `ip.addr == 192.168.1.10` | traffic to or from the host |
| `tcp.port == 443`, `udp.port == 53` | by port |
| `http`, `dns`, `tls`, `quic`, `http2` | a protocol |
| `dns.qry.name contains "example"` | DNS queries for a name |
| `tcp.flags.syn == 1 && tcp.flags.ack == 0` | connection attempts |
| `tcp.analysis.retransmission \|\| tcp.analysis.duplicate_ack` | trouble signs |
| `tcp.analysis.zero_window` | a receiver that cannot keep up |
| `http.response.code >= 400` | HTTP errors |
| `tls.handshake.type == 1` | TLS ClientHello (shows SNI and offered ciphers) |

Handy features: **Follow TCP Stream** (reassemble the whole conversation), **Statistics > Conversations / IO Graphs / Flow Graph**, **Expert Information** (all anomalies listed), **Export Objects > HTTP**, and **`tshark`**, the command-line Wireshark (`tshark -r cap.pcap -Y 'dns' -T fields -e dns.qry.name`).

### Looking inside TLS

HTTPS payload is encrypted, so a capture shows only handshake metadata (versions, SNI, certificate) and encrypted records. To **decrypt your own traffic** during debugging, tell the client to log its session keys and give the file to Wireshark:

```bash
export SSLKEYLOGFILE=$HOME/tls-keys.log     # Chrome, Firefox, curl, and Python's ssl module (3.8+) honor this variable
curl https://example.com/ > /dev/null
# Wireshark: Preferences > Protocols > TLS > (Pre)-Master-Secret log filename = ~/tls-keys.log   -> HTTP is now readable
```

(This works because you are the client and hold the keys; it does **not** let anyone decrypt traffic they merely captured, the whole point of [forward secrecy](../tls-security/01-cryptography-and-tls-lab.md).)

## 7. Measuring a request from the inside: where does the time go?

`curl` can print a timing breakdown with a format string; the same idea in Python is just timestamps around each phase:

```bash
curl -s -o /dev/null -w 'dns=%{time_namelookup}s connect=%{time_connect}s tls=%{time_appconnect}s ttfb=%{time_starttransfer}s total=%{time_total}s\n' https://example.com
# dns=0.012s connect=0.045s tls=0.110s ttfb=0.190s total=0.201s       (cumulative times: DNS, TCP handshake done, TLS done, first byte, finished)
```

```python
import http.server, threading, http.client

class Slow(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        time.sleep(0.15)                                          # a deliberately slow backend ("think time")
        body = b"done"
        self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Slow)
threading.Thread(target=server.serve_forever, daemon=True).start()
port = server.server_address[1]

def timing_breakdown(host, port, path="/"):
    marks = {}
    t0 = time.perf_counter()
    address = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)[0][4]       # DNS (loopback: instant)
    marks["dns"] = time.perf_counter() - t0
    sock = socket.create_connection(address)                                      # TCP handshake
    marks["connect"] = time.perf_counter() - t0
    sock.sendall(f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode())
    marks["request_sent"] = time.perf_counter() - t0
    first = sock.recv(1)                                                           # blocks until the first response byte arrives
    marks["first_byte"] = time.perf_counter() - t0
    while sock.recv(4096):
        pass
    marks["done"] = time.perf_counter() - t0
    sock.close()
    return marks

m = timing_breakdown("localhost", port)
phases = {"dns": m["dns"], "connect": m["connect"] - m["dns"], "server wait (ttfb)": m["first_byte"] - m["request_sent"], "download": m["done"] - m["first_byte"]}
print({k: f"{v * 1000:.0f} ms" for k, v in phases.items()})
# {'dns': '7 ms', 'connect': '0 ms', 'server wait (ttfb)': '156 ms', 'download': '0 ms'}       (exact numbers vary) the 150 ms we injected shows up as server wait
print(max(phases, key=phases.get))                              # server wait (ttfb)
server.shutdown(); server.server_close()
```

The **biggest bucket tells you where to look**: large DNS time (slow resolver or low TTL), large connect/TLS time (distance, no keep-alive, no TLS resumption), large time-to-first-byte (a slow backend or database), large download (a big response or little bandwidth).

## 8. Troubleshooting playbooks

**"The site is slow."** Get the breakdown (`curl -w`, browser DevTools **Network > Timing**). Slow DNS: try another resolver. Slow connect or TLS: check geography and whether keep-alive and HTTP/2 or 3 are used. Slow TTFB: it is the server: check its logs, the database, the [load balancer](../load-balancing-cdn/01-load-balancing-and-resilience-lab.md) health. Slow download: payload size and compression.

**"I cannot connect."** `nc -vz host port` and read the failure type (section 2): refused (service down or wrong port), timeout (firewall or routing), unreachable (no route). Check the service is **listening** on the right interface with `ss -ltnp` (listening on `127.0.0.1` only means remote hosts cannot reach it; you need `0.0.0.0`).

**"It works from my laptop but not from the server" or inside Docker/Kubernetes.** Compare **DNS** (`dig` from both places), **routes and firewalls/security groups**, **proxy environment variables** (`HTTPS_PROXY`), the **outbound IP** (`curl ifconfig.me`), and the **time** (certificates fail if the clock is wrong).

**"Intermittent failures and timeouts."** Capture on both ends and compare: do packets leave but never arrive (loss on the path)? Retransmission bursts? A particular backend behind a load balancer (check which IP the failing requests hit)? A **connection tracking table full** or **idle timeout** in a NAT/firewall (long-lived idle connections reset after N minutes: use TCP keepalives)?

**"Large requests hang but small ones work."** Classic **MTU / Path MTU Discovery** problem: packets over the path's MTU are dropped because ICMP "fragmentation needed" messages are blocked. Test: `ping -M do -s 1472 host` (Linux; `-D -s` on macOS) and lower the size until it passes; the usual fix is lowering the MTU or MSS (VPNs and tunnels are the usual cause).

**"TLS handshake fails."** `openssl s_client -connect host:443 -servername host` shows the certificate chain, the verification result and the negotiated protocol; check expiry (`-showcerts | openssl x509 -noout -dates`), hostname match (SNI), a missing intermediate certificate, or the client offering only old protocol versions.

**"DNS gives different answers."** Query each resolver directly (`dig @8.8.8.8`, `dig @your-resolver`), look at the **TTL** left (cached answers), `dig +trace` to see the authoritative answer, and remember browsers and the OS cache too ([DNS lab](../dns-http/02-dns-in-depth.md)).

## 9. A toolbox at a glance

| Tool | Use |
|------|-----|
| `ping`, `mtr`, `traceroute` | reachability, latency, loss per hop |
| `dig`, `nslookup`, `host` | DNS queries (`dig +short`, `+trace`, `@server`) |
| `curl -v`, `curl -w`, `httpie`, `wget --server-response` | HTTP and TLS details, timing |
| `nc` (netcat), `telnet` | test a raw TCP port, send text, listen on a port |
| `ss -tulpn`, `netstat -an`, `lsof -i :PORT` | which process listens or is connected where |
| `ip addr / route / neigh`, `ifconfig`, `route -n get default`, `arp -a` | interface, routes, neighbors |
| `openssl s_client`, `testssl.sh`, `sslscan` | TLS handshake, certificates, ciphers |
| `tcpdump`, `tshark`, Wireshark | packet capture and analysis |
| `iperf3` | measure raw bandwidth between two hosts |
| `nmap` | discover open ports (only on systems you own or are authorized to scan) |
| `socat`, `ncat`, `mitmproxy` | relay, proxy and inspect application traffic (HTTP debugging proxy) |
| Browser **DevTools > Network** | per-request timing, protocol (h2/h3), headers, payloads |

## 10. Two real-world examples

**Example 1: "Random 502s that nobody could reproduce."** Users saw occasional 502 errors from a reverse proxy. Logs showed "upstream prematurely closed connection" but no cause. A capture on the proxy host showed **RST packets from the backend arriving exactly 5 seconds after the last request** on a kept-alive connection: the backend's **keep-alive timeout (5 s) was shorter than the proxy's (60 s)**, so the proxy occasionally reused a connection the backend had just closed. Raising the backend timeout above the proxy's fixed the errors, a bug no log line would have revealed.

**Example 2: "Large uploads freeze over the VPN."** Small API calls worked, but uploads stalled forever. A capture showed full-size packets being **retransmitted over and over without any ACK**, while small ones got through: the VPN tunnel reduced the usable MTU, packets above it were dropped, and the ICMP error telling the sender to shrink them was blocked by a firewall. Clamping the TCP **MSS** at the tunnel endpoint fixed it immediately.

## 11. Common mistakes

- Debugging at the application layer first, when a `dig` or `nc -vz` would find the cause in seconds.
- Confusing **refused** (an RST: nothing listening) with **timeout** (silence: filtering or routing).
- Capturing on the wrong interface or with a wrong filter and concluding "no traffic" (use `-i any` first).
- Forgetting that **loopback** traffic and traffic inside a container or VM need the right capture point.
- Capturing without `-s 0` on old versions (truncated packets), or on a busy link without filters (huge files).
- Sharing a capture file without realizing it contains cookies, tokens and passwords.
- Reading relative sequence numbers as absolute ones, or blaming a retransmission on the wrong side.
- Blocking all ICMP "for security" (it breaks Path MTU Discovery).
- Concluding something from a **single** capture point: capture at **both ends** to see what was sent versus received.
- Treating a middlebox's RST as the server's behavior without checking who sent it (compare TTL values).

## 12. Practice

1. Which symptom points to a firewall silently dropping packets, and which to nothing listening on the port?
2. Use `analyze` on a capture where the server's `[S.]` arrives 200 ms after the `[S]`. What do you conclude about the path?
3. In `conversation()`, add a second DNS query and answer for `www.example.com`. Write the pcap, then use `read_pcap` and `analyze` to confirm 4 DNS-port packets.
4. Write a BPF filter and a Wireshark display filter for: "only HTTP traffic (port 80) from host 10.0.0.5".
5. How would you tell from a capture whether a connection ended with a **FIN** or a **RST**?
6. Using `find_retransmissions`, what retransmission delay do you observe, and what does a growing delay on repeated retransmissions suggest (look up *exponential backoff* for TCP)?
7. A user says "the site works on Wi-Fi but not over the mobile network". List three layers you would check first.
8. Why is capturing TLS traffic not enough to read it, and what lets you decrypt your own?

<details>
<summary>Solutions</summary>

1. Silent drops show up as a **timeout** (the SYN gets no reply at all). A closed port shows up as an immediate **connection refused**, an RST reply to the SYN.
2. The handshake RTT is 200 ms: a long or congested path (or a distant server), not a server-processing problem, because the SYN-ACK is generated by the kernel almost instantly. Every request will pay at least this per round trip.
3. ```python
   extra = conversation()
   query2 = struct.pack("!HHHHHH", 0x5678, 0x0100, 1, 0, 0, 0) + dns_name("www.example.com") + struct.pack("!HH", 1, 1)
   answer2 = (struct.pack("!HHHHHH", 0x5678, 0x8180, 1, 1, 0, 0) + dns_name("www.example.com") + struct.pack("!HH", 1, 1)
              + b"\xc0\x0c" + struct.pack("!HHIH", 1, 1, 300, 4) + socket.inet_aton(SERVER))
   t0 = extra[-1][0] + 0.1
   extra.append((t0, ethernet(CMAC, RMAC, ipv4(CLIENT, RESOLVER, 17, udp(CLIENT, RESOLVER, 53101, 53, query2), ident=20))))
   extra.append((t0 + 0.02, ethernet(RMAC, CMAC, ipv4(RESOLVER, CLIENT, 17, udp(RESOLVER, CLIENT, 53, 53101, answer2), ident=21))))
   path2 = os.path.join(tempfile.mkdtemp(), "two_dns.pcap"); write_pcap(path2, extra)
   print(sum(1 for _, f in read_pcap(path2) if dissect(f)["proto"] == "UDP"))      # 4
   ```
4. BPF: `src host 10.0.0.5 and tcp port 80` (use `dst port 80` for requests only). Wireshark: `ip.src == 10.0.0.5 && tcp.port == 80` (or simply `ip.src == 10.0.0.5 && http`).
5. Look at the flags of the last packets: a clean close shows `[F.]` from each side followed by an ACK; an abort shows `[R]` or `[R.]` (and then nothing). `find` the RST packets as in `rst_packets`.
6. ```python
   print(find_retransmissions(read_pcap(lossy)))           # [(0.337, '93.184.216.34', 5001)]  : first sent at 0.137 s, resent 0.2 s later
   ```
   TCP's retransmission timer **doubles** after each failed attempt (exponential backoff: 200 ms, 400 ms, 800 ms ...), so growing gaps between repeats of the same sequence number mean the packets keep getting lost and TCP is backing off, not that the server is slow.
7. (a) **DNS**: does the mobile resolver return the same (or any) address (`dig` from both networks)? (b) **Routing/IPv6**: does the site have an IPv6 record that the mobile path mishandles (`curl -4` vs `curl -6`)? (c) **MTU/proxies/filters**: carrier NAT, a transparent proxy or a smaller MTU (`ping -s`, `curl -v`). Also check TLS and that the carrier does not block the port.
8. TLS encrypts the payload, so a capture contains only handshake metadata and ciphertext. Setting `SSLKEYLOGFILE` makes your own client write its session secrets to a file which Wireshark uses to decrypt that session; third parties who only captured packets cannot, thanks to forward secrecy.

</details>

## 13. Check yourself

1. In what order do you check layers when debugging connectivity, and why?
2. How do "connection refused" and "connection timed out" differ on the wire?
3. What are the parts of a pcap file?
4. What do `[S]`, `[S.]`, `[.]`, `[P.]`, `[F.]` and `[R]` mean?
5. How do you find a retransmission in a capture?
6. What is the difference between a BPF capture filter and a Wireshark display filter?
7. How can you see where the time goes in an HTTP request?

<details>
<summary>Answers</summary>

1. Bottom-up (link, IP/DNS, route, TCP port, TLS, application) because each layer depends on the ones below; the first failing layer is where the problem is.
2. Refused: the host answers the SYN with an RST at once (nothing listening). Timed out: no reply at all (packets dropped by a firewall, a wrong address or a down host).
3. A 24-byte global header (magic, version, snaplen, link type) followed by records, each a 16-byte header (timestamps, captured and original lengths) and the packet bytes.
4. SYN, SYN-ACK, ACK, PSH+ACK (data to deliver now), FIN+ACK, RST.
5. The same sequence number carrying data appears again (sent twice from the same source); Wireshark marks it as `tcp.analysis.retransmission`.
6. A BPF filter is applied by the kernel before capture (limits what is recorded, terse syntax); a display filter is applied by Wireshark to an already captured file (rich protocol-aware syntax).
7. Time the phases (DNS, connect, TLS, time to first byte, download) with `curl -w`, browser DevTools or a small script, or compute them from a packet capture; the biggest bucket shows where to look.

</details>

[Back to networking](../README.md)
