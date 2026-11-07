# Binary, Hexadecimal and How Data Is Stored

**Prerequisites:** [how a computer runs a program](how-computers-work.md). **You will learn:** why computers use binary, how to convert between binary, decimal and hex, how negative numbers and decimals are stored (and why `0.1 + 0.2` is odd), how text and emoji become bytes, and how bitwise operators work.

## 1. In plain words

A computer is built from billions of tiny switches that are either **off or on**. We write that as **0 or 1**: one **bit**. Everything a computer stores (numbers, text, photos, music, programs) is a long pattern of bits. The meaning comes only from **how we agree to interpret the pattern**.

| Unit | Size | Holds |
|------|------|-------|
| **bit** | 1 binary digit | 0 or 1 |
| **byte** | 8 bits | 256 different patterns (0 to 255); one character in simple text |
| **KB / MB / GB / TB** | 1,000 (or 1,024) bytes, then x1,000 each step | files, memory, disks |

(Strictly, **KiB, MiB, GiB** mean powers of 1,024; **KB, MB, GB** mean powers of 1,000. Operating systems and marketing mix them, which is why a "500 GB" disk shows as about 465 GiB.)

## 2. Number systems

We count in **base 10** because we have ten fingers: each position is worth ten times the one to its right. Computers use **base 2** (binary). Programmers also use **base 16** (hexadecimal) because it is a compact way to write binary.

| System | Digits | Position values (right to left) |
|--------|--------|---------------------------------|
| Decimal (base 10) | 0-9 | 1, 10, 100, 1000 |
| Binary (base 2) | 0, 1 | 1, 2, 4, 8, 16, 32, 64, 128 |
| Hexadecimal (base 16) | 0-9, A-F (A=10 ... F=15) | 1, 16, 256, 4096 |

### Binary to decimal: add up the positions that are 1

```text
binary  1 0 1 1 0 1
value  32 16 8 4 2 1
        1  0 1 1 0 1   ->  32 + 8 + 4 + 1 = 45
```

### Decimal to binary: divide by 2 and collect remainders (read them bottom-up)

```text
45 / 2 = 22 remainder 1
22 / 2 = 11 remainder 0
11 / 2 =  5 remainder 1
 5 / 2 =  2 remainder 1
 2 / 2 =  1 remainder 0
 1 / 2 =  0 remainder 1      read upward: 1 0 1 1 0 1  = 101101
```

```python
def to_binary(n):
    """Decimal to a binary string, by repeated division."""
    if n == 0:
        return "0"
    bits = []
    while n > 0:
        bits.append(str(n % 2))        # the remainder is the next bit (from the right)
        n //= 2
    return "".join(reversed(bits))

def from_binary(text):
    """Binary string to decimal, by adding up place values."""
    total = 0
    for bit in text:
        total = total * 2 + int(bit)   # shift left one place and add the new bit
    return total

print(to_binary(45), from_binary("101101"))            # 101101 45
print(bin(45), int("101101", 2))                       # 0b101101 45       (Python's built-ins)
print(hex(255), 0xFF, oct(8), 0o10, 0b1111)            # 0xff 255 0o10 8 15
assert all(from_binary(to_binary(n)) == n for n in range(1000))
```

### Why hexadecimal?

One hex digit equals exactly **4 bits**, so a byte is exactly **two hex digits**. It is far easier to read `FF` or `3A7F` than `11111111` or `0011101001111111`.

```text
binary:  1010 0111      hex:  A    7      ->  0xA7 = 167
```

```python
print(f"{167:08b}", f"{167:02X}", f"{167:#x}")         # 10100111 A7 0xa7
print(int("A7", 16), int("10100111", 2))                # 167 167
# Colors on the web are three bytes in hex: #RRGGBB
r, g, b = 255, 165, 0
print(f"#{r:02X}{g:02X}{b:02X}")                        # #FFA500   (orange)
```

## 3. Bitwise operators

They work on the individual bits of integers. They are used in flags, permissions, compression, graphics, networking (IP masks) and clever algorithms.

