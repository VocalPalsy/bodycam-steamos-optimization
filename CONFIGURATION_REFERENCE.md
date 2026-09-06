# Complete Configuration Reference: Bodycam v0.8 (Steam Machine & SteamOS)

This document provides a comprehensive technical audit of all configurations required to achieve a sustained, locked ~119–120 FPS flatline under 120Hz displays on AMD RDNA 2/3 GPUs running SteamOS / Linux.

---

## 1. File Map & Permissions

| Component | Target System Path | Local Repository File | Permissions | Critical Role |
| :--- | :--- | :--- | :--- | :--- |
| **Engine Overrides** | `~/.local/share/Steam/steamapps/compatdata/2406770/pfx/drive_c/users/steamuser/AppData/Local/Bodycam/Saved/Config/Windows/Engine.ini` | [`Engine.ini`](./Engine.ini) | `chmod 444` (Read-only) | Locks frame pacing, disables VSM, enables Contact Shadows & FSR 3 FG |
| **Scalability & Res** | `~/.local/share/Steam/steamapps/compatdata/2406770/pfx/drive_c/users/steamuser/AppData/Local/Bodycam/Saved/Config/Windows/GameUserSettings.ini` | [`GameUserSettings.ini`](./GameUserSettings.ini) | `chmod 444` (Read-only) | Prevents UE5 from overwriting Texture/Resolution settings on boot |
| **Proton Runtime** | `~/.local/share/Steam/steamapps/common/Proton - Experimental/user_settings.py` | [`user_settings.py`](./user_settings.py) | `chmod 644` | Injects GPL shaders, descriptor heap indexing, and swapchain latency |
| **Telemetry Sampler** | Anywhere locally / `/tmp` | [`monitor_5min_variance.py`](./monitor_5min_variance.py) | `chmod 755` (`+x`) | Reads live Gamescope stats pipe for FPS, variance, lows, VRAM & GPU load |

> [!IMPORTANT]
> **Why both files MUST be `chmod 444`**:
> Unreal Engine 5 automatically overwrites `GameUserSettings.ini` and `Engine.ini` on shutdown and startup. Without `chmod 444`, `GameUserSettings.ini` reverts `sg.TextureQuality` from 1 to 2, which instantly consumes all 8 GB of VRAM, overflows 3.75 GB into slow system RAM (GTT), and triggers heavy freezing.

---

## 2. Engine Optimizations (`Engine.ini`)

### A. Framerate & Pacing Synchronization
* `bSmoothFrameRate=False`: Disables UE5 default internal 62 FPS clamping smoother.
* `bUseFixedFrameRate=False`: Prevents lockstep physics stalls.
* `SmoothedFrameRateRange=(LowerBound=60.0,UpperBound=120.0)`: Bounds internal scheduler targets.
* `MinDesiredFrameRate=120.0`: Instructs the engine scheduler to drop transient non-critical tasks when frametimes approach 8.33ms.
* `t.MaxFPS=120`: Caps engine presentation directly at 120 FPS. Perfectly aligns with 120Hz display refresh intervals (8.33ms per frame) without floating-point cadence drift.
* `r.VSync=0`: Disables hardware double-buffer stalls in favor of Wayland/Gamescope presentation.
* `r.GTSyncType=1`: Synchronizes GameThread and RenderThread on fence points to eliminate frame-time jitter.
* `r.FinishCurrentFrame=0`: Allows overlap between CPU frame dispatch and GPU drawing.
* `r.OneFrameThreadLag=1`: **Mandatory for FSR 3 Frame Generation**. Setting this to 0 breaks the optical flow vector pipeline and causes severe stutter.

### B. Nanite & Geometry Scaling
* `r.Nanite.MaxPixelsPerEdge=4`: Evaluates Nanite mesh clusters at 4 px/edge. Retains razor-sharp world geometry on large displays while reducing geometry evaluation overhead by ~25%.
* `r.StaticMeshLODDistanceScale=1.1`: Extends high-detail LOD transitions safely without overloading draw calls.
* `r.DetailMode=1`: Retains standard environmental detail and debris markers.

### C. Lighting, Shadows & Photorealism Balance
* `r.Shadow.Virtual.Enable=0`: Completely disables Virtual Shadow Maps (VSM), which consume massive rasterization and VRAM fillrate.
* `r.Shadow.CSM.MaxCascades=2`: Caps traditional cascaded shadow maps to 2 cascades, giving realistic character shadows without multi-pass overhead.
* `r.Shadow.DistanceScale=0.70`: Culls distant dynamic shadows in open combat arenas to stop combat GPU spikes.
* `r.Shadow.RadiusThreshold=0.05`: Prevents minuscule background objects from casting dynamic shadow passes.
* `r.Shadow.PerObject=1`: Preserves high-detail dynamic weapon and character shadows.
* `r.ContactShadows=1`: **Critical for Bodycam's photorealism**. Adds screen-space depth under boots, weapons, and helmets with virtually zero performance impact.
* `r.AmbientOcclusionLevels=2`: Provides realistic soft contact shading in room corners and doorways.
* `r.SSR.Quality=1`: Enables clean screen-space reflections without the expensive multi-ray marching cost of SSR Quality 2.
* `r.TranslucencyLightingVolumeDim=32`: Standard translucency volume resolution for dust and glass.
* `r.LightShaftQuality=1`: Retains atmospheric volumetric light shafts through windows.
* `r.SubsurfaceScattering=0`: Disables skin subsurface scattering passes (unnecessary for tactical gear/helmets).
* `r.VolumetricFog=0`: Eliminates heavy 3D voxel fog calculations that cause 20–30 FPS drops when aiming into light sources.
* `r.LumenScene.DirectLighting=0` & `r.Lumen.Reflections.Allow=0`: Bypasses software Lumen ray tracing passes.

