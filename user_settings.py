# ==============================================================================
# Proton Experimental Optimization Profile: AMD RDNA 2/3 (Navi 33)
# Target: Bodycam v0.8 (Unreal Engine 5.5 / VKD3D-Proton / FSR 4.1)
# Deploy to: ~/.local/share/Steam/steamapps/common/Proton - Experimental/
# ==============================================================================

user_settings = {
    # Route upscaling and frame interpolation to native AMD FSR 4.1 pipelines
    "PROTON_USE_FSR4": "1",

    # Enable Graphics Pipeline Libraries in RADV (eliminates in-game shader stutter)
    "RADV_PERFTEST": "gpl",

    # Enable direct GPU descriptor indexing for DirectX 12 render passes
    "VKD3D_CONFIG": "descriptor_heap",

    # Allow custom DLL overrides cleanly
    "WINEDLLOVERRIDES": "steam_api64=n,b;winmm=n,b",

    # Uncap external layer limiter so UE5 engine limiter governs FreeSync pacing
    "DXVK_FRAME_RATE": "0",

    # Double-buffered swapchain to eliminate input latency while keeping pacing smooth
    "VKD3D_SWAPCHAIN_LATENCY_FRAMES": "2",
}