| Operator | Name | Meaning | Example (on 4-bit values) |
|----------|------|---------|---------------------------|
| `&` | AND | 1 only if both bits are 1 | `1100 & 1010 = 1000` |
| `\|` | OR | 1 if either bit is 1 | `1100 \| 1010 = 1110` |
| `^` | XOR | 1 if the bits differ | `1100 ^ 1010 = 0110` |
| `~` | NOT | flips every bit | `~0101 = ...1010` |
| `<<` | shift left | multiplies by 2 per step | `0011 << 2 = 1100` (3 becomes 12) |
| `>>` | shift right | integer-divides by 2 per step | `1100 >> 2 = 0011` (12 becomes 3) |

```python
a, b = 0b1100, 0b1010
print(f"{a & b:04b} {a | b:04b} {a ^ b:04b}")          # 1000 1110 0110
print(3 << 2, 12 >> 2, 1 << 10)                        # 12 3 1024

# Flags: pack several yes/no settings in one integer (like Unix file permissions)
READ, WRITE, EXECUTE = 0b100, 0b010, 0b001
permissions = READ | WRITE                             # turn two flags on
print(bool(permissions & WRITE), bool(permissions & EXECUTE))      # True False   (test a flag)
permissions |= EXECUTE                                 # turn a flag on
permissions &= ~WRITE                                  # turn a flag off
print(f"{permissions:03b}")                            # 101

# Handy tricks
n = 40
print(n & 1 == 0)                                      # True: the last bit tells even/odd
print(n & (n - 1) == 0, 64 & 63 == 0)                  # False True : a power of two has exactly one 1 bit
```

## 4. Integers, negative numbers and overflow

A fixed number of bits can hold only a fixed range of values: **n bits give 2^n patterns**.

