## 2025-05-15 - [UI Update Bottleneck in Typing Counter]
**Learning:** Updating Tkinter UI elements (like labels) directly within a high-frequency system-wide event handler (pynput's `_on_press`) creates significant overhead and can block the main thread, leading to perceived lag during fast typing. Furthermore, Tkinter is not thread-safe, and updating it from a listener thread is an anti-pattern.
**Action:** Move UI updates into a periodic polling loop (`master.after`) on the main thread. This effectively debounces the visual refresh and improves overall application responsiveness and stability.

## 2025-05-15 - [Timing Precision and Performance]
**Learning:** `datetime.now()` and `timedelta` calculations are significantly slower (~4x) than using `time.monotonic()` or `time.time()` for measuring elapsed time and tracking session durations in hot paths.
**Action:** Prefer `time.monotonic()` for internal duration tracking and inactivity timeouts. It is also immune to system clock adjustments.
