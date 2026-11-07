# DNS in Depth: Wire Format, a Toy Server, Caching and Resolution

**Prerequisites:** [sockets lab](../tcp-ip-osi/02-sockets-tcp-udp-lab.md) (UDP), [packets and addressing](../tcp-ip-osi/01-packets-addressing-and-subnets.md), [HTTP from scratch](01-http-from-scratch.md). **You will learn:** how **DNS** turns names into IP addresses, the **record types** (A, AAAA, CNAME, MX, TXT, NS), the **resolution hierarchy** (root, TLD, authoritative) and **caching with TTLs**, and (by building them) the actual **DNS packet format**, a working **DNS server on UDP**, and a **caching resolver**. All local; no internet required.

## 1. In plain words

Humans remember `example.com`; routers need `93.184.216.34`. **DNS (Domain Name System)** is the distributed phone book that translates one into the other. It is **hierarchical** (no single machine knows everything), **cached heavily** (so most lookups never leave your network) and mostly runs over **UDP port 53** (TCP for large answers; DNS over HTTPS/TLS for privacy).

```text
Your browser -> OS -> recursive resolver (ISP / 8.8.8.8 / 1.1.1.1)
                         |-- asks a ROOT server:      "who handles .com?"       -> a .com TLD server
                         |-- asks the .com TLD:       "who handles example.com?" -> example.com's name server
                         |-- asks the AUTHORITATIVE:  "what is www.example.com?" -> 93.184.216.34
                      (the resolver caches every answer for its TTL)
```

## 2. Names, zones and record types

A name reads **right to left**: `www.example.com.` is `.` (root) -> `com` -> `example` -> `www`. Each level is managed by someone: a **zone** is the part of the tree one set of name servers is **authoritative** for.

| Record | Maps | Example |
|--------|------|---------|
| **A** | name to **IPv4** address | `example.com -> 93.184.216.34` |
| **AAAA** | name to **IPv6** address | `example.com -> 2606:2800:...` |
| **CNAME** | alias to another **name** | `www.example.com -> example.com` |
| **MX** | where to deliver **mail**, with priorities | `example.com -> 10 mail.example.com` |
| **NS** | the zone's **name servers** | `example.com -> ns1.example.net` |
| **TXT** | free text (SPF/DKIM email policy, domain verification) | `"v=spf1 include:_spf.google.com ~all"` |
| **PTR** | **reverse**: IP address to name | `34.216.184.93.in-addr.arpa -> example.com` |
| **SOA** | zone administration data | serial number, refresh timers |

Each record has a **TTL** (time to live): how many seconds a resolver may cache it. Low TTL (60 s) means changes spread fast but cost more lookups; high TTL (24 h) is cheaper but slow to change.

```python
import socket

print(socket.gethostbyname("localhost"))                         # 127.0.0.1
print(sorted({info[4][0] for info in socket.getaddrinfo("localhost", 80, type=socket.SOCK_STREAM)}))
# ['127.0.0.1', '::1']   (localhost has both an IPv4 and an IPv6 address)
```

## 3. Lab 1: the DNS packet format

Every DNS message (query and response) has a 12-byte **header** followed by sections. We build a query for an `A` record with `struct`.

```text
Header (12 bytes): ID | flags | #questions | #answers | #authority | #additional
Question:  QNAME (labels) | QTYPE | QCLASS
Answer:    NAME | TYPE | CLASS | TTL | RDLENGTH | RDATA
```

A name is stored as a sequence of **length-prefixed labels** ending with a zero byte: `www.example.com` becomes `3www7example3com0`.

```python
import struct

def encode_name(name: str) -> bytes:
    out = b""
    for label in name.rstrip(".").split("."):
        out += bytes([len(label)]) + label.encode()
    return out + b"\x00"

def build_query(name, qtype=1, ident=0xBEEF):                    # qtype 1 = A, 28 = AAAA, 15 = MX, 16 = TXT, 5 = CNAME
    header = struct.pack("!HHHHHH", ident, 0x0100, 1, 0, 0, 0)  # flags 0x0100: "recursion desired"
    return header + encode_name(name) + struct.pack("!HH", qtype, 1)       # class 1 = IN (Internet)

print(encode_name("www.example.com"))                            # b'\x03www\x07example\x03com\x00'
query = build_query("www.example.com")
print(len(query), query.hex())
# 33 beef0100000100000000000003777777076578616d706c6503636f6d0000010001
```

