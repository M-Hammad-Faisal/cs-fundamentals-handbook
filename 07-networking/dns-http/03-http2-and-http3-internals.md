# HTTP/2 and HTTP/3 Internals

**Prerequisites:** [HTTP from scratch](01-http-from-scratch.md), [sockets lab](../tcp-ip-osi/02-sockets-tcp-udp-lab.md) (TCP vs UDP), [cryptography and TLS lab](../tls-security/01-cryptography-and-tls-lab.md), [packets and headers](../tcp-ip-osi/01-packets-addressing-and-subnets.md) (`struct`). **You will learn:** why HTTP/1.1 is slow for modern pages (**head-of-line blocking**, six connections, the hacks it caused); how **HTTP/2** fixes it with **binary frames, streams and multiplexing**, **HPACK header compression** (implemented here and checked byte-for-byte against the RFC's examples), and **flow control**; why HTTP/2 over TCP still suffers **transport-level head-of-line blocking**; how **HTTP/3 over QUIC** (UDP) removes it, merges the TLS handshake in, supports **connection migration** and **0-RTT**; how clients and servers **negotiate the version (ALPN)**; and what all this changes for how you build sites. Everything is built or simulated in Python; the official test vectors catch mistakes.

## 1. Why HTTP/1.1 hurts

HTTP/1.1 carries **one request at a time per connection**: send a request, wait for the response, then send the next. Pipelining was defined but broken in practice. A modern page needs 50 to 100 resources (HTML, CSS, scripts, images, fonts, API calls), so:

- Browsers open **up to 6 parallel connections per host** (each costs a TCP and TLS handshake and its own congestion window).
- On each connection, a **slow or large response blocks everything queued behind it**: **HTTP-level head-of-line (HOL) blocking**.
- Headers (cookies, user agent, accept lists) are repeated **uncompressed in every request**: 500 to 2000 bytes each, sometimes larger than the response.

Developers invented workarounds: **domain sharding** (more hostnames, more connections), **CSS sprites** and **bundling** (fewer requests), **inlining**. HTTP/2 makes most of these unnecessary or even harmful.

A tiny model of the latency cost (it ignores many real effects, but shows the shape): each connection serves one request per round trip, and all bytes share the same bottleneck bandwidth.

```python
import math

def page_load_seconds(resources, size_bytes, rtt, bandwidth_bps, protocol):
    total_transfer = resources * size_bytes * 8 / bandwidth_bps          # time to push all bytes through the link
    if protocol == "http1":
        rounds = math.ceil(resources / 6)                                # 6 connections, one request at a time on each
    else:
        rounds = 1                                                       # HTTP/2: all requests are sent at once on one connection
    return rounds * rtt + total_transfer

for n in (10, 60, 120):
    h1 = page_load_seconds(n, 20_000, rtt=0.100, bandwidth_bps=10_000_000, protocol="http1")
    h2 = page_load_seconds(n, 20_000, rtt=0.100, bandwidth_bps=10_000_000, protocol="http2")
    print(f"{n:4} resources: HTTP/1.1 {h1:.2f}s   HTTP/2 {h2:.2f}s")
#   10 resources: HTTP/1.1 0.36s   HTTP/2 0.26s
#   60 resources: HTTP/1.1 1.96s   HTTP/2 1.06s
#  120 resources: HTTP/1.1 3.92s   HTTP/2 2.02s
```

The saving is the **waiting rounds**, not bandwidth: when latency (RTT) is high or there are many small resources, multiplexing matters most. (Bandwidth-bound downloads of one large file do not speed up.)

## 2. HTTP/2 in one picture

HTTP/2 (2015, RFC 9113) keeps HTTP's **meaning** (methods, status codes, headers, URLs) but changes how it is **sent**:

```text
ONE TCP connection (with TLS)
  ├─ stream 1: GET /index.html      ──► response frames ... ... ...
  ├─ stream 3: GET /style.css       ──► response frames ... ...
  └─ stream 5: GET /app.js          ──► response frames ... ... ... ...
   frames from different streams are INTERLEAVED on the wire:  [H1][H3][H5][D3][D1][D5][D1]...
```

| Feature | What it is | Benefit |
|---------|-----------|---------|
| **Binary framing** | everything is a small **frame** with a fixed header, not text lines | faster, unambiguous parsing |
| **Streams and multiplexing** | many independent request/response exchanges share one connection; frames carry a **stream ID** | no HTTP-level HOL blocking; one connection per origin |
| **HPACK header compression** | headers are encoded against a shared table of previously seen fields | headers shrink to a few bytes after the first request |
| **Flow control** | per-stream and per-connection **windows** limit unacknowledged data | one stream cannot flood the connection |
| **Prioritization** | clients hint which streams matter most (replaced by the simpler *Extensible Priorities*) | critical CSS before images |
| **Server push** | the server sends resources unrequested | **removed/disabled in browsers**: hard to use well, rarely helped |
| **Mandatory-ish TLS** | browsers use HTTP/2 only over HTTPS (`h2`) | encryption by default |

### Frames: the 9-byte header

Every HTTP/2 message is a sequence of frames. Each begins with a fixed **9-byte header**:

```text
+-----------------------------------------------+
|                 Length (24 bits)              |   payload size (not counting these 9 bytes)
+---------------+---------------+---------------+
|   Type (8)    |   Flags (8)   |
+-+-------------+---------------+-------------------------------+
|R|                 Stream Identifier (31 bits)                 |   0 = the whole connection; odd = client-initiated; even = server-initiated
+=+=============================================================+
|                   Frame Payload (Length bytes)                |
```

Common frame types: `0 DATA`, `1 HEADERS`, `3 RST_STREAM` (cancel one stream), `4 SETTINGS` (connection parameters), `6 PING`, `7 GOAWAY` (graceful shutdown), `8 WINDOW_UPDATE` (flow control). Flags include `END_STREAM` (0x1: last frame of this side) and `END_HEADERS` (0x4).

```python
import struct

FRAME_TYPES = {0: "DATA", 1: "HEADERS", 2: "PRIORITY", 3: "RST_STREAM", 4: "SETTINGS", 5: "PUSH_PROMISE",
               6: "PING", 7: "GOAWAY", 8: "WINDOW_UPDATE", 9: "CONTINUATION"}
TYPE_BY_NAME = {name: code for code, name in FRAME_TYPES.items()}

def build_frame(frame_type, flags, stream_id, payload=b""):
    length = len(payload)
    header = struct.pack("!I", length)[1:]                       # 24-bit length: take the low 3 bytes of a 32-bit integer
    header += struct.pack("!BBI", TYPE_BY_NAME[frame_type], flags, stream_id & 0x7FFFFFFF)       # type, flags, reserved bit + 31-bit stream id
    return header + payload

def parse_frame(raw):
    length = int.from_bytes(raw[:3], "big")
    frame_type, flags, stream_word = struct.unpack("!BBI", raw[3:9])
    return {"type": FRAME_TYPES.get(frame_type, frame_type), "flags": flags, "stream": stream_word & 0x7FFFFFFF,
            "length": length, "payload": raw[9:9 + length]}

PREFACE = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"                    # the fixed 24 bytes every client sends first (an HTTP/1.x-looking line that old servers reject)
print(len(PREFACE))                                              # 24

# SETTINGS: a list of (16-bit id, 32-bit value) pairs. 3 = MAX_CONCURRENT_STREAMS, 4 = INITIAL_WINDOW_SIZE
settings = build_frame("SETTINGS", 0, 0, struct.pack("!HI", 3, 100) + struct.pack("!HI", 4, 65535))
print(settings.hex())                                            # 00000c04000000000000030000006400040000ffff
print(parse_frame(settings))
# {'type': 'SETTINGS', 'flags': 0, 'stream': 0, 'length': 12, 'payload': b'\x00\x03\x00\x00\x00d\x00\x04\x00\x00\xff\xff'}

data = build_frame("DATA", 0x1, 5, b"<html>hello</html>")        # END_STREAM flag set on the last data frame of stream 5
print(parse_frame(data)["type"], parse_frame(data)["stream"], parse_frame(data)["flags"] & 0x1 == 1)         # DATA 5 True
print(len(build_frame("PING", 0, 0, b"12345678")))               # 17     9-byte header + 8-byte opaque payload
```

Multiplexing then simply means **frames of different streams are interleaved** and each receiver reassembles by stream id.

```python
def interleave(streams, frame_size=4):
    """Round-robin the frames of several streams onto one connection, like an HTTP/2 sender."""
    queues = {sid: [body[i:i + frame_size] for i in range(0, len(body), frame_size)] for sid, body in streams.items()}
    wire = []
    while any(queues.values()):
        for sid in sorted(queues):
            if queues[sid]:
                wire.append((sid, queues[sid].pop(0)))
    return wire

wire = interleave({1: b"AAAAAAAAAA", 3: b"BBBB", 5: b"CCCCCCCC"})
print([(sid, chunk.decode()) for sid, chunk in wire])
# [(1, 'AAAA'), (3, 'BBBB'), (5, 'CCCC'), (1, 'AAAA'), (5, 'CCCC'), (1, 'AA')]       the small stream 3 finishes in the first round: no waiting behind stream 1

reassembled = {}
for sid, chunk in wire:
    reassembled[sid] = reassembled.get(sid, b"") + chunk
print(reassembled)                                               # {1: b'AAAAAAAAAA', 3: b'BBBB', 5: b'CCCCCCCC'}
```

## 3. HPACK: header compression

HTTP headers are repetitive: the same `:authority`, `user-agent`, `accept` and (large) `cookie` on every request. **HPACK** (RFC 7541) compresses them with two ideas, deliberately **not** a general-purpose compressor like gzip (which leaked secrets through the **CRIME/BREACH** attacks when applied to headers):

1. **Static table:** 61 predefined common fields (`:method GET` is entry 2, `:status 200` is entry 8).
2. **Dynamic table:** a per-connection list of fields seen earlier. **Both sides update it identically**, so later references are just a small index. New entries are added at index 62 and older entries shift up; the table is size-limited (4096 bytes by default) and evicts the oldest.

A header field is then encoded in one of three ways:

| Representation | First bits | Meaning |
|----------------|-----------|---------|
| **Indexed** | `1xxxxxxx` | the whole name and value are in a table: send only the index |
| **Literal with incremental indexing** | `01xxxxxx` | send it as text **and add it to the dynamic table** (`xxxxxx` = index of the name, or 0 for a new name) |
| **Literal without indexing** | `0000xxxx` | send as text, do not add it (for values that change every time, or secrets) |

Integers use a **prefix-N encoding** (the first `N` bits of a byte hold the value; if it does not fit, the rest continues in 7-bit groups with a continuation bit):

```python
def encode_int(value, prefix_bits, flags=0):
    limit = (1 << prefix_bits) - 1
    if value < limit:
        return bytes([flags | value])
    out = [flags | limit]
    value -= limit
    while value >= 128:
        out.append((value % 128) | 0x80)                         # low 7 bits plus the "more bytes follow" flag
        value //= 128
    out.append(value)
    return bytes(out)

def decode_int(data, pos, prefix_bits):
    limit = (1 << prefix_bits) - 1
    value = data[pos] & limit
    pos += 1
    if value < limit:
        return value, pos
    shift = 0
    while True:
        byte = data[pos]; pos += 1
        value += (byte & 0x7F) << shift
        shift += 7
        if not byte & 0x80:
            return value, pos

# The RFC 7541 examples:
print(encode_int(10, 5).hex(), encode_int(1337, 5).hex(), encode_int(42, 8).hex())       # 0a 1f9a0a 2a
print(decode_int(encode_int(1337, 5), 0, 5))                     # (1337, 3)
```

The static table (all 61 entries; index 1 is first):

```python
STATIC = [(":authority", ""), (":method", "GET"), (":method", "POST"), (":path", "/"), (":path", "/index.html"),
          (":scheme", "http"), (":scheme", "https"), (":status", "200"), (":status", "204"), (":status", "206"),
          (":status", "304"), (":status", "400"), (":status", "404"), (":status", "500"), ("accept-charset", ""),
          ("accept-encoding", "gzip, deflate"), ("accept-language", ""), ("accept-ranges", ""), ("accept", ""),
          ("access-control-allow-origin", ""), ("age", ""), ("allow", ""), ("authorization", ""), ("cache-control", ""),
          ("content-disposition", ""), ("content-encoding", ""), ("content-language", ""), ("content-length", ""),
          ("content-location", ""), ("content-range", ""), ("content-type", ""), ("cookie", ""), ("date", ""), ("etag", ""),
          ("expect", ""), ("expires", ""), ("from", ""), ("host", ""), ("if-match", ""), ("if-modified-since", ""),
          ("if-none-match", ""), ("if-range", ""), ("if-unmodified-since", ""), ("last-modified", ""), ("link", ""),
          ("location", ""), ("max-forwards", ""), ("proxy-authenticate", ""), ("proxy-authorization", ""), ("range", ""),
          ("referer", ""), ("refresh", ""), ("retry-after", ""), ("server", ""), ("set-cookie", ""),
          ("strict-transport-security", ""), ("transfer-encoding", ""), ("user-agent", ""), ("vary", ""), ("via", ""),
          ("www-authenticate", "")]
print(len(STATIC), STATIC[1], STATIC[7])                         # 61 (':method', 'GET') (':status', '200')
```

An encoder and decoder that keep identical dynamic tables (Huffman coding of strings, an optional extra, is left out for clarity):

```python
class HpackEncoder:
    def __init__(self, max_size=4096):
        self.dynamic, self.max_size = [], max_size               # newest entry first; index 62 is dynamic[0]

    def _size(self):
        return sum(len(n) + len(v) + 32 for n, v in self.dynamic)         # each entry costs name + value + 32 bytes of overhead

    def _add(self, name, value):
        self.dynamic.insert(0, (name, value))
        while self._size() > self.max_size:
            self.dynamic.pop()                                   # evict the oldest

    def _find(self, name, value):
        table = STATIC + self.dynamic                            # indexes 1..61 static, 62.. dynamic
        exact = name_only = None
        for i, (n, v) in enumerate(table, start=1):
            if n == name and v == value and exact is None:
                exact = i
            if n == name and name_only is None:
                name_only = i
        return exact, name_only

    @staticmethod
    def _string(text):
        raw = text.encode()
        return encode_int(len(raw), 7, 0x00) + raw               # length (Huffman bit = 0: not Huffman coded) then the bytes

    def encode(self, headers):
        out = b""
        for name, value in headers:
            exact, name_only = self._find(name, value)
            if exact:
                out += encode_int(exact, 7, 0x80)                # indexed: 1xxxxxxx
            else:
                out += encode_int(name_only or 0, 6, 0x40)       # literal with incremental indexing: 01xxxxxx (0 = new name)
                if not name_only:
                    out += self._string(name)
                out += self._string(value)
                self._add(name, value)
        return out

class HpackDecoder:
    def __init__(self, max_size=4096):
        self.dynamic, self.max_size = [], max_size

    def _string(self, data, pos):
        length, pos = decode_int(data, pos, 7)
        return data[pos:pos + length].decode(), pos + length

    def decode(self, block):
        headers, pos = [], 0
        while pos < len(block):
            byte = block[pos]
            table = STATIC + self.dynamic
            if byte & 0x80:                                      # indexed
                index, pos = decode_int(block, pos, 7)
                headers.append(table[index - 1])
            else:                                                # literal (with or without indexing)
                incremental = bool(byte & 0x40)
                index, pos = decode_int(block, pos, 6 if incremental else 4)
                if index:
                    name = table[index - 1][0]
                else:
                    name, pos = self._string(block, pos)
                value, pos = self._string(block, pos)
                headers.append((name, value))
                if incremental:
                    self.dynamic.insert(0, (name, value))
        return headers
```

**Check it against the RFC.** RFC 7541 Appendix C.3 gives three consecutive requests on one connection and the exact bytes for each (without Huffman coding):

```python
requests = [
    [(":method", "GET"), (":scheme", "http"), (":path", "/"), (":authority", "www.example.com")],
    [(":method", "GET"), (":scheme", "http"), (":path", "/"), (":authority", "www.example.com"), ("cache-control", "no-cache")],
    [(":method", "GET"), (":scheme", "https"), (":path", "/index.html"), (":authority", "www.example.com"), ("custom-key", "custom-value")],
]
rfc_expected = [
    "828684410f7777772e6578616d706c652e636f6d",
    "828684be58086e6f2d6361636865",
    "828785bf400a637573746f6d2d6b65790c637573746f6d2d76616c7565",
]
encoder, decoder = HpackEncoder(), HpackDecoder()
for request, expected in zip(requests, rfc_expected):
    block = encoder.encode(request)
    print(len(block), block.hex() == expected, decoder.decode(block) == request)
# 20 True True
# 14 True True
# 29 True True
```

**All three match the RFC byte for byte**, and the decoder (with its own copy of the table) rebuilds the headers. Look at the sizes: the first request costs 20 bytes; the second, which repeats the host and adds `cache-control`, costs only **14**. The effect compounds for big, repetitive headers:

```python
browser_headers = [(":method", "GET"), (":scheme", "https"), (":authority", "shop.example.com"), (":path", "/products"),
                   ("user-agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"),
                   ("accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"),
                   ("accept-language", "en-US,en;q=0.9"), ("cookie", "session=9f8e7d6c5b4a39281706f5e4d3c2b1a0; theme=dark; cart=3")]
plain = sum(len(n) + len(v) + 4 for n, v in browser_headers)         # HTTP/1.1 text: "name: value\r\n"
enc = HpackEncoder()
sizes = [len(enc.encode(browser_headers)) for _ in range(5)]
print(plain, sizes)                                              # 345 [253, 8, 8, 8, 8]
```

The first request is a little smaller than the plain text (the dynamic table must be filled once), but every following request needs only **8 bytes** instead of 345. Over a page that makes 80 requests, that saves roughly 27 KB of uploads: significant on mobile uplinks.

**Security note:** the dynamic table is shared, so a header with a secret that an attacker can *influence* and *observe the compressed size of* (CRIME-style) could be guessed. HPACK limits this (no cross-field context mixing, an option to mark sensitive fields as **never indexed**: `0001xxxx`), and TLS-level compression is disabled.

## 4. Flow control and why one connection works

TCP already has flow control for the whole connection, but with many streams on one connection a greedy stream could use all the buffer and starve the others. HTTP/2 adds its **own windows**: every stream and the connection have a **receive window** (default **65,535 bytes**); a sender may not send more `DATA` than the window allows and waits for **`WINDOW_UPDATE`** frames from the receiver as it consumes data.

```python
class FlowControlledStream:
    def __init__(self, window=65_535):
        self.window = window
        self.sent = 0

    def send(self, size):
        allowed = min(size, self.window)                         # may only send what the peer has promised to buffer
        self.window -= allowed
        self.sent += allowed
        return allowed

    def window_update(self, increment):
        self.window += increment

s = FlowControlledStream()
print(s.send(40_000), s.send(40_000), s.window)                  # 40000 25535 0       the second send is cut off at the window
print(s.send(10_000))                                            # 0                   blocked until the receiver sends WINDOW_UPDATE
s.window_update(30_000)
print(s.send(10_000), s.sent)                                    # 10000 75535
```

Servers raise these windows (and `MAX_CONCURRENT_STREAMS`) in `SETTINGS` for high-bandwidth, high-latency links: a window of 64 KB per round trip caps throughput at `window / RTT`, only 5 Mbit/s at 100 ms!

```python
for rtt in (0.010, 0.100, 0.300):
    print(f"RTT {rtt * 1000:3.0f} ms: max throughput with a 64 KB window = {65_535 * 8 / rtt / 1e6:5.1f} Mbit/s")
# RTT  10 ms: max throughput with a 64 KB window =  52.4 Mbit/s
# RTT 100 ms: max throughput with a 64 KB window =   5.2 Mbit/s
# RTT 300 ms: max throughput with a 64 KB window =   1.7 Mbit/s
```

(This is the **bandwidth-delay product** again; window scaling in TCP and larger HTTP/2 windows fix it.)

## 5. HTTP/2's remaining problem: TCP head-of-line blocking

HTTP/2 removed blocking **between requests**, but all streams share **one TCP connection**, and TCP delivers a **single ordered byte stream**. If **one packet is lost**, TCP **holds back every later byte** (from *all* streams) until the lost packet is retransmitted, even bytes that belong to completely unrelated streams and have already arrived. On a clean network this is invisible; on lossy mobile or Wi-Fi links, one lost packet can freeze the whole page. (Ironically, HTTP/1.1's six separate connections degrade more gracefully here.)

A simulation. Three streams send four packets each, interleaved, one packet every 10 ms. One-way delay is 50 ms. **The second packet of stream A is lost** and is retransmitted after a timeout of one RTT (100 ms) once the sender notices:

```python
def simulate_loss(quic, one_way=0.050, interval=0.010, rto=0.100):
    # send order: A1 B1 C1 A2 B2 C2 A3 B3 C3 A4 B4 C4 (A2 is the lost packet)
    packets = [(f"{s}{n}", s) for n in range(1, 5) for s in "ABC"]
    arrival = {}
    for i, (name, stream) in enumerate(packets):
        sent = i * interval
        arrival[name] = sent + one_way
    lost = "A2"
    arrival[lost] = packets.index((lost, "A")) * interval + one_way + rto            # retransmission arrives one RTO later

    delivered = {}
    if quic:
        # QUIC: each stream is reassembled independently; a packet only blocks the same stream
        for stream in "ABC":
            time = 0.0
            for n in range(1, 5):
                time = max(time, arrival[f"{stream}{n}"])          # the stream needs its OWN earlier packets in order
                delivered[f"{stream}{n}"] = time
    else:
        # TCP: one ordered byte stream: nothing is delivered before every earlier packet has arrived
        time = 0.0
        for name, _ in packets:
            time = max(time, arrival[name])
            delivered[name] = time
    return {stream: round(delivered[f"{stream}4"] * 1000) for stream in "ABC"}        # completion time (ms) of each stream's last packet

print("HTTP/2 over TCP :", simulate_loss(quic=False))            # {'A': 180, 'B': 180, 'C': 180}
print("HTTP/3 over QUIC:", simulate_loss(quic=True))             # {'A': 180, 'B': 150, 'C': 160}
```

Without any loss all three streams would finish by about 160 ms. With TCP, **all three streams** finish at 180 ms because every packet after the lost one waited for the retransmission. With QUIC, **only stream A** is delayed (180 ms); streams B and C finish at 150 and 160 ms, **unaffected by A's loss**. That is the core motivation for HTTP/3.

## 6. HTTP/3 and QUIC

**QUIC** (RFC 9000, 2021) is a new transport protocol built on **UDP**; **HTTP/3** (RFC 9114) is HTTP mapped onto QUIC. It was designed at Google, deployed in Chrome and Google's servers, then standardized. About a third of web traffic uses it today.

| Idea | What QUIC does |
|------|----------------|
| **Runs over UDP** | UDP passes through the internet's existing middleboxes; QUIC re-implements reliability, ordering and congestion control **in user space**, so it can evolve without waiting for operating-system kernels |
| **Streams are first-class** | loss on one stream blocks only that stream (section 5) |
| **TLS 1.3 is built in** | the cryptographic handshake is **part of** the transport handshake: **1 RTT** to a secure connection (TCP + TLS 1.3 needs 2; TCP + TLS 1.2 needs 3) |
| **0-RTT resumption** | a returning client can send request data in its **very first packet** using a saved key (with a replay caveat: only for idempotent requests) |
| **Connection IDs** | a connection is identified by an ID chosen by the endpoints, **not** by the (IP, port) 4-tuple: switch from Wi-Fi to mobile data and the connection **survives** (**connection migration**) |
| **Almost everything encrypted** | even most transport headers, so middleboxes cannot ossify the protocol |
| **QPACK** | HTTP/3's header compression: HPACK redesigned so it does not reintroduce head-of-line blocking |
| **Better loss recovery** | unique packet numbers (no retransmission ambiguity), fast detection and tail-loss probes |

### Time to first request: counting round trips

```python
def handshake_rtts(stack):
    """Round trips before the client can send its first HTTP request."""
    return {"TCP + TLS 1.2": 3,          # 1 RTT TCP handshake + 2 RTT TLS 1.2 handshake
            "TCP + TLS 1.3": 2,          # 1 RTT TCP + 1 RTT TLS 1.3
            "QUIC (HTTP/3)": 1,          # transport and TLS handshakes combined
            "QUIC 0-RTT (resumption)": 0}[stack]

for rtt in (0.020, 0.100, 0.250):                                # nearby server, cross-country, intercontinental/mobile
    row = {s: round(handshake_rtts(s) * rtt * 1000) for s in ("TCP + TLS 1.2", "TCP + TLS 1.3", "QUIC (HTTP/3)", "QUIC 0-RTT (resumption)")}
    print(f"RTT {rtt * 1000:3.0f} ms ->", row)
# RTT  20 ms -> {'TCP + TLS 1.2': 60, 'TCP + TLS 1.3': 40, 'QUIC (HTTP/3)': 20, 'QUIC 0-RTT (resumption)': 0}
# RTT 100 ms -> {'TCP + TLS 1.2': 300, 'TCP + TLS 1.3': 200, 'QUIC (HTTP/3)': 100, 'QUIC 0-RTT (resumption)': 0}
# RTT 250 ms -> {'TCP + TLS 1.2': 750, 'TCP + TLS 1.3': 500, 'QUIC (HTTP/3)': 250, 'QUIC 0-RTT (resumption)': 0}
```

On a 250 ms satellite or congested mobile link, QUIC saves **half a second** before the first byte is requested.

### QUIC's variable-length integers

QUIC encodes many numbers with a **variable-length integer**: the **top two bits of the first byte** give the length (00 = 1 byte, 01 = 2, 10 = 4, 11 = 8 bytes); the remaining bits (6, 14, 30 or 62) hold the value in network byte order. Small numbers stay small.

```python
def quic_varint_encode(value):
    if value < 2**6:
        return bytes([value])                                    # 00xxxxxx
    if value < 2**14:
        return (value | 0x4000).to_bytes(2, "big")               # 01xxxxxx xxxxxxxx
    if value < 2**30:
        return (value | 0x80000000).to_bytes(4, "big")           # 10...
    if value < 2**62:
        return (value | 0xC000000000000000).to_bytes(8, "big")   # 11...
    raise ValueError("too large for a QUIC variable-length integer")

def quic_varint_decode(data):
    length = 1 << (data[0] >> 6)                                 # 2 bits -> 1, 2, 4 or 8 bytes
    value = int.from_bytes(data[:length], "big") & ((1 << (8 * length - 2)) - 1)
    return value, length

# The examples from RFC 9000 appendix A:
for value, expected in ((151_288_809_941_952_652, "c2197c5eff14e88c"), (494_878_333, "9d7f3e7d"), (15_293, "7bbd"), (37, "25")):
    encoded = quic_varint_encode(value)
    print(value, encoded.hex(), encoded.hex() == expected, quic_varint_decode(encoded) == (value, len(encoded)))
# 151288809941952652 c2197c5eff14e88c True True
# 494878333 9d7f3e7d True True
# 15293 7bbd True True
# 37 25 True True
```

## 7. Negotiating the version: ALPN and Alt-Svc

How do client and server agree on HTTP/1.1, HTTP/2 or HTTP/3?

- **HTTP/2 over TLS: ALPN (Application-Layer Protocol Negotiation).** Inside the TLS handshake the client lists the protocols it speaks (`["h2", "http/1.1"]`) and the server picks one. No extra round trip. (HTTP/2 without TLS, `h2c`, exists but browsers do not use it.)
- **HTTP/3: `Alt-Svc`.** A client usually first connects over TCP (HTTP/1.1 or 2). The server's response carries `Alt-Svc: h3=":443"; ma=86400` ("I also speak HTTP/3 on UDP port 443; remember that for a day"). The client then tries QUIC, **falling back to TCP** if UDP is blocked. (DNS **HTTPS records** can advertise this even before the first connection.)

You can watch ALPN happen on your own machine: our local TLS server offers `h2` and `http/1.1`, and clients with different preferences get different results.

```python
import ssl, socket, threading, tempfile, subprocess, os

workdir = tempfile.mkdtemp()
key_path, cert_path = os.path.join(workdir, "key.pem"), os.path.join(workdir, "cert.pem")
subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", key_path, "-out", cert_path, "-days", "2",
                "-subj", "/CN=localhost", "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1"], check=True, capture_output=True)

def alpn_server(ready, stop):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(cert_path, key_path)
    ctx.set_alpn_protocols(["h2", "http/1.1"])                   # the server's preference order
    with socket.socket() as srv:
        srv.bind(("127.0.0.1", 0)); srv.listen()
        ready.append(srv.getsockname()[1]); srv.settimeout(0.2)
        while not stop.is_set():
            try:
                raw, _ = srv.accept()
            except socket.timeout:
                continue
            try:
                with ctx.wrap_socket(raw, server_side=True) as conn:
                    conn.recv(1)
            except (ssl.SSLError, OSError):
                pass

ready, stop = [], threading.Event()
server_thread = threading.Thread(target=alpn_server, args=(ready, stop)); server_thread.start()
while not ready: pass

def negotiated(offered):
    ctx = ssl.create_default_context(cafile=cert_path)
    ctx.set_alpn_protocols(offered)
    with socket.create_connection(("127.0.0.1", ready[0])) as raw:
        with ctx.wrap_socket(raw, server_hostname="localhost") as tls:
            result = tls.selected_alpn_protocol()
            tls.sendall(b"x")
            return result

print(negotiated(["h2", "http/1.1"]), negotiated(["http/1.1"]), negotiated(["http/1.1", "h2"]))
# h2 http/1.1 h2
stop.set(); server_thread.join()
```

Read the three results: a client offering `h2` gets HTTP/2; an old client offering only `http/1.1` gets HTTP/1.1 (the server can only choose from what the client offers); and when the client offers both (even listing `http/1.1` first) this server still picks `h2`, because **the server's preference order wins** in OpenSSL's default behavior. Configure your server to list the protocols you prefer first.

## 8. What this changes for how you build sites

| Old HTTP/1.1 habit | With HTTP/2 and HTTP/3 |
|---------------------|-------------------------|
| **Bundle everything** into one huge JS/CSS file to save requests | Moderate bundling still helps compression and caching, but you need not fight to minimize request count; ship smaller, cacheable chunks |
| **CSS sprites**, image concatenation | Not needed |
| **Domain sharding** (`img1.cdn.com`, `img2.cdn.com`) | **Harmful**: it splits you across several connections, defeating multiplexing and prioritization |
| **Inlining** critical assets to avoid round trips | Still useful for the very first paint (critical CSS), but less critical |
| **Server push** | Deprecated in browsers; use `<link rel="preload">` or **103 Early Hints** instead |
| **Cookie-heavy requests** | HPACK/QPACK shrink repeated headers, but keep cookies small anyway |
| **Persistent connection tuning** | One long-lived connection per origin: tune `SETTINGS`, keep-alive and idle timeouts; use a CDN that terminates HTTP/3 near users |

Things that **still matter**: caching (`Cache-Control`, `ETag`: [HTTP lab](01-http-from-scratch.md)), compression (Brotli/gzip for bodies), smaller payloads, fewer blocking resources, a CDN, and efficient images. The protocol removed a class of workarounds; it did not remove the need for a lean site.

### Checking and enabling in practice

```bash
curl -sI --http2 https://example.com | head -1             # HTTP/2 200       (the status line shows the protocol used)
curl -sI --http3 https://cloudflare.com | head -1          # HTTP/3 200       (needs a curl built with HTTP/3 support)
curl -sI https://example.com | grep -i alt-svc             # alt-svc: h3=":443"; ma=86400    (HTTP/3 advertised)
nghttp -v https://example.com                              # prints every HTTP/2 frame (SETTINGS, HEADERS, DATA ...)
# Browser DevTools > Network > right-click the column header > enable "Protocol": h2, h3 or http/1.1 for each request
# Wireshark: filter "http2" or "quic"; with SSLKEYLOGFILE set you can decrypt and inspect the frames
```

Servers: **nginx** (`listen 443 ssl; http2 on;`, and `listen 443 quic reuseport;` for HTTP/3), **Caddy** (HTTP/3 by default), **Envoy**, **HAProxy**, and managed CDNs (Cloudflare, Fastly, CloudFront) enable it with a toggle. Remember to **open UDP port 443** in the firewall for HTTP/3.

## 9. Two real-world examples

**Example 1: A news site on a mobile network.** A page loads 90 resources and visitors are on a lossy 4G link with 150 ms RTT. On HTTP/1.1 the six connections serve 15 rounds of requests (about 2.25 s of pure waiting). On HTTP/2 the waiting collapses to one round; on HTTP/3 a lost packet no longer freezes the whole page, and returning visitors resume with 0-RTT. The site's measured median load time dropped by about a third just by enabling HTTP/3 at the CDN.

**Example 2: A video call app switching networks.** A user walks out of the building, and their phone moves from Wi-Fi to cellular, changing IP address. A TCP-based session would break and have to reconnect. A QUIC connection continues because it is identified by a **connection ID**, not the old IP and port: the app notices a short pause but no reconnection. This is a main reason mobile-first apps adopted QUIC.

## 10. Common mistakes

- Assuming HTTP/2 makes every site faster regardless of design (it mainly removes waiting between requests).
- Keeping domain sharding, sprite sheets and other HTTP/1.1 hacks "just in case".
- Relying on **server push**.
- Blocking UDP/443 (HTTP/3 silently falls back to TCP, so you lose the benefit without seeing an error).
- Forgetting that **0-RTT data can be replayed**: only allow it for safe, idempotent requests.
- Assuming a lost packet only affects one request on HTTP/2 over TCP (it stalls the whole connection).
- Believing QUIC is "less reliable because UDP": reliability and congestion control are implemented inside QUIC.
- Leaving small HTTP/2 flow-control windows on high-latency, high-bandwidth links (throughput capped at `window / RTT`).
- Putting secrets in headers you let attackers influence, or compressing sensitive content with the body (CRIME/BREACH-style risks).

## 11. Practice

1. Using `page_load_seconds`, compute HTTP/1.1 and HTTP/2 time for 36 resources of 50 KB over a 50 Mbit/s link with 40 ms RTT. Which part of the HTTP/1.1 time is waiting?
2. Build a `WINDOW_UPDATE` frame (type 8) for stream 0 with an increment of 65,535 and parse it back.
3. Encode the headers `[(":method", "POST"), (":path", "/api"), ("content-type", "application/json")]` with `HpackEncoder` and decode them. What does the `:method POST` header cost in bytes?
4. Why can HPACK not simply use gzip over all headers?
5. In `simulate_loss`, what happens if the lost packet is the *last* packet of stream C instead of `A2`? (modify the lost packet name and compare).
6. Compute the QUIC variable-length encoding of 63, 64 and 16,384.
7. A client offers `["http/1.1"]` over TLS. Which protocol is used, and why?
8. Why is domain sharding bad with HTTP/2?

<details>
<summary>Solutions</summary>

1. ```python
   h1 = page_load_seconds(36, 50_000, 0.040, 50_000_000, "http1")
   h2 = page_load_seconds(36, 50_000, 0.040, 50_000_000, "http2")
   print(round(h1, 3), round(h2, 3))                       # 0.528 0.328
   ```
   Transfer time is `36 * 50 KB * 8 / 50 Mbit/s = 0.288 s` for both; HTTP/1.1 waits `ceil(36/6) = 6` round trips (0.24 s) versus 1 (0.04 s) for HTTP/2.
2. ```python
   frame = build_frame("WINDOW_UPDATE", 0, 0, struct.pack("!I", 65_535))
   print(frame.hex(), parse_frame(frame))
   # 0000040800000000000000ffff {'type': 'WINDOW_UPDATE', 'flags': 0, 'stream': 0, 'length': 4, 'payload': b'\x00\x00\xff\xff'}
   ```
   (Thirteen bytes: length `000004`, type `08`, flags `00`, stream `00000000`, then the 4-byte increment `0000ffff`.)
3. ```python
   e, d = HpackEncoder(), HpackDecoder()
   block = e.encode([(":method", "POST"), (":path", "/api"), ("content-type", "application/json")])
   print(len(block), d.decode(block))
   # 25 [(':method', 'POST'), (':path', '/api'), ('content-type', 'application/json')]
   print(len(e.encode([(":method", "POST")])))             # 1
   ```
   `:method POST` is entry 3 of the static table, so it costs **one byte** (`0x83`).
4. Compression that mixes attacker-controlled data with secrets in one shared context leaks the secret through compressed sizes (the CRIME attack). HPACK compresses only through exact-match table references per field, so an attacker learns at most whether a whole header field matched, and sensitive fields can be marked "never indexed".
5. ```python
   def simulate_loss_at(lost, quic, one_way=0.050, interval=0.010, rto=0.100):
       packets = [(f"{s}{n}", s) for n in range(1, 5) for s in "ABC"]
       arrival = {name: i * interval + one_way for i, (name, _) in enumerate(packets)}
       arrival[lost] += rto
       delivered, time = {}, 0.0
       if quic:
           for stream in "ABC":
               t = 0.0
               for n in range(1, 5):
                   t = max(t, arrival[f"{stream}{n}"]); delivered[f"{stream}{n}"] = t
       else:
           for name, _ in packets:
               time = max(time, arrival[name]); delivered[name] = time
       return {s: round(delivered[f"{s}4"] * 1000) for s in "ABC"}
   print(simulate_loss_at("C4", quic=False), simulate_loss_at("C4", quic=True))
   # {'A': 140, 'B': 150, 'C': 260} {'A': 140, 'B': 150, 'C': 260}
   ```
   Losing the very last packet harms only the stream that owns it under both protocols, because nothing sent after it exists to be blocked. Head-of-line blocking hurts most when the loss is **early** in an interleaved flight.
6. ```python
   print([quic_varint_encode(v).hex() for v in (63, 64, 16_384)])           # ['3f', '4040', '80004000']
   ```
   63 fits in 6 bits (1 byte); 64 needs 14 bits (2 bytes, prefix `01`); 16,384 needs 30 bits (4 bytes, prefix `10`).
7. `http/1.1`: the server selects only from protocols the client offered, so the client that does not offer `h2` gets HTTP/1.1.
8. Each hostname gets its own connection, so you lose multiplexing, shared HPACK context and prioritization across resources, pay extra TCP and TLS handshakes, and open more congestion windows competing with each other.

</details>

## 12. Check yourself

1. What is head-of-line blocking in HTTP/1.1, and how does HTTP/2 remove it?
2. What are the fields of an HTTP/2 frame header?
3. How does HPACK shrink repeated headers, and why is it not gzip?
4. Why does HTTP/2 over TCP still suffer head-of-line blocking?
5. What does QUIC change to fix that, and what else does it provide?
6. How does a client learn that a server supports HTTP/3?
7. Name two HTTP/1.1 optimizations that are unnecessary or harmful under HTTP/2.

<details>
<summary>Answers</summary>

1. One slow response blocks the requests queued behind it on a connection; HTTP/2 multiplexes many streams as interleaved frames on one connection.
2. A 24-bit length, an 8-bit type, 8 bits of flags, a reserved bit and a 31-bit stream identifier.
3. It replaces repeated header fields with small indexes into a static table and a per-connection dynamic table that both ends update identically; it avoids gzip's shared compression context, which leaked secrets (CRIME).
4. TCP gives a single ordered byte stream, so one lost packet delays delivery of all later bytes for every stream until it is retransmitted.
5. QUIC runs streams independently over UDP with its own reliability, so loss on one stream does not block others; it also integrates TLS 1.3 (1-RTT, 0-RTT), uses connection IDs for migration and encrypts almost all headers.
6. Through the `Alt-Svc` response header (or DNS HTTPS records), then it tries QUIC and falls back to TCP if that fails.
7. Domain sharding and CSS sprites (also aggressive bundling to reduce request count) and relying on server push.

</details>

[Back to DNS and HTTP](README.md) · Previous: [DNS in depth](02-dns-in-depth.md)
