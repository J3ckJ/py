"""Потоки прячут I/O; CPU-bound на классическом CPython не ускоряется от двух потоков."""

from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor


def io_like(delay: float) -> float:
    time.sleep(delay)
    return delay


def cpu_like(n: int) -> int:
    s = 0
    for i in range(n):
        s += i % 7
    return s


def threads_overlap_sleep() -> None:
    delay = 0.08
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(io_like, delay) for _ in range(2)]
        results = [f.result() for f in futures]
    elapsed = time.perf_counter() - started
    assert results == [delay, delay]
    # Sequential would be ~0.16s; overlapping sleeps should beat that.
    assert elapsed < delay * 1.7, elapsed


def same_list_from_one_thread_is_fine() -> None:
    xs: list[int] = []
    xs.append(1)
    assert xs == [1]


def thread_name_is_not_a_result_channel() -> None:
    holder: dict[str, int] = {}

    def write() -> None:
        holder["v"] = 42

    t = threading.Thread(target=write)
    t.start()
    t.join()
    assert holder["v"] == 42


if __name__ == "__main__":
    threads_overlap_sleep()
    same_list_from_one_thread_is_fine()
    thread_name_is_not_a_result_channel()
    print("06_concurrency_map: ok")