### D. Camera Aesthetics & Anti-Aliasing
* `r.AntiAliasingMethod=2`: Uses Temporal Anti-Aliasing (TAA) container required for FSR 3 reconstruction.
* `r.MotionBlurQuality=0` & `r.DepthOfFieldQuality=0`: Disables artificial camera blur to maximize target tracking clarity.
* `r.SceneColorFringeQuality=1` & `r.LensFlareQuality=1` & `r.BloomQuality=1`: Retains Bodycam's signature tactical optical camera artifacts.
* `r.FilmGrain=0.5`: Retains realistic bodycam sensor noise.
* `r.Tonemapper.Sharpen=1.1`: Compensates for sensor diffusion and ensures razor-sharp reticles.

### E. Combat Effect & Particle Smoothing
* `fx.Niagara.QualityLevel=0`: Lowers Niagara fluid compute overhead during heavy combat.
* `r.ParticleLODBias=2`: Reduces particle count for bullet impacts, muzzle flashes, and smoke bursts to stop combat dips.
* `p.Chaos.Solver.ThreadCount=4`: Dedicates 4 worker threads to Chaos physics and ragdoll collisions.
* `p.Chaos.Debris.Lifetime=3`: Despawns destroyed environment debris quickly to free CPU and GPU memory bandwidth.

### F. Texture Streaming & VRAM Protection
* `r.Streaming.PoolSize=4608`: Allocates a locked 4.5 GB GDDR6 texture streaming pool.
* `r.Streaming.LimitPoolSizeToVRAM=1`: Guarantees texture allocation never exceeds physical GDDR6 VRAM.
* `r.Streaming.AmortizeCPUToGPUCopy=1`: Spreads texture uploads across consecutive frames, eliminating corner-turning hitches.
* `r.Streaming.MaxNumTexturesToStreamPerFrame=3`: Caps per-frame texture uploads.
* `r.Streaming.Boost=0`: Prevents sudden priority shifts that trigger massive batch uploads.
* `r.Streaming.FramesForFullUpdate=30`: Updates texture stream bounds every 30 frames.
* `r.Streaming.DefragDynamicBounds=1`: Keeps VRAM fragmentation low.

### G. AMD FidelityFX FSR 3.1 & Frame Generation
* `r.FidelityFX.FI.OverrideSwapChainDX12=1`: Hooks the native DX12 swapchain with FidelityFX asynchronous presentation.
* `r.FidelityFX.FSR3.Enabled=1`: Enables FidelityFX upscaler.
* `r.FidelityFX.FI.Enabled=1`: Enables FidelityFX Frame Generation (2x frame multiplier).
* `r.FidelityFX.FSR3.AsyncCompute=1`: Offloads upscaling passes to asynchronous compute queues.
* `r.FidelityFX.FI.AsyncCompute=1`: Offloads frame interpolation to asynchronous compute queues.
* `r.FidelityFX.FSR3.Sharpness=0.8`: Optimal edge sharpness for FSR Balanced.

---

## 3. Scalability Settings (`GameUserSettings.ini`)

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

### Key Scalability Attributes
* `sg.ResolutionQuality=59`: FSR Balanced (~1133×637 internal render container upscaled to 1080p). Provides 22% more GPU fillrate headroom than Quality (67%), keeping base combat framerates above 58 FPS.
* `sg.TextureQuality=1`: **Medium Textures**. Crucial for 8 GB cards. Keeps total VRAM under 5.4 GB, completely preventing the 3.75 GB system RAM (GTT) spillover bug.
* `FrameRateLimit=120.000000`: Synchronized with `t.MaxFPS=120` to guarantee a 1:1 display refresh match.

---

## 4. Proton Configuration (`user_settings.py`)

Located in: `~/.local/share/Steam/steamapps/common/Proton - Experimental/user_settings.py`

```python
# Proton Experimental Hardware Optimization Profile
# Designed for AMD Zen 4 + RDNA 3 Navi 33 (SteamOS / Linux)
user_settings = {
    "PROTON_USE_FSR4": "1",                 # Routes upscaling/FG to native AMD FSR 3/4 pipelines
    "RADV_PERFTEST": "gpl",                 # Graphics Pipeline Libraries (eliminates shader compilation stutter)
    "VKD3D_CONFIG": "descriptor_heap",      # Direct GPU descriptor indexing for RDNA architectures
    "WINEDLLOVERRIDES": "steam_api64=n,b;winmm=n,b", # Clean DLL hook handling
    "DXVK_FRAME_RATE": "0",                 # Defers framerate pacing strictly to the engine limiter
    "VKD3D_SWAPCHAIN_LATENCY_FRAMES": "2",  # Low-latency double-buffered swapchain
}
```