| Bits | Unsigned range | Signed range (two's complement) |
|------|----------------|--------------------------------|
| 8 | 0 to 255 | -128 to 127 |
| 16 | 0 to 65,535 | -32,768 to 32,767 |
| 32 | 0 to about 4.29 billion | about -2.1 billion to 2.1 billion |
| 64 | 0 to about 1.8 x 10^19 | about -9.2 x 10^18 to 9.2 x 10^18 |

### Two's complement: how negative numbers are stored

Computers store a negative number by taking the binary of the positive number, **flipping all bits and adding 1**. The top bit then acts as the sign (1 = negative). This makes subtraction work with the same hardware as addition.

```text
8-bit example: -5
   5      = 0000 0101
   flip   = 1111 1010
   add 1  = 1111 1011     <- this pattern means -5
Check:  5 + (-5) = 0000 0101 + 1111 1011 = 1 0000 0000 -> the carry falls off the 8-bit edge -> 0000 0000 = 0  
```

```python
def to_twos_complement(value, bits=8):
    return format(value & ((1 << bits) - 1), f"0{bits}b")      # mask to `bits` bits

def from_twos_complement(pattern):
    value = int(pattern, 2)
    return value - (1 << len(pattern)) if pattern[0] == "1" else value

print(to_twos_complement(-5), to_twos_complement(5))           # 11111011 00000101
print(from_twos_complement("11111011"), from_twos_complement("01111111"))    # -5 127

# Overflow: what happens when a value does not fit
def wrap_int8(x):
    return from_twos_complement(to_twos_complement(x, 8))
print(wrap_int8(127 + 1))                                      # -128   (127 + 1 "wraps around" in 8-bit arithmetic)
print(2 ** 100)                                                # Python integers never overflow: they grow as needed
```

In languages such as C, Java and Go, fixed-size integers **overflow silently**: an overflow bug famously destroyed the Ariane 5 rocket (1996) and causes real security flaws. Python's arbitrary-precision integers avoid this, at the cost of speed.

## 5. Decimals: floating-point numbers

Computers store fractions as **floating-point** numbers (the IEEE 754 standard): a sign, an exponent and a 52-bit fraction (for 64-bit "double"), much like scientific notation (`1.2345 x 10^3`) but in base 2.

The catch: **most decimal fractions cannot be written exactly in binary**, just as 1/3 cannot be written exactly in decimal (0.3333...). `0.1` becomes a slightly-off binary fraction.

```python
print(0.1 + 0.2)                                    # 0.30000000000000004
print(0.1 + 0.2 == 0.3)                             # False
print(f"{0.1:.20f}")                                # 0.10000000000000000555   (what is actually stored)

import math
print(math.isclose(0.1 + 0.2, 0.3))                 # True    (compare with a tolerance)

from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))     # True    (exact decimal arithmetic: use for money)

# Floats lose precision with large numbers
print(2.0 ** 53 + 1 == 2.0 ** 53)                   # True    (beyond 2^53 floats skip integers)
print(1e308 * 10)                                   # inf     (overflow in floating point gives infinity)
print(float("nan") == float("nan"))                 # False   (NaN, "not a number", is not equal to anything)
```

Rules: **never compare floats with `==`** (use `math.isclose`); **never use floats for money** (use integer cents or `Decimal`); expect tiny errors to accumulate in long calculations.

## 6. Text: characters become numbers

Computers store text by giving every character a number (a **code point**) and storing that number.

- **ASCII** (1960s): 128 characters (English letters, digits, punctuation): `A` = 65, `a` = 97, `0` = 48.
- **Unicode**: a universal table of over 150,000 characters from every language plus emoji; each has a code point (`é` = 233, `ن` = 1606, 😀 = 128512).
- **UTF-8**: the most common way to store Unicode as bytes: ASCII characters use **1 byte**, others use 2-4 bytes. It is the standard for the web and Python source files.

```python
print(ord("A"), chr(65), ord("é"), chr(128512))             # 65 A 233 😀
text = "héllo 😀"
data = text.encode("utf-8")
print(len(text), len(data))                                 # 7 11      (7 characters but 11 bytes)
print(data)                                                 # b'h\xc3\xa9llo \xf0\x9f\x98\x80'
print(data.decode("utf-8") == text)                         # True
print("héllo".encode("ascii", errors="replace"))            # b'h?llo'   (ASCII cannot represent é)
```

Lessons: **a character is not a byte**; always say which **encoding** you use (`open(path, encoding="utf-8")`); `len(str)` counts characters, `len(bytes)` counts bytes; decoding with the wrong encoding produces garbled text ("mojibake").

## 7. Everything else is numbers too

| Data | How it is stored |
|------|------------------|
| **Image** | A grid of pixels; each pixel is 3 numbers (red, green, blue, 0-255). A 1920x1080 photo is about 2 million pixels x 3 bytes = 6 MB before compression (JPEG/PNG shrink it). |
| **Audio** | Samples of the sound wave taken 44,100 times per second, each stored as a number. |
| **Video** | Many images per second plus audio, heavily compressed. |
| **Program** | A list of numeric instruction codes ([machine code](how-computers-work.md)). |
| **Boolean** | One bit (stored in a whole byte in practice). |
| **A file** | Just a sequence of bytes; the file extension (`.png`, `.txt`) tells programs how to interpret them. |

```python
# A tiny 3x3 black-and-white "image" as a grid of numbers
image = [[0, 255, 0], [255, 255, 255], [0, 255, 0]]       # a plus sign: 0 = black, 255 = white
for row in image:
    print("".join("#" if p == 255 else "." for p in row))
# .#.
# ###
# .#.
print(len(image) * len(image[0]), "pixels")               # 9 pixels

# Size estimates
width, height, bytes_per_pixel = 1920, 1080, 3
print(f"{width * height * bytes_per_pixel / 1_000_000:.1f} MB uncompressed")      # 6.2 MB uncompressed
```

## 8. Two real-world examples

**Example 1: Unix file permissions.** `chmod 754 script.sh` sets permissions with three octal digits (owner 7, group 5, others 4). Each digit is the bit set `rwx`: 7 = `111` (read, write, execute), 5 = `101` (read, execute), 4 = `100` (read). The whole permission system is three 3-bit numbers combined with bitwise AND/OR.

**Example 2: IP addresses and subnet masks.** An IPv4 address is a 32-bit number written as four bytes (`192.168.1.10`). A network mask like `255.255.255.0` is 24 ones then 8 zeros; **bitwise AND** of address and mask extracts the network part. This is how routers decide where to send packets ([IP addressing](../../07-networking/tcp-ip-osi/README.md)).

```python
import ipaddress
address = int(ipaddress.ip_address("192.168.1.10"))
mask = int(ipaddress.ip_address("255.255.255.0"))
print(ipaddress.ip_address(address & mask))                # 192.168.1.0   (the network address)
```

## 9. Common mistakes

- Comparing floats with `==`; using floats for currency.
- Confusing characters with bytes, or forgetting to specify an encoding.
- Assuming integers are unlimited in other languages (overflow!).
- Mixing up `^` (XOR) with `**` (power) in Python.
- Treating `0.1 + 0.2 != 0.3` as a Python bug: it is a property of binary floating point in every language.
- Forgetting that hex digits and Python's `0x` prefix are just notation: the number is the same.

## 10. Practice

1. Convert 200 to binary and hex by hand, then check with Python.
2. Write `count_ones(n)` (number of 1 bits) without `bin`.
3. What is `0b1010 ^ 0b0110`? What is `5 << 3`?
4. Represent -20 in 8-bit two's complement.
5. Why does `"naïve".encode("utf-8")` have 6 bytes? How many characters?
6. Write a function that returns the permission string (like `rw-`) for a 3-bit number.
7. Compute exactly 0.1 + 0.2 with `Decimal` and with integer cents.

<details>
<summary>Solutions</summary>

**1.** 200 = 128 + 64 + 8 = `11001000` = `0xC8`.
```python
print(f"{200:b}", f"{200:X}", bin(200), hex(200))        # 11001000 C8 0b11001000 0xc8
```

**2.**
```python
def count_ones(n):
    count = 0
    while n:
        count += n & 1                 # look at the last bit
        n >>= 1                        # drop it
    return count
print(count_ones(0b101101), count_ones(255), count_ones(0))     # 4 8 0
```

**3.** `1010 ^ 0110 = 1100` = 12; `5 << 3 = 5 * 8 = 40`.
```python
print(0b1010 ^ 0b0110, 5 << 3)                  # 12 40
```

**4.** 20 = `00010100`; flip = `11101011`; add 1 = `11101100`.
```python
print(to_twos_complement(-20))                  # 11101100
```

**5.** `ï` takes 2 bytes in UTF-8 and the other 4 letters take 1 byte each: 5 characters, 6 bytes.
```python
print(len("naïve"), len("naïve".encode("utf-8")))           # 5 6
```

**6.**
```python
def perm_string(bits):
    return ("r" if bits & 4 else "-") + ("w" if bits & 2 else "-") + ("x" if bits & 1 else "-")
print(perm_string(7), perm_string(5), perm_string(4), perm_string(0))     # rwx r-x r-- ---
```

**7.**
```python
from decimal import Decimal
print(Decimal("0.1") + Decimal("0.2"))           # 0.3
print((10 + 20) / 100)                           # 0.3  (10 and 20 are cents: store money as integers)
```

</details>

## 11. Check yourself

1. How many different values can n bits represent?
2. Why is hex popular with programmers?
3. How is -1 stored in 8-bit two's complement?
4. Why is `0.1 + 0.2 != 0.3`, and how should you compare floats?
5. What is the difference between a Unicode code point and a UTF-8 byte?
6. What does `x & (x - 1)` do?
7. What would you use for money in code?

<details>
<summary>Answers</summary>

1. 2^n.
2. One hex digit is exactly 4 bits, so binary data is much shorter and easier to read.
3. `11111111` (all ones): flip `00000001` to `11111110` and add 1.
4. The decimal fractions are stored as slightly inexact binary fractions; compare with `math.isclose` (a tolerance) or use `Decimal`.
5. A code point is a character's number in the Unicode table; UTF-8 is a way to store that number as 1-4 bytes.
6. It clears the lowest set bit (so a result of 0 means x was zero or a power of two).
7. Integer cents or `decimal.Decimal`, never `float`.

</details>

[Back to foundations](../README.md) · Previous: [how computers work](how-computers-work.md) · Next: [memory, the stack and the heap](memory-stack-heap.md)
