# Packets, Addressing and Subnets (with Runnable Labs)

**Prerequisites:** [binary and hexadecimal](../../00-foundations/computer-basics/binary-and-data-representation.md), [what is an OS](../../06-operating-systems/00-what-is-an-operating-system.md), the [overview](README.md). **You will learn:** how data is wrapped in **layers** (encapsulation), what an **IP**, **UDP** and **TCP** header contains (by building and parsing real ones with `struct`), how a **checksum** catches errors, how **IP addresses, CIDR masks and subnets** work (with Python's `ipaddress` module), what a **port** is, and how a router decides where to send a packet. Everything runs locally; no internet needed.

## 1. In plain words

You send a message to a friend: you put the letter in an **envelope**, write the address, drop it in a **bag** the postal service puts in a **truck**. Each stage adds its own wrapper and only reads its own wrapper. Networks work identically: your data is wrapped by several layers, each adding a **header** (the address label for that layer).

```text
Application   HTTP request: "GET /index.html"
Transport     [TCP header: src port, dst port, sequence ...]  + HTTP data
Network       [IP header: src IP, dst IP, TTL ...]            + TCP segment
Link          [Ethernet header: src MAC, dst MAC]             + IP packet  + [trailer: CRC]
Physical      bits on a wire / radio waves
```

Names for the data unit at each layer: **message/data -> segment (TCP) or datagram (UDP) -> packet (IP) -> frame (Ethernet)**.

## 2. The layers and their jobs

| Layer (TCP/IP) | Job | Address used | Examples |
|----------------|-----|--------------|----------|
| **Application** | what the programs say | URL, names | HTTP, DNS, SMTP, SSH |
| **Transport** | talk to the right **program** on a host; (optionally) reliability | **port** (16 bits) | TCP, UDP |
| **Internet / Network** | route packets across networks | **IP address** | IPv4, IPv6, ICMP |
| **Link** | move a frame to the next device on the same local network | **MAC address** (48 bits) | Ethernet, Wi-Fi |

(The 7-layer **OSI model** splits "application" into application, presentation and session, and "link" into data link and physical; the 4-layer TCP/IP view is what real stacks implement.)

## 3. Lab 1: build an IPv4 header by hand

An IPv4 header is 20 bytes (without options). Let us pack one with `struct` (`!` means "network byte order" = big-endian):

```python
import struct, socket

def ip_checksum(data: bytes) -> int:
    """The Internet checksum: add all 16-bit words, fold the carry back in, invert."""
    if len(data) % 2:
        data += b"\x00"
    total = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return ~total & 0xFFFF

def build_ipv4_header(src, dst, payload_len, protocol=17, ttl=64, ident=0x1234):
    version_ihl = (4 << 4) | 5                                  # version 4, header length 5 words (20 bytes)
    total_length = 20 + payload_len
    header = struct.pack("!BBHHHBBH4s4s",
                         version_ihl, 0, total_length,
                         ident, 0,                               # identification, flags + fragment offset
                         ttl, protocol, 0,                       # time to live, protocol (17 = UDP, 6 = TCP), checksum placeholder
                         socket.inet_aton(src), socket.inet_aton(dst))
    checksum = ip_checksum(header)
    return header[:10] + struct.pack("!H", checksum) + header[12:]

header = build_ipv4_header("192.168.1.10", "93.184.216.34", payload_len=8)
print(len(header), header.hex())
# 20 4500001c1234000040117110c0a8010a5db8d822    (the 7110 is the computed checksum)
print(ip_checksum(header))                                      # 0    a header with a correct checksum sums to zero when re-checked
```

Now parse it back:

```python
def parse_ipv4_header(raw: bytes):
    (version_ihl, tos, total_length, ident, flags_frag,
     ttl, protocol, checksum, src, dst) = struct.unpack("!BBHHHBBH4s4s", raw[:20])
    return {
        "version": version_ihl >> 4,
        "header_bytes": (version_ihl & 0xF) * 4,
        "total_length": total_length,
        "ttl": ttl,
        "protocol": {1: "ICMP", 6: "TCP", 17: "UDP"}.get(protocol, protocol),
        "src": socket.inet_ntoa(src),
        "dst": socket.inet_ntoa(dst),
        "checksum_ok": ip_checksum(raw[:20]) == 0,
    }

print(parse_ipv4_header(header))
# {'version': 4, 'header_bytes': 20, 'total_length': 28, 'ttl': 64, 'protocol': 'UDP', 'src': '192.168.1.10', 'dst': '93.184.216.34', 'checksum_ok': True}

corrupted = bytearray(header); corrupted[8] ^= 0x01            # flip one bit in the TTL field
print(parse_ipv4_header(bytes(corrupted))["checksum_ok"])       # False   (the receiver detects the damage and drops the packet)
```

Important header fields:

| Field | Purpose |
|-------|---------|
| **TTL** (time to live) | decremented by each router; at 0 the packet is dropped, preventing endless loops (this is how `traceroute` works) |
| **Protocol** | which transport comes next (6 = TCP, 17 = UDP, 1 = ICMP) |
| **Source / destination IP** | who sent it, where it goes |
| **Checksum** | detects header corruption |
| **Identification, flags, offset** | reassembling **fragments** when a packet is too big for a link (the **MTU**, usually 1500 bytes) |

## 4. Lab 2: UDP and TCP headers

**UDP** is minimal: just 8 bytes (source port, destination port, length, checksum). It adds *ports* to IP and nothing else: no connection, no retransmission, no ordering.

```python
def build_udp(src_port, dst_port, payload: bytes):
    length = 8 + len(payload)
    return struct.pack("!HHHH", src_port, dst_port, length, 0) + payload      # checksum 0 = "not computed" (allowed in IPv4)

datagram = build_udp(54321, 53, b"hello")
src_port, dst_port, length, _ = struct.unpack("!HHHH", datagram[:8])
print(src_port, dst_port, length, datagram[8:])                 # 54321 53 13 b'hello'
```

**TCP** is richer: 20+ bytes with **sequence and acknowledgement numbers, flags, and a window**, which give reliable, ordered, flow-controlled streams.

```python
def parse_tcp(raw: bytes):
    src, dst, seq, ack, offset_flags, window, checksum, urgent = struct.unpack("!HHIIHHHH", raw[:20])
    flags = offset_flags & 0x1FF
    names = [n for n, bit in (("FIN", 0x01), ("SYN", 0x02), ("RST", 0x04), ("PSH", 0x08), ("ACK", 0x10), ("URG", 0x20)) if flags & bit]
    return {"src_port": src, "dst_port": dst, "seq": seq, "ack": ack, "flags": names, "window": window}

# the three packets of a TCP handshake (3-way handshake), as the headers would look:
syn     = struct.pack("!HHIIHHHH", 54321, 80, 1000, 0,    (5 << 12) | 0x02, 65535, 0, 0)
syn_ack = struct.pack("!HHIIHHHH", 80, 54321, 5000, 1001, (5 << 12) | 0x12, 65535, 0, 0)
ack     = struct.pack("!HHIIHHHH", 54321, 80, 1001, 5001, (5 << 12) | 0x10, 65535, 0, 0)
for name, packet in (("client -> server", syn), ("server -> client", syn_ack), ("client -> server", ack)):
    print(name, parse_tcp(packet))
# client -> server {'src_port': 54321, 'dst_port': 80, 'seq': 1000, 'ack': 0, 'flags': ['SYN'], 'window': 65535}
# server -> client {'src_port': 80, 'dst_port': 54321, 'seq': 5000, 'ack': 1001, 'flags': ['SYN', 'ACK'], 'window': 65535}
# client -> server {'src_port': 54321, 'dst_port': 80, 'seq': 1001, 'ack': 5001, 'flags': ['ACK'], 'window': 65535}
```

Read the handshake: the client says **SYN** ("I want to talk; my first byte number is 1000"); the server answers **SYN-ACK** ("OK, mine starts at 5000, and I expect your byte 1001 next"); the client confirms with **ACK**. Each side now knows the other is alive and where numbering starts. (We build the full conversation with real sockets in the [socket lab](02-sockets-tcp-udp-lab.md).)

| | TCP | UDP |
|---|-----|-----|
| Connection | yes (handshake) | no |
| Reliable and ordered | **yes** (retransmits, sequence numbers) | no |
| Flow and congestion control | yes | no |
| Header size | 20+ bytes | 8 bytes |
| Typical use | web, email, files, SSH | DNS, video calls, games, QUIC (HTTP/3) |

## 5. Ports: finding the right program

An IP address finds the **machine**; a **port** (0-65535) finds the **program** on it. A connection is identified by the **5-tuple**: `(protocol, source IP, source port, destination IP, destination port)`. That is why your browser can open 20 connections to the same server: each uses a different source port.

| Range | Meaning |
|-------|---------|
| 0-1023 | well-known (need privileges): 22 SSH, 53 DNS, 80 HTTP, 443 HTTPS, 25 SMTP |
| 1024-49151 | registered services: 3306 MySQL, 5432 PostgreSQL, 6379 Redis |
| 49152-65535 | **ephemeral** ports the OS gives to clients |

```python
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1", 0))                                         # port 0 = "OS, pick any free port"
print(s.getsockname()[0], 1024 <= s.getsockname()[1] <= 65535)   # 127.0.0.1 True
s.close()
print(socket.getservbyname("https"), socket.getservbyname("ssh"), socket.getservbyport(53, "udp"))      # 443 22 domain
```

## 6. IPv4 addresses, CIDR and subnets

An IPv4 address is **32 bits**, written as four bytes in decimal (`192.168.1.10`). It has two parts: a **network prefix** (which network) and a **host part** (which device on it). **CIDR notation** `192.168.1.0/24` says "the first **24** bits are the network".

```python
import ipaddress

net = ipaddress.ip_network("192.168.1.0/24")
print(net.netmask, net.num_addresses, net.network_address, net.broadcast_address)
# 255.255.255.0 256 192.168.1.0 192.168.1.255
print(list(net.hosts())[0], list(net.hosts())[-1], len(list(net.hosts())))        # 192.168.1.1 192.168.1.254 254
print(ipaddress.ip_address("192.168.1.77") in net, ipaddress.ip_address("192.168.2.1") in net)      # True False
print(f"{int(ipaddress.ip_address('192.168.1.10')):032b}")      # 11000000101010000000000100001010
```

Usable hosts = `2^(32 - prefix) - 2` (one address is the network id, one the broadcast).

| Prefix | Mask | Addresses | Typical use |
|--------|------|-----------|-------------|
| /8 | 255.0.0.0 | 16 777 216 | huge (10.0.0.0/8) |
| /16 | 255.255.0.0 | 65 536 | large site |
| /24 | 255.255.255.0 | 256 | a home or office LAN |
| /30 | 255.255.255.252 | 4 | point-to-point link |
| /32 | 255.255.255.255 | 1 | a single host |

### Splitting a network (subnetting)

Give each department its own subnet by borrowing host bits:

```python
office = ipaddress.ip_network("10.20.0.0/22")                   # 1024 addresses
for sub in office.subnets(new_prefix=24):                      # four /24 subnets
    print(sub, sub.num_addresses - 2, "hosts")
# 10.20.0.0/24 254 hosts
# 10.20.1.0/24 254 hosts
# 10.20.2.0/24 254 hosts
# 10.20.3.0/24 254 hosts

# Do two addresses need a router to talk? Only if they are on different subnets.
def same_subnet(a, b, prefix):
    return ipaddress.ip_interface(f"{a}/{prefix}").network == ipaddress.ip_interface(f"{b}/{prefix}").network

print(same_subnet("10.20.1.5", "10.20.1.200", 24), same_subnet("10.20.1.5", "10.20.2.5", 24))      # True False
print(ipaddress.ip_network("10.20.0.0/24").overlaps(ipaddress.ip_network("10.20.0.128/25")))      # True
print(list(ipaddress.collapse_addresses([ipaddress.ip_network("10.0.0.0/25"), ipaddress.ip_network("10.0.0.128/25")])))
# [IPv4Network('10.0.0.0/24')]     (two adjacent /25 networks merge into one /24: route aggregation)
```

### Private and special ranges

```python
for ip in ("10.1.2.3", "172.16.0.9", "192.168.0.1", "127.0.0.1", "169.254.1.1", "8.8.8.8"):
    a = ipaddress.ip_address(ip)
    print(f"{ip:12} private={a.is_private!s:5} loopback={a.is_loopback!s:5} link_local={a.is_link_local}")
# 10.1.2.3     private=True  loopback=False link_local=False
# 172.16.0.9   private=True  loopback=False link_local=False
# 192.168.0.1  private=True  loopback=False link_local=False
# 127.0.0.1    private=True  loopback=True  link_local=False
# 169.254.1.1  private=True  loopback=False link_local=True
# 8.8.8.8      private=False loopback=False link_local=False
```

- **Private ranges** (`10/8`, `172.16/12`, `192.168/16`) are not routed on the public internet; your home router uses **NAT** to share one public address among all devices.
- **127.0.0.1** (loopback / `localhost`) is "this machine".
- **169.254.x.x** is self-assigned when DHCP fails.

## 7. IPv6 in one minute

IPv4 has only about 4.3 billion addresses, which ran out. **IPv6** uses **128-bit** addresses (`2001:db8::1`), enough for every grain of sand to have billions of addresses, and drops NAT, fragmentation by routers and header checksums.

```python
v6 = ipaddress.ip_address("2001:0db8:0000:0000:0000:0000:0000:0001")
print(v6.compressed, v6.exploded[:19])                          # 2001:db8::1 2001:0db8:0000:0000
print(ipaddress.ip_network("2001:db8::/32").num_addresses == 2 ** 96)       # True
```

## 8. How a router decides: longest prefix match

A router holds a **routing table** of `(prefix -> next hop)`. For each packet it picks the **most specific** (longest) prefix that contains the destination.

```python
routes = [
    (ipaddress.ip_network("0.0.0.0/0"),       "ISP gateway (default route)"),
    (ipaddress.ip_network("10.0.0.0/8"),      "corporate VPN"),
    (ipaddress.ip_network("10.20.0.0/16"),    "data center A"),
    (ipaddress.ip_network("10.20.5.0/24"),    "rack 5 switch"),
]

def route(destination):
    ip = ipaddress.ip_address(destination)
    matches = [(net, hop) for net, hop in routes if ip in net]
    return max(matches, key=lambda m: m[0].prefixlen)[1]

for dst in ("10.20.5.77", "10.20.9.1", "10.99.0.1", "8.8.4.4"):
    print(f"{dst:11} -> {route(dst)}")
# 10.20.5.77  -> rack 5 switch
# 10.20.9.1   -> data center A
# 10.99.0.1   -> corporate VPN
# 8.8.4.4     -> ISP gateway (default route)
```

Each router along the way repeats this lookup, decrements the TTL, and forwards the packet to the next hop. Core internet routers do this for about a million prefixes (BGP routes) at billions of packets per second using specialized tries and hardware.

The same idea, solved with a [trie](../../02-data-structures/tries/01-tries.md) over address bits, gives `O(32)` lookups regardless of table size.

## 9. Two real-world examples

**Example 1: `ping` and `traceroute`.** `ping` sends an ICMP echo request and times the reply. `traceroute` sends packets with TTL 1, 2, 3, ...; each router that drops one (TTL reaches 0) replies "time exceeded", revealing the route hop by hop.

**Example 2: Your home network.** The router gives your devices private addresses via **DHCP** (e.g. `192.168.1.x/24`), has one public address from the ISP, and **NAT** rewrites source addresses and ports so replies find the right device. That is why you cannot connect *to* a laptop at home from outside without port forwarding.

## 10. Common mistakes

- Forgetting network byte order (big-endian) when packing headers (`!` in `struct`).
- Confusing IP address (host) with port (program) and with MAC address (local hop).
- Using `/24` arithmetic out of habit for other prefixes (compute with `ipaddress`).
- Counting the network and broadcast addresses as usable hosts.
- Assuming UDP gives reliability or ordering.
- Treating "private IP" as "secure"; it only means "not publicly routable".

## 11. Practice

1. How many usable hosts are in `/26`? In `/30`?
2. Is `192.168.5.130` inside `192.168.5.0/25`? Inside `192.168.5.128/25`?
3. Split `172.16.0.0/16` into four equal subnets; list them.
4. Which route would `10.20.5.9` use in the routing table above if the `/24` entry were removed?
5. What does TTL protect against?
6. Why does TCP need a handshake but UDP does not?
7. Write `is_valid_ipv4(text)` without regex, using the `ipaddress` module.

<details>
<summary>Solutions</summary>

1. `/26`: `2^6 - 2 = 62` hosts; `/30`: `2^2 - 2 = 2`.
   ```python
   print(ipaddress.ip_network("10.0.0.0/26").num_addresses - 2, ipaddress.ip_network("10.0.0.0/30").num_addresses - 2)      # 62 2
   ```
2. `/25` splits the last octet at 128: `.0-.127` and `.128-.255`. So no, then yes.
   ```python
   ip = ipaddress.ip_address("192.168.5.130")
   print(ip in ipaddress.ip_network("192.168.5.0/25"), ip in ipaddress.ip_network("192.168.5.128/25"))      # False True
   ```
3. ```python
   print([str(n) for n in ipaddress.ip_network("172.16.0.0/16").subnets(new_prefix=18)])
   # ['172.16.0.0/18', '172.16.64.0/18', '172.16.128.0/18', '172.16.192.0/18']
   ```
4. It would match `10.20.0.0/16` (longest remaining match): "data center A".
5. Packets circling forever in routing loops: each hop decrements TTL and a packet at zero is discarded.
6. TCP promises reliable ordered delivery, so both sides must agree on initial sequence numbers and that the peer exists; UDP just sends datagrams with no state.
7. ```python
   def is_valid_ipv4(text):
       try:
           ipaddress.IPv4Address(text)
           return True
       except ValueError:
           return False
   print(is_valid_ipv4("192.168.1.1"), is_valid_ipv4("256.1.1.1"), is_valid_ipv4("1.2.3"))      # True False False
   ```

</details>

## 12. Check yourself

1. What does each layer's header add and who reads it?
2. What is a port and what is the 5-tuple?
3. What does `/20` mean and how many addresses does it hold?
4. How does a router choose among overlapping routes?
5. What is the checksum for?
6. Why does NAT exist?

<details>
<summary>Answers</summary>

1. Addressing/control information for that layer, read only by the matching layer on the other side (and by devices operating at that layer).
2. A 16-bit number identifying a program on a host; the 5-tuple (protocol, source IP, source port, destination IP, destination port) uniquely identifies a connection.
3. The first 20 bits are the network prefix; `2^12 = 4096` addresses.
4. Longest prefix match: the most specific route wins.
5. Detecting corruption in transit; a bad checksum causes the packet to be dropped.
6. To share one public IPv4 address among many private devices, a workaround for IPv4 address exhaustion.

</details>

[Back to TCP/IP and OSI](README.md) · Next: [sockets lab: TCP and UDP](02-sockets-tcp-udp-lab.md)
