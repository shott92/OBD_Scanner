# Performance Optimization Guide

## Python 3.13 & JIT Compiler
This project is optimized for **Python 3.13+**, which introduces an experimental Just-In-Time (JIT) compiler. The JIT compiler can significantly improve the performance of CPU-bound tasks, such as:

*   **CAN/FlexRay Signal Decoding**: Parsing thousands of frames per second.
*   **SWDL Checksums**: Calculating CRC32/SHA-256 for large firmware files.
*   **Filtering**: Iterating over large trace buffers.

### Installation & Setup

1.  **Install Python 3.13**:
    Download and install the latest Python 3.13 release from [python.org](https://www.python.org/downloads/).

2.  **Enable JIT**:
    Python 3.13's JIT is currently experimental and may require specific build flags or runtime options depending on the exact release version.
    
    To run the application with JIT enabled (if supported by your build), use:
    ```bash
    python -X jit main.py
    ```
    *Note: Verify your Python build supports JIT by running `python -VV`.*

### High-Load Optimization Tips
*   **Disable UI Logging**: In high-load scenarios (e.g., full bus logging), the UI log widget can become a bottleneck. Future versions will include a "Performance Mode" toggle to suppress real-time updates.
*   **Run as Administrator**: Some raw socket operations (DoIP/Ethernet) may perform better or require Admin privileges on Windows.

## Free-threaded Python (No-GIL)

Python 3.13 introduces an experimental **free-threaded build** mode that disables the Global Interpreter Lock (GIL).

### Why it matters for CANdy_Diag_Pro
For this application, the GIL is a primary bottleneck during **High-Load Competitor Analysis**:
*   **Parallel Decoding**: Without the GIL, we can run the `TopologyScanner` and `CommunicationManager` on separate CPU cores.
*   **Benefits**: Allows decoding 100% of bus traffic on loaded networks (e.g., FlexRay/CAN-FD) without dropping frames due to thread contention.

### How to use
1.  **Install the Free-threaded Build**:
    When installing Python 3.13, look for the "Free-threaded" or "nogil" installer option (often marked as experimental).
    
2.  **Running the App**:
    Execute the application normally. If using the free-threaded interpreter, threads will automatically scale across cores.
    ```bash
    python_t.exe main.py  # (Naming may vary, e.g., python3.13t)
    ```

> [!WARNING]
> **Compatibility**: Many third-party libraries (including `PyQt5`) may need updates to be fully thread-safe in a No-GIL environment. Use this mode with caution and verify stability.