Parsing a name must handle **compression**: to save space, a repeated name is replaced by a 2-byte **pointer** (`11` in the top two bits, then a 14-bit offset to an earlier occurrence).

```python
def decode_name(message: bytes, offset: int):
    labels, jumped, end = [], False, offset
    while True:
        length = message[offset]
        if length == 0:
            offset += 1
            break
        if length & 0xC0 == 0xC0:                                # a compression pointer
            pointer = ((length & 0x3F) << 8) | message[offset + 1]
            if not jumped:
                end = offset + 2                                 # the name ends here in the stream, even though we jump away
            offset, jumped = pointer, True
            continue
        labels.append(message[offset + 1: offset + 1 + length].decode())
        offset += 1 + length
    return ".".join(labels), (end if jumped else offset)

def parse_message(msg: bytes):
    ident, flags, qd, an, ns, ar = struct.unpack("!HHHHHH", msg[:12])
    offset, questions, answers = 12, [], []
    for _ in range(qd):
        name, offset = decode_name(msg, offset)
        qtype, qclass = struct.unpack("!HH", msg[offset: offset + 4]); offset += 4
        questions.append((name, qtype))
    for _ in range(an):
        name, offset = decode_name(msg, offset)
        rtype, rclass, ttl, rdlen = struct.unpack("!HHIH", msg[offset: offset + 10]); offset += 10
        rdata = msg[offset: offset + rdlen]
        if rtype == 1:
            value = socket.inet_ntoa(rdata)                      # A record: 4 bytes
        elif rtype == 5:
            value = decode_name(msg, offset)[0]                  # CNAME: a name (possibly compressed)
        elif rtype == 16:
            value = rdata[1:1 + rdata[0]].decode()               # TXT: length-prefixed string
        else:
            value = rdata.hex()
        offset += rdlen
        answers.append({"name": name, "type": rtype, "ttl": ttl, "value": value})
    return {"id": hex(ident), "is_response": bool(flags & 0x8000), "rcode": flags & 0xF,
            "questions": questions, "answers": answers}

print(parse_message(query))
# {'id': '0xbeef', 'is_response': False, 'rcode': 0, 'questions': [('www.example.com', 1)], 'answers': []}
```

**Building a response by hand** (with a pointer back to the question name, as real servers do):

```python
def build_response(query_msg, answers):
    """answers: list of (type, ttl, rdata_bytes). Echo the question; point each answer's name at offset 12."""
    ident = struct.unpack("!H", query_msg[:2])[0]
    flags = 0x8180 if answers else 0x8183                        # response + recursion available; rcode 3 = NXDOMAIN (name does not exist)
    header = struct.pack("!HHHHHH", ident, flags, 1, len(answers), 0, 0)
    question = query_msg[12:]
    body = b""
    for rtype, ttl, rdata in answers:
        body += struct.pack("!H", 0xC00C)                        # pointer to the name at offset 12 (the question)
        body += struct.pack("!HHIH", rtype, 1, ttl, len(rdata)) + rdata
    return header + question + body

response = build_response(query, [(1, 300, socket.inet_aton("93.184.216.34"))])
print(parse_message(response))
# {'id': '0xbeef', 'is_response': True, 'rcode': 0, 'questions': [('www.example.com', 1)], 'answers': [{'name': 'www.example.com', 'type': 1, 'ttl': 300, 'value': '93.184.216.34'}]}
print(len(response), "bytes; the answer's name took only 2 bytes thanks to compression")
# 49 bytes; the answer's name took only 2 bytes thanks to compression
print(parse_message(build_response(query, []))["rcode"])         # 3     (NXDOMAIN: no such domain)
```

