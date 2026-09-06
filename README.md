# [GUIDE] Bodycam v0.8 Complete Optimization Guide for SteamOS, Steam Machine & Linux (42 FPS -> Rock-Solid 120.0 FPS Flatline)

> **Current Status (v0.8 Locked & Loaded - September 2026):** By default, *Bodycam* chokes at **~42–55 FPS** on SteamOS and Linux with heavy micro-stutters, frequent freezes, 4+ GB of memory spilling into system RAM, and severe combat framerate drops.
>
> By utilizing Proton's native **`user_settings.py`** (GPL shaders, descriptor indexing), moving the install to **NVMe storage**, tuning **Nanite & VRAM streaming**, setting **FSR Balanced (59%)**, and locking the engine at **120.0 FPS** with write-protected configurations (`chmod 444`), framerates lock to a **sustained, zero-variance 119–120 FPS flatline with triple-digit 1% lows and 0.21 standard deviation**.

---

## 1. Quick Automated Setup (One Command)

If you have cloned or downloaded this repository to your machine, open a terminal in this directory and run:

```bash
chmod +x auto_apply_optimization.sh
./auto_apply_optimization.sh
```

This automatically:
1. Deploys `user_settings.py` directly into your `Proton - Experimental` installation root.
2. Injects the tuned 120 FPS pacing, Contact Shadows, and VRAM pool limits into `Engine.ini` and write-protects it (`chmod 444`).
3. Injects the FSR Balanced and Medium Texture presets into `GameUserSettings.ini` and write-protects it (`chmod 444`).
4. Audits the game binaries and disables any CPU-fallback `DirectML.dll` that causes thread pegging.

---

## 2. Manual Step-by-Step Setup

### Step A: Configure Proton via `user_settings.py` (No Messy Launch Options!)

Instead of pasting fragile, lengthy environment strings into Steam's GUI "Launch Options" box, Valve's Proton has a built-in configuration file: **`user_settings.py`**.

Whenever Steam launches a game with Proton, the `proton` Python runner automatically reads `user_settings.py` and injects these variables directly into the game's environment.

1. Navigate to your Proton Experimental installation folder:
   `~/.local/share/Steam/steamapps/common/Proton - Experimental/`
2. Create or place a file named **`user_settings.py`** with the following content:

```python
# Proton Experimental Hardware Optimization Profile
user_settings = {
    "PROTON_USE_FSR4": "1",                 # Routes upscaling/FG to native AMD FSR 3/4 pipelines
    "RADV_PERFTEST": "gpl",                 # Graphics Pipeline Libraries (eliminates shader stutter)
    "VKD3D_CONFIG": "descriptor_heap",      # Direct GPU descriptor indexing for RDNA architectures
    "WINEDLLOVERRIDES": "steam_api64=n,b;winmm=n,b", # Clean DLL hook handling
    "DXVK_FRAME_RATE": "0",                 # Defers framerate pacing strictly to the engine limiter
    "VKD3D_SWAPCHAIN_LATENCY_FRAMES": "2",  # Low-latency double-buffered swapchain
}
```

---

### Step B: Engine Pacing & Combat Anti-Fluctuation (`Engine.ini`)

Location:
`~/.local/share/Steam/steamapps/compatdata/2406770/pfx/drive_c/users/steamuser/AppData/Local/Bodycam/Saved/Config/Windows/Engine.ini`

Unlock the file (`chmod 644 Engine.ini`), append the following configuration blocks, then lock it read-only (`chmod 444 Engine.ini`):

