#!/usr/bin/env python3
"""
==============================================================================
Gamescope Telemetry Sampler for SteamOS / Linux
Monitors /run/user/1000/gamescope.*/stats.pipe for live FPS & frame-time metrics.
==============================================================================
"""

import glob
import os
import select
import sys
import time

def main():
    pipes = glob.glob('/run/user/1000/gamescope.*/stats.pipe')
    if not pipes:
        print("[!] Error: No active gamescope stats.pipe found.")
        print("    Ensure the game is actively running in Gamescope / Gaming Mode.")
        sys.exit(1)

    pipe_path = pipes[0]
    print(f"[*] Monitoring Gamescope pipe: {pipe_path} for 10 seconds...")

    samples = []
    try:
        fd = os.open(pipe_path, os.O_RDONLY | os.O_NONBLOCK)
    except OSError as e:
        print(f"[!] Failed to open pipe: {e}")
        sys.exit(1)

    start_time = time.time()
    buffer = ""

    while time.time() - start_time < 10:
        r, _, _ = select.select([fd], [], [], 0.5)
        if r:
            chunk = os.read(fd, 4096).decode("utf-8", errors="ignore")
            buffer += chunk
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if line.startswith("fps="):
                    try:
                        fps_val = float(line.split("=", 1)[1])
                        if fps_val > 10.0:  # Ignore paused / loading states
                            samples.append(fps_val)
                    except ValueError:
                        pass
        time.sleep(0.05)

    os.close(fd)

    if samples:
        avg_fps = sum(samples) / len(samples)
        min_fps = min(samples)
        max_fps = max(samples)
        print(f"[+] Results: SAMPLES={len(samples)} | AVG_FPS={avg_fps:.1f} | MIN_FPS={min_fps:.1f} | MAX_FPS={max_fps:.1f}")
    else:
        print("[-] Warning: No valid FPS frames recorded during sampling window.")

if __name__ == "__main__":
    main()