## 4. Lab 2: a working DNS server over UDP

A tiny **authoritative server** with a zone dictionary, answering real UDP packets on loopback:

```python
import threading

TXT_VALUE = b"verify=abc123xyz!"
ZONE = {
    ("www.shop.test", 1): [(300, socket.inet_aton("10.0.0.5"))],
    ("api.shop.test", 1): [(60, socket.inet_aton("10.0.0.6")), (60, socket.inet_aton("10.0.0.7"))],     # two A records: a simple load spread
    ("shop.test", 16): [(3600, bytes([len(TXT_VALUE)]) + TXT_VALUE)],                                   # TXT data is length-prefixed
}

queries_served = {"count": 0}

def dns_server(sock, stop):
    sock.settimeout(0.1)
    while not stop.is_set():
        try:
            data, addr = sock.recvfrom(512)                      # classic DNS messages over UDP are at most 512 bytes
        except socket.timeout:
            continue
        queries_served["count"] += 1
        name, offset = decode_name(data, 12)
        qtype = struct.unpack("!H", data[offset: offset + 2])[0]
        records = ZONE.get((name, qtype), [])
        sock.sendto(build_response(data, [(qtype, ttl, rdata) for ttl, rdata in records]), addr)

dns_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dns_sock.bind(("127.0.0.1", 0))
DNS_ADDR = dns_sock.getsockname()
stop_dns = threading.Event()
server_thread = threading.Thread(target=dns_server, args=(dns_sock, stop_dns), daemon=True); server_thread.start()

def lookup(name, qtype=1, server=DNS_ADDR, timeout=1.0):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    try:
        s.sendto(build_query(name, qtype), server)
        data, _ = s.recvfrom(512)
        return parse_message(data)
    finally:
        s.close()

reply = lookup("api.shop.test")
print([(a["value"], a["ttl"]) for a in reply["answers"]])        # [('10.0.0.6', 60), ('10.0.0.7', 60)]
print(lookup("shop.test", 16)["answers"][0]["value"])            # verify=abc123xyz!
print(lookup("nothing.shop.test")["rcode"])                      # 3    (NXDOMAIN)
```

Notice: **no connection, one datagram each way**. That is why DNS is fast, and why it must handle loss itself: resolvers **retry** with timeouts.

## 5. Lab 3: a caching resolver (TTL)

Most lookups are answered from a cache. Our resolver stores each answer until `ttl` seconds pass.

```python
import time

class CachingResolver:
    def __init__(self, upstream, clock=time.monotonic):
        self.upstream, self.cache, self.clock = upstream, {}, clock
        self.hits = self.misses = 0

    def resolve(self, name, qtype=1):
        key = (name, qtype)
        entry = self.cache.get(key)
        if entry and entry["expires"] > self.clock():
            self.hits += 1
            return entry["answers"]
        self.misses += 1
        reply = lookup(name, qtype, server=self.upstream)
        answers = [a["value"] for a in reply["answers"]]
        ttl = min((a["ttl"] for a in reply["answers"]), default=30)       # negative answers are cached briefly too
        self.cache[key] = {"answers": answers, "expires": self.clock() + ttl}
        return answers

fake_time = {"now": 1000.0}
resolver = CachingResolver(DNS_ADDR, clock=lambda: fake_time["now"])
served_before = queries_served["count"]

print(resolver.resolve("www.shop.test"))                          # ['10.0.0.5']    (miss: the server is asked)
print(resolver.resolve("www.shop.test"))                          # ['10.0.0.5']    (hit: answered from cache)
fake_time["now"] += 299
resolver.resolve("www.shop.test")                                 # still within the 300 s TTL: hit
fake_time["now"] += 2
resolver.resolve("www.shop.test")                                 # TTL expired: miss, asks again
print(resolver.hits, resolver.misses, queries_served["count"] - served_before)      # 2 2 2
```