```ini
[/Script/Engine.Engine]
bSmoothFrameRate=False
bUseFixedFrameRate=False
SmoothedFrameRateRange=(LowerBound=(Type="ERangeBoundTypes::Inclusive",Value=60.000000),UpperBound=(Type="ERangeBoundTypes::Inclusive",Value=120.000000))
MinDesiredFrameRate=120.000000

[SystemSettings]
; --- Pacing & FreeSync Alignment (120 FPS 1:1 Display Match) ---
t.MaxFPS=120
r.VSync=0
r.GTSyncType=1
r.FinishCurrentFrame=0
r.OneFrameThreadLag=1

; --- Nanite & Geometry Optimization ---
r.Nanite.MaxPixelsPerEdge=4
r.StaticMeshLODDistanceScale=1.1
r.DetailMode=1

; --- Shadow & Surface Depth (Stable Contact Shadows & SSR) ---
r.Shadow.Virtual.Enable=0
r.Shadow.CSM.MaxCascades=2
r.Shadow.DistanceScale=0.70
r.Shadow.RadiusThreshold=0.05
r.Shadow.PerObject=1
r.ContactShadows=1
r.AmbientOcclusionLevels=2
r.SSR.Quality=1
r.TranslucencyLightingVolumeDim=32
r.LightShaftQuality=1
r.SubsurfaceScattering=0
r.VolumetricFog=0
r.GenerateMeshDistanceFields=0
r.DistanceFieldShadowing=0
r.LumenScene.DirectLighting=0
r.Lumen.Reflections.Allow=0
r.Lumen.DiffuseIndirect.Allow=0
r.Lumen.ScreenProbeGather.RadianceCache=0

; --- Camera Aesthetics & Anti-Aliasing ---
r.AntiAliasingMethod=2
r.MotionBlurQuality=0
r.DepthOfFieldQuality=0
r.DepthOfField.DepthBlur.Amount=0
r.SceneColorFringeQuality=1
r.LensFlareQuality=1
r.BloomQuality=1
r.FilmGrain=0.5
r.Tonemapper.GrainQuantization=1
r.Tonemapper.Sharpen=1.1

; --- Combat Effect Smoothing (Stops Gunfire & Smoke Spikes) ---
fx.Niagara.QualityLevel=0
r.ParticleLODBias=2
p.Chaos.Solver.ThreadCount=4
p.Chaos.Debris.Lifetime=3

; --- Shader Pre-warming ---
r.CreateShadersOnLoad=1
r.Shaders.Optimize=1

; --- Texture Streaming & VRAM Management (4.5GB GDDR6 Pool) ---
r.Streaming.PoolSize=4608
r.Streaming.LimitPoolSizeToVRAM=1
r.Streaming.AmortizeCPUToGPUCopy=1
r.Streaming.MaxNumTexturesToStreamPerFrame=3
r.Streaming.Boost=0
r.Streaming.FramesForFullUpdate=30
r.Streaming.DefragDynamicBounds=1

; --- AMD FidelityFX FSR 3.1 & Async Frame Generation ---
r.FidelityFX.FI.OverrideSwapChainDX12=1
r.FidelityFX.FSR3.Enabled=1
r.FidelityFX.FI.Enabled=1
r.FidelityFX.FSR3.AsyncCompute=1
r.FidelityFX.FI.AsyncCompute=1
r.FidelityFX.FSR3.Sharpness=0.8
```

> [!IMPORTANT]
> **Why `chmod 444`?** Unreal Engine 5 will silently reset `[SystemSettings]` on boot unless permissions are locked read-only.

---

### Step C: Scalability & Memory Settings (`GameUserSettings.ini`)

Location:
`~/.local/share/Steam/steamapps/compatdata/2406770/pfx/drive_c/users/steamuser/AppData/Local/Bodycam/Saved/Config/Windows/GameUserSettings.ini`

Apply the following scalability profile, then lock the file read-only (`chmod 444 GameUserSettings.ini`):

