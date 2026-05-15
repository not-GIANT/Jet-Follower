# Jet Follower

A high-performance, `tkinter`-based fighter jet cursor follower with physics-based movement, animations, and advanced visual effects.

## Features
- **Optimized Rendering:** Uses a persistent canvas item pool to minimize memory churn and CPU usage.
- **Physics Engine:** Implements smooth velocity LERPing, angular momentum, and state-driven behaviors (flying, circling, exploding).
- **Combat System:** Automatically cycles between bullet bursts and homing missiles with dedicated visual effects and impact explosions.
- **Multi-Monitor Support:** Seamlessly traverses display boundaries across all connected monitors.
- **Visual Effects:** Realistic world-space smoke trails, animated exhaust flames, and barrel rolls during high-G turns.

## Installation
1. Ensure you have Python 3.x installed.
2. Download the `jet_follower.py` script.
3. Run the script:
   ```bash
   python jet_follower.py
   ```
   Or use the provided `Jet Follower.exe` (Windows).

## Controls
- **Cursor:** The jet follows your cursor automatically.
- **ESC / Middle Click:** Exit the application.

## Configuration
Behavioral and aesthetic parameters can be adjusted in the `CONFIG` dictionary at the top of `jet_follower.py`.
