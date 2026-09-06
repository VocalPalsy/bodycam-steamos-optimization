#!/usr/bin/env python3
import glob, os, select, sys, time, statistics

pipes = glob.glob('/run/user/1000/gamescope.*/stats.pipe')
if not pipes:
    print('ERROR: No gamescope stats.pipe found')
    sys.exit(1)

pipe_path = pipes[0]
fd = os.open(pipe_path, os.O_RDONLY | os.O_NONBLOCK)

duration = int(sys.argv[1]) if len(sys.argv) > 1 else 300
start_time = time.time()
samples = []
gpu_loads = []
vram_usages = []
temps = []

def get_sys_metric(path):
    try:
        with open(path, 'r') as f:
            return float(f.read().strip())
    except:
        return None

hwmon_temp_path = None
for p in glob.glob('/sys/class/drm/card0/device/hwmon/hwmon*/temp1_input'):
    hwmon_temp_path = p
    break

buffer = ""
last_sys_check = 0

print(f"[*] Recording 5-minute online telemetry on {pipe_path}...")
sys.stdout.flush()

while time.time() - start_time < duration:
    now = time.time()
    r, _, _ = select.select([fd], [], [], 0.2)
    if r:
        try:
            chunk = os.read(fd, 4096).decode('utf-8', errors='ignore')
            buffer += chunk
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                if line.startswith('fps='):
                    try:
                        fps = float(line.split('=', 1)[1])
                        if fps > 15.0:
                            samples.append(fps)
                    except ValueError:
                        pass
        except OSError:
            pass

    if now - last_sys_check >= 1.0:
        last_sys_check = now
        g = get_sys_metric('/sys/class/drm/card0/device/gpu_busy_percent')
        if g is not None:
            gpu_loads.append(g)
        v = get_sys_metric('/sys/class/drm/card0/device/mem_info_vram_used')
        if v is not None:
            vram_usages.append(v / (1024 * 1024))
        if hwmon_temp_path:
            t = get_sys_metric(hwmon_temp_path)
            if t is not None:
                temps.append(t / 1000.0)

    time.sleep(0.02)

os.close(fd)

if not samples:
    print('ERROR: No frame samples gathered during 5-minute window.')
    sys.exit(1)

sorted_s = sorted(samples)
n = len(sorted_s)
avg_fps = statistics.mean(samples)
min_fps = min(samples)
max_fps = max(samples)
stdev_fps = statistics.stdev(samples) if len(samples) > 1 else 0.0
p1_low = sorted_s[max(0, int(n * 0.01))]
p01_low = sorted_s[max(0, int(n * 0.001))]

avg_gpu = statistics.mean(gpu_loads) if gpu_loads else 0.0
max_gpu = max(gpu_loads) if gpu_loads else 0.0
avg_vram = statistics.mean(vram_usages) if vram_usages else 0.0
avg_temp = statistics.mean(temps) if temps else 0.0

print('==============================================================')
print('        5-MINUTE LIVE ONLINE TELEMETRY BENCHMARK RESULTS      ')
print('==============================================================')
print(f'Total Valid Samples : {n}')
print(f'Average FPS         : {avg_fps:.2f} FPS')
print(f'FPS Standard Dev    : {stdev_fps:.2f} (Framerate Variance)')
print(f'Minimum FPS         : {min_fps:.2f} FPS')
print(f'1.0% Low FPS        : {p1_low:.2f} FPS')
print(f'0.1% Low FPS        : {p01_low:.2f} FPS')
print(f'Maximum FPS         : {max_fps:.2f} FPS')
print(f'Average GPU Load    : {avg_gpu:.1f}% (Peak: {max_gpu:.1f}%)')
print(f'VRAM Usage (GDDR6)  : {avg_vram:.0f} MB / 8192 MB')
print(f'GPU Core Temperature: {avg_temp:.1f}°C')
print('==============================================================')