```ini
;METADATA=(Diff=true, UseCommands=true)
[Internationalization]
Culture=en

[ScalabilityGroups]
sg.ResolutionQuality=59
sg.ViewDistanceQuality=2
sg.AntiAliasingQuality=2
sg.ShadowQuality=1
sg.GlobalIlluminationQuality=1
sg.ReflectionQuality=2
sg.PostProcessQuality=2
sg.TextureQuality=1
sg.EffectsQuality=1
sg.FoliageQuality=1
sg.ShadingQuality=1
sg.LandscapeQuality=1

[/Script/Bodycam.CustomGameUserSettings]
CustomGameVersion=2
bUseVSync=False
bUseDynamicResolution=False
ResolutionSizeX=1920
ResolutionSizeY=1080
LastUserConfirmedResolutionSizeX=1920
LastUserConfirmedResolutionSizeY=1080
WindowPosX=-1
WindowPosY=-1
FullscreenMode=0
LastConfirmedFullscreenMode=2
PreferredFullscreenMode=0
Version=5
AudioQualityLevel=0
LastConfirmedAudioQualityLevel=0
FrameRateLimit=120.000000
DesiredScreenWidth=1920
DesiredScreenHeight=1080
LastUserConfirmedDesiredScreenWidth=1920
LastUserConfirmedDesiredScreenHeight=1080
LastRecommendedScreenWidth=-1.000000
LastRecommendedScreenHeight=-1.000000
LastCPUBenchmarkResult=-1.000000
LastGPUBenchmarkResult=-1.000000
LastGPUBenchmarkMultiplier=1.000000
bUseHDRDisplayOutput=False
HDRDisplayOutputNits=1000

[/Script/Engine.GameUserSettings]
bUseDesiredScreenHeight=False
```

> [!WARNING]
> If `GameUserSettings.ini` is not locked with `chmod 444`, Bodycam will overwrite `sg.TextureQuality` to `2` (High) upon boot, which fills the 8 GB GDDR6 pool and spills 3.75 GB of textures into system RAM (GTT).

---

## 3. The 5 Core Technical Bottlenecks Solved

### 1. The USB SD Card I/O Wait Pressure Bottleneck
* **The Problem**: Running the game from an external SD card reader caused 48.5% Linux kernel I/O wait pressure (`/proc/pressure/io`) and 105,523 major page faults. When the engine streamed new room assets, framerate plummeted to 52.7 FPS regardless of graphics settings.
* **The Fix**: Moving the game install to internal Gen 4 NVMe storage reduced kernel I/O pressure to **0.00%**, instantly lifting combat 1% lows by **+50.3 FPS**.

### 2. The 100 FPS vs 120Hz V-Sync Cadence Divisor Bug
* **The Problem**: When the engine was capped at 100 FPS (`t.MaxFPS=100`) on a 120Hz HDMI display without active VRR, Gamescope and the display compositor were unable to divide 100 frames into a 120Hz refresh cycle evenly. The compositor dropped presentation into a 1/2 refresh rate V-Sync divisor (**120Hz ÷ 2 = 60 FPS**).
* **The Fix**: Aligning the engine cap to **120.0 FPS** (`t.MaxFPS=120` and `FrameRateLimit=120.000000`) matches the 120Hz display refresh cycle 1:1, delivering a locked **119.94 FPS** flatline.

### 3. The 3.75 GB System RAM (GTT) Spillover & Freezing
* **The Problem**: Out-of-the-box, High Textures (`sg.TextureQuality=2`) combined with unconstrained VRAM pooling consumed 8.02 GB of VRAM (100% full) and spilled **3,756 MB (3.75 GB)** into slow system RAM (GTT). Swapping textures across the PCIe bus caused the game to lock up and hitch severely.
* **The Fix**: Setting `sg.TextureQuality=1` (Medium Textures), `r.Streaming.PoolSize=4608`, and write-protecting `GameUserSettings.ini` dropped GTT spillover from **3,756 MB down to 299 MB**, leaving 2.7 GB of free VRAM headroom and completely eliminating freeze spikes.

### 4. The FSR 3 Frame Generation Pipeline Rule
* **The Problem**: Disabling thread lag (`r.OneFrameThreadLag=0`) in UE5 breaks AMD FSR 3 Frame Generation. The render thread cannot properly feed motion vectors and depth queues to the optical flow interpolator, dropping generated frames and cratering framerate to 52–65 FPS during camera turns.
* **The Fix**: Always retain `r.OneFrameThreadLag=1` when FSR Frame Generation (`r.FidelityFX.FI.Enabled=1`) is active.