This is **TTL** in action: of four lookups only two reached the server. Real resolvers also cache **negative answers** (NXDOMAIN), and **browsers and the OS cache too**, so a DNS change can appear to take effect at different times for different users: **lower the TTL before a planned migration** (to 60 s a day ahead), then raise it afterward.

## 6. Simulating the full resolution walk

A fresh recursive resolver with an empty cache follows **referrals** down the hierarchy. We model the three levels of servers as dictionaries:

```python
ROOT = {"com": "tld-com-server", "org": "tld-org-server"}
TLD = {"tld-com-server": {"example.com": "ns1.example.com"}, "tld-org-server": {"wikipedia.org": "ns1.wikipedia.org"}}
AUTH = {"ns1.example.com": {"www.example.com": "93.184.216.34", "mail.example.com": "93.184.216.35"},
        "ns1.wikipedia.org": {"en.wikipedia.org": "208.80.154.224"}}

def recursive_resolve(name, trace):
    tld = name.split(".")[-1]
    trace.append(f"ask ROOT about {name!r}: refer to {ROOT[tld]}")
    server = ROOT[tld]
    domain = ".".join(name.split(".")[-2:])
    trace.append(f"ask {server} about {name!r}: refer to {TLD[server][domain]}")
    auth = TLD[server][domain]
    answer = AUTH[auth][name]
    trace.append(f"ask {auth} about {name!r}: answer {answer}")
    return answer

trace = []
print(recursive_resolve("www.example.com", trace))               # 93.184.216.34
print(*trace, sep="\n")
# ask ROOT about 'www.example.com': refer to tld-com-server
# ask tld-com-server about 'www.example.com': refer to ns1.example.com
# ask ns1.example.com about 'www.example.com': answer 93.184.216.34
```

Three round trips for a cold lookup, zero for a cached one. There are **13 root server addresses** (letters A to M), each replicated worldwide using **anycast** (many machines sharing one IP; routing sends you to the nearest). Recursive resolvers cache the root and TLD referrals for a long time, so they rarely ask the root at all.

## 7. DNS in practice: tools and uses

```bash
dig example.com A +short            # query an A record
dig example.com MX                  # mail servers
dig +trace example.com              # watch the whole walk from the root
dig @1.1.1.1 example.com            # ask a specific resolver
dig -x 93.184.216.34                # reverse lookup (PTR)
nslookup example.com                # the older, simpler tool
```

- **Load balancing and failover:** return several A records (round-robin DNS) or answer by the client's location (GeoDNS); short TTLs allow failover.
- **Email:** MX records pick the mail server; **SPF/DKIM/DMARC** TXT records fight spoofing.
- **Domain verification:** services ask you to publish a TXT record to prove ownership.
- **CDNs** are reached by CNAMEs (`www.shop.com -> shop.cdn-provider.net`).
- **Service discovery** inside companies (Kubernetes `my-service.default.svc.cluster.local`, Consul).

### CNAME rules

A name with a CNAME **cannot** have other records (so you cannot put a CNAME at the zone apex `example.com`, which needs NS/SOA/MX); many providers offer an "ALIAS/ANAME" workaround. Following a CNAME chain costs extra lookups.

## 8. Security and privacy

| Issue | What happens | Defense |
|-------|--------------|---------|
| **Cache poisoning** | an attacker injects a fake answer into a resolver's cache | random IDs and source ports, **DNSSEC** (signed records) |
| **Spoofing / hijacking** | a forged response redirects victims | DNSSEC, TLS (a certificate check at the destination still catches it) |
| **Amplification DDoS** | small spoofed UDP queries trigger large responses to a victim | response rate limiting, closing open resolvers |
| **Privacy** | plain DNS shows every domain you look up | **DoH** (DNS over HTTPS) / **DoT** (over TLS) |
| **Typosquatting, DNS tunneling** | lookalike domains; data smuggled in query names | filtering, monitoring |

## 9. Two real-world examples

**Example 1: The October 2016 Dyn outage.** A botnet flooded the DNS provider Dyn; sites such as Twitter, GitHub and Netflix were unreachable even though their servers were fine: with the phone book down, nobody could find them. Lesson: use **multiple DNS providers** and sensible TTLs.

