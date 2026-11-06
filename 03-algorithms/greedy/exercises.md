# Greedy Algorithms: Exercises

## Problems
1. **Activity selection:** maximum number of non-overlapping intervals.
2. **Erase overlap intervals:** minimum intervals to remove so the rest do not overlap.
3. **Jump game:** can you reach the last index?
4. **Jump game II:** minimum jumps to reach the last index.
5. **Gas station:** starting index to complete the circuit, or `-1`.
6. **Assign cookies:** maximize content children.
7. **Fractional knapsack:** maximum value when items can be split.
8. **Partition labels:** split a string so each letter appears in at most one part; return the part sizes.
9. **Non-decreasing array:** can you make the array non-decreasing by changing at most one element?
10. **Huffman coding:** build an optimal prefix code from frequencies.
11. **Task scheduler:** minimum time to run tasks with a cooling interval `n` between identical tasks.
12. **Find a counterexample:** show greedy fails for coin change with `{1, 3, 4}` and amount `6`.

<details>
<summary>Solutions</summary>

```python
import heapq
from collections import Counter

# 1
def max_non_overlapping(intervals):
    count, last = 0, float("-inf")
    for s, e in sorted(intervals, key=lambda x: x[1]):
        if s >= last:
            count += 1; last = e
    return count

# 2
def erase_overlap(intervals):
    return len(intervals) - max_non_overlapping(intervals)

# 3
def can_jump(nums):
    reach = 0
    for i, x in enumerate(nums):
        if i > reach:
            return False
        reach = max(reach, i + x)
    return True

# 4
def min_jumps(nums):
    jumps = cur_end = farthest = 0
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == cur_end:
            jumps += 1; cur_end = farthest
    return jumps

# 5
def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    tank = start = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:
            start, tank = i + 1, 0
    return start

# 6
def assign_cookies(children, cookies):
    children.sort(); cookies.sort()
    i = 0
    for c in cookies:
        if i < len(children) and c >= children[i]:
            i += 1
    return i

# 7
def fractional_knapsack(items, capacity):          # (value, weight)
    total = 0.0
    for v, w in sorted(items, key=lambda x: x[0] / x[1], reverse=True):
        take = min(w, capacity)
        total += v * take / w
        capacity -= take
        if capacity == 0:
            break
    return total

# 8
def partition_labels(s):
    last = {ch: i for i, ch in enumerate(s)}
    sizes, start, end = [], 0, 0
    for i, ch in enumerate(s):
        end = max(end, last[ch])
        if i == end:
            sizes.append(end - start + 1)
            start = i + 1
    return sizes

# 9
def check_possibility(nums):
    changed = False
    for i in range(1, len(nums)):
        if nums[i] < nums[i - 1]:
            if changed:
                return False
            changed = True
            if i >= 2 and nums[i] < nums[i - 2]:
                nums[i] = nums[i - 1]
            else:
                nums[i - 1] = nums[i]
    return True

# 10
def huffman(freqs):
    heap = [(f, i, {s: ""}) for i, (s, f) in enumerate(freqs.items())]
    heapq.heapify(heap)
    counter = len(heap)
    while len(heap) > 1:
        f1, _, c1 = heapq.heappop(heap)
        f2, _, c2 = heapq.heappop(heap)
        merged = {s: "0" + c for s, c in c1.items()}
        merged.update({s: "1" + c for s, c in c2.items()})
        heapq.heappush(heap, (f1 + f2, counter, merged))
        counter += 1
    return heap[0][2]

# 11
def least_interval(tasks, n):
    counts = Counter(tasks)
    max_count = max(counts.values())
    num_max = sum(1 for c in counts.values() if c == max_count)
    return max(len(tasks), (max_count - 1) * (n + 1) + num_max)

# 12
def greedy_coins(coins, amount):
    count = 0
    for c in sorted(coins, reverse=True):
        count += amount // c
        amount %= c
    return count if amount == 0 else -1
# greedy_coins([1, 3, 4], 6) == 3, but the optimum is 2 (3 + 3).
```

</details>