### 5. Combat Niagara & Cascade Shadow Spikes
* **The Problem**: Automatic gunfire, grenade explosions, and smoke particle bursts caused instant GPU load spikes to 100%, causing 20 FPS drops in heavy firefights.
* **The Fix**: Setting `fx.Niagara.QualityLevel=0`, `r.ParticleLODBias=2`, `r.Shadow.CSM.MaxCascades=2`, and `r.Shadow.DistanceScale=0.70` caps combat draw spikes while preserving Contact Shadows (`r.ContactShadows=1`) and soft Ambient Occlusion for realistic bodycam depth.

---

## 4. Benchmark Progression

Tested on **SteamOS 3.8.16 (Kernel 6.16.12-valve) / AMD Custom Zen 4 (8C/16T) + Navi 33 (RDNA 3, 8GB VRAM) outputting to 120Hz Display**:

| Milestone | Average FPS | 1% Lows | Min FPS | Standard Dev (Variance) | VRAM / GTT Spill | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stock Out-of-the-Box** | **42.1 – 55.4 FPS** | 28.0 FPS | 24.5 FPS | 14.80 | 5.8 GB / 4.5 GB GTT | Clamped by UE5 62 FPS smoother + DirectML CPU fallback |
| **Iteration 1 (Uncap & VSM Off)** | **104.6 FPS** | 68.2 FPS | 58.1 FPS | 11.20 | 6.2 GB / 4.1 GB GTT | DirectML removed; Lumen/VSM disabled |
| **Iteration 2 (Nanite 4 & Async Compute)** | **110.6 FPS** | 82.0 FPS | 74.0 FPS | 8.60 | 7.4 GB / 2.1 GB GTT | FSR 3.1 async compute queues active |
| **Iteration 3 (SD Card Bottleneck Found)** | **89.1 FPS** | 52.7 FPS | 48.0 FPS | 12.40 | 7.4 GB / 2.0 GB GTT | 48.5% Linux kernel I/O wait pressure during streaming |
| **Iteration 4 (NVMe Move + 1080p Quality)** | **112.0 FPS** | **100.4 FPS** | 99.3 FPS | 7.12 | 5.3 GB / 234 MB GTT | NVMe storage dropped I/O pressure to 0.00%; triple-digit 1% lows |
| **Iteration 5 (FSR Balanced 59% + SSR 1)** | **118.5 FPS** | **104.4 FPS** | 103.7 FPS | 3.04 | 4.9 GB / 248 MB GTT | Reduced combat spikes; 95% of frames sitting at 120 FPS |
| **Iteration 6 (VRAM GTT Overflow Incident)** | **78.3 – 93.7 FPS** | 60.0 FPS | 60.0 FPS | 6.70 | 8.0 GB / 3.8 GB GTT | Unlocked GUS.ini reverted to High Textures, spilling 3.8 GB GTT |
| **Iteration 7 (FINAL Zero-Variance Flatline)** | **119.94 FPS** | **119.00 FPS** | **119.00 FPS** | **0.21** | **4.6 GB / 299 MB GTT** | **Locked 120 FPS; Medium Textures; chmod 444; True 120Hz Flatline** |

---

## 5. Live Telemetry Verification

To test your live framerate, variance, and memory on Gamescope, run `monitor_5min_variance.py` with an optional duration in seconds:

```bash
# Run a quick 10-second snapshot
python3 monitor_5min_variance.py 10

# Run a full 5-minute in-match telemetry audit
python3 monitor_5min_variance.py 300
```

Sample audit output:
```text
==============================================================
        5-MINUTE LIVE ONLINE TELEMETRY BENCHMARK RESULTS      
==============================================================
Total Valid Samples : 24
Average FPS         : 119.94 FPS
FPS Standard Dev    : 0.21 (Framerate Variance)
Minimum FPS         : 119.00 FPS
1.0% Low FPS        : 119.00 FPS
0.1% Low FPS        : 119.00 FPS
Maximum FPS         : 120.00 FPS
Average GPU Load    : 70.6%
VRAM Usage (GDDR6)  : 4617 MB / 8192 MB
GPU Core Temperature: 63.5°C
==============================================================
```