**Example 2: Zero-downtime migration.** To move a site to a new server you lower the A record's TTL to 60 s a day before, switch the IP, watch traffic move within minutes, and raise the TTL again. A forgotten 24-hour TTL would leave half your users on the old server for a day.

## 10. Common mistakes

- Forgetting that DNS answers are **cached** at several levels (resolver, OS, browser, application) when debugging "it still goes to the old server".
- Setting a huge TTL right before a change.
- Putting a CNAME at the zone apex or alongside other record types.
- Blocking UDP/53 but not TCP/53 (or vice versa); large answers fall back to TCP.
- Treating a failed lookup as permanent (it may be a timeout; retry with back-off).
- Hard-coding IP addresses instead of names (or caching resolved IPs forever in long-running programs).
- Confusing the **recursive resolver** (asks on your behalf, caches) with an **authoritative server** (owns the data).

## 11. Practice

1. Encode `mail.example.org` as a DNS name by hand (length-prefixed labels).
2. Why does the response use `0xC00C` for each answer's name?
3. With TTL 300, you query at `t=0`, `t=100`, `t=299`, `t=301`. Which of these reach the server?
4. Add a CNAME to the toy zone and have the resolver follow it (describe the steps).
5. A record has TTL 86400 and you must change it now. What are your options?
6. Why can DNS responses be used in amplification attacks and what is the mitigation?
7. Parse the `rcode` of a response for a nonexistent name.

<details>
<summary>Solutions</summary>

1. `4mail7example3org0`, i.e. `b'\x04mail\x07example\x03org\x00'`.
   ```python
   print(encode_name("mail.example.org"))                         # b'\x04mail\x07example\x03org\x00'
   ```
2. A compression pointer (`11` + offset 12) refers back to the question name at byte 12 of the message, saving the full name's bytes.
3. `t=0` (miss) and `t=301` (expired). `t=100` and `t=299` are within the TTL, so they are answered from the cache.
4. Store `("www.shop.test", 5): target name`; when the resolver gets a CNAME answer it issues a second lookup for the target name and returns the final A records (watch out for loops: limit the chain length).
5. Contact the resolvers' operators (hard), accept that the change spreads over up to a day, serve the old and new endpoint simultaneously during the transition, and lower TTLs earlier next time.
6. A tiny query with a **spoofed source address** (the victim's) elicits a much larger response sent to the victim. Mitigations: rate-limit responses, do not run open resolvers, ingress filtering (BCP 38), prefer DNS cookies/TCP for large answers.
7. ```python
   print(lookup("missing.shop.test")["rcode"])                    # 3
   ```

</details>

## 12. Check yourself

1. What are the three kinds of servers involved in a cold lookup?
2. What does TTL control and what is the trade-off of a low TTL?
3. What is an NS record? A CNAME? An MX?
4. Why is DNS usually over UDP?
5. What is DNSSEC and what problem does it address?
6. How would you debug "my users still hit the old IP after the DNS change"?

<details>
<summary>Answers</summary>

1. Root, TLD, authoritative name servers (all reached through a recursive resolver).
2. How long answers may be cached; a low TTL makes changes propagate faster but increases query load and lookup latency.
3. NS: the zone's name servers; CNAME: an alias to another name; MX: the mail servers for a domain (with priorities).
4. A single small request/response is faster and cheaper than a TCP handshake; reliability is handled by timeouts and retries (TCP is used for large responses).
5. Digitally signing DNS records so resolvers can verify they are authentic, preventing forged answers and cache poisoning.
6. Check remaining TTL (`dig` shows it), whether resolvers/OS/browser caches or the application cached the IP, and whether other records (CNAME chains, AAAA) still point to the old address.

</details>

## 13. Shut down the toy server

```python
stop_dns.set(); server_thread.join(timeout=1)
dns_sock.close()
print(not server_thread.is_alive())                              # True
```

[Back to DNS and HTTP](README.md) · Previous: [HTTP from scratch](01-http-from-scratch.md)
