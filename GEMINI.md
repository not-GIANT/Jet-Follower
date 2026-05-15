# Jet Follower Project

## Overview
This project features a high-performance, `tkinter`-based fighter jet cursor follower. The script simulates a jet that tracks the user's cursor with physics-based movement, animations, and advanced visual effects like particle exhaust trails and explosions.

## Architectural Highlights
- **Optimized Rendering:** Uses a persistent canvas item pool to minimize memory churn and CPU usage. Instead of clearing the canvas every frame, items are updated via `coords()` and `itemconfig()`.
- **World-Space Particle System:** Particles are managed in global screen coordinates, allowing smoke trails to linger realistically as the jet moves.
- **Physics Engine:** Implements smooth velocity LERPing, angular momentum, and state-driven behaviors (flying, circling, exploding).
- **Centralized Configuration:** All behavioral and aesthetic parameters are exposed in a top-level `CONFIG` dictionary for easy customization.

## Development Progress

### 2026-05-14: Major Overhaul & Enhancement
- **Rendering Optimization:** Replaced `cv.delete('all')` with persistent canvas item management.
- **Fixed Boundary Clamping:** Removed "invisible walls" by allowing the jet window to move partially off-screen. The jet can now follow the cursor to the absolute edges of all monitors.
- **Special Flight Maneuvers:**
    - **Barrel Rolls:** Dynamically simulates 3D rolls during high-G turns by oscillating the polygon perspective.
    - **Afterburners:** Automatically engages when the cursor is at extreme distances, boosting speed by 2x and featuring intense blue exhaust flames.
- **Full Multi-Monitor Support:**
    - Detects the entire virtual desktop area across all connected monitors.
    - Seamlessly traverses display boundaries and spawns from any screen edge.
- **Dual-Weapon Combat System:**
    - **Burst Fire:** Fires a continuous burst of 25 bullets before switching to specialized ordnance.
    - **Homing Missiles:** Deploys 2 high-speed missiles that utilize advanced homing physics to track the real cursor.
    - **Dedicated Visuals:** Missiles feature their own dynamic smoke trails and trigger larger, multi-point impact explosions upon contact.
    - **Mode Switching:** Automatically cycles between bullet bursts and missile strikes for a dynamic combat feel.
- **High-Responsiveness Control:**
    - Reduced input latency (from 1.0s to 0.15s) to ensure the jet reacts almost instantly to cursor movements.
    - **Aggressive Physics:** Increased turn speed and acceleration to match the fast-moving bullet tracers.
    - **Smoothing Refinement:** Tuned the velocity LERPing for a more agile and snappy flight feel.
- **Interactive Shooting Mechanic:**
    - The jet now dynamically shoots at the real cursor when within a configured range (`shoot_dist`).
    - **Visible Bullet Trails:** Bullets appear as high-speed tracer rounds with motion-blur trails.
    - **Impact Effects:** Triggers small, flickering "micro-explosions" upon reaching the target position.
    - **Expanded Viewport:** Increased canvas size to 400x400 to accommodate long-range combat effects.
- **Enhanced Visual Effects:** 
    - **Realistic Smoke Trails:** Refactored particles to **World Coordinates** for authentic lingering effects.
    - **Visibility Boost:** Increased particle size, lifespan (1.5s), and emission density.
    - **Animated Flames:** Dynamic, speed-proportional exhaust flame animations.
- **Performance Tuning:** Optimized cursor history polling with early-exit logic.
- **Enhanced Window Management:** Implemented a transparent, "topmost" frameless window that dynamically follows the jet's position.
- **Robust Configuration:** Centralized all constants into a `CONFIG` object.

**Current State:** Fully functional, high-performance visual tool with rich aesthetics and easy maintainability.
