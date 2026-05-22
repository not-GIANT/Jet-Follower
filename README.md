<!-- BANNER -->
<div align="center">

```
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║        ✈  J E T   F O L L O W E R  ✈                    ║
║                                                          ║
║    PHYSICS-DRIVEN · MULTI-MONITOR · COMBAT AI            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows)](https://github.com/not-GIANT/Jet-Follower/releases)
[![FPS](https://img.shields.io/badge/Target-60%20FPS-brightgreen?style=flat-square)]()
[![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)]()

*A high-performance fighter jet that hunts your cursor — armed, dangerous, and physics-accurate.*

[**⬇ Download .exe**](https://github.com/not-GIANT/Jet-Follower/releases/tag/Latest) · [**📖 Read the Docs**](#-installation) · [**⚙️ Configure**](#%EF%B8%8F-configuration)

</div>

---

## What Is This?

Jet Follower is a `tkinter`-based desktop toy that renders a fully animated fighter jet that chases your cursor across the screen — including across multiple monitors. Under the hood it runs a real physics simulation: velocity LERPing, angular momentum, afterburner states, and an autonomous dual-weapon combat system that fires at your cursor without mercy.

> **This is not a simple "follow the mouse" widget.** It's a miniature flight simulator with a weapons loadout.

---

## ✦ Feature Breakdown

### 🔬 Physics Engine

| System | Description |
|---|---|
| **Velocity LERPing** | Smooth acceleration and deceleration — the jet carries momentum, not just position |
| **Angular Momentum** | Curved turning arcs instead of instant snapping — the jet banks into its turns |
| **Afterburner Logic** | Auto-engages on long-distance pursuit; flame switches from orange to high-intensity blue |
| **Barrel Rolls** | Simulated 3D roll during high-G turns via oscillating polygon perspective |

### ⚔️ Dual-Weapon Combat System

The jet **proactively attacks your cursor** — it's not just following you, it's hunting you.

```
┌─────────────────────────────────────────────────────┐
│  WEAPON 1 — Tracer Burst                            │
│  Fires 25-bullet rapid bursts with motion-blur      │
│  trails. High velocity, tight spread.               │
├─────────────────────────────────────────────────────┤
│  WEAPON 2 — Homing Missiles                         │
│  Dual missiles with real-time pathfinding.          │
│  They will find your cursor. Eventually.            │
└─────────────────────────────────────────────────────┘
```

Both weapons trigger **impact effects**: micro-explosions for bullet hits, multi-point heavy explosions for missile impacts.

### 🎨 Visual Effects

- **World-Space Smoke Trails** — Particles calculated in global coordinates, drifting and lingering as the jet moves
- **60 FPS Rendering** — Optimized item pool management prevents CPU spikes
- **Persistent Particles** — Smoke, fire, and debris all have their own physics lifecycle

### 🖥️ Multi-Monitor Support

- Detects the full virtual desktop bounding box
- Traverses screen edges seamlessly
- Respawns from any screen edge after a fatal cursor-catch

---

## ⬇ Installation

### Option A — Run the Executable *(Windows, zero setup)*

1. Go to [**Releases**](https://github.com/not-GIANT/Jet-Follower/releases/tag/Latest)
2. Download `Jet Follower.exe`
3. Run it. That's it.

### Option B — Run from Source

**Prerequisites:** Python 3.8+ with `tkinter` (included in standard Python installs on Windows)

```bash
# Clone the repo
git clone https://github.com/not-GIANT/Jet-Follower.git
cd Jet-Follower

# Launch
python jet_follower.py
```

Or double-click `Run Jet.bat` if you prefer.

---

## 🕹️ Controls

| Input | Action |
|---|---|
| **Move mouse** | Jet tracks your cursor with physics delay |
| **ESC** | Close the application |
| **Middle click** | Close the application |
| *(automatic)* | If the jet catches the cursor and explodes — it auto-respawns from a random edge |

---

## ⚙️ Configuration

Every tunable parameter lives in the `CONFIG` dictionary at the top of `jet_follower.py`. Open it in any text editor and adjust to taste.

```python
CONFIG = {
    "cursor_delay":      0.08,   # Input lag for the jet's reaction (lower = tighter)
    "max_speed":         18,     # Top velocity in pixels/frame
    "shoot_dist":        300,    # Range at which weapons engage
    "missile_turn_spd":  0.06,   # Missile tracking aggression (higher = sharper turns)
    "explosion_chance":  0.4,    # Probability of exploding on cursor contact
    # ... and many more
}
```

| Parameter | Effect |
|---|---|
| `cursor_delay` | Higher = more sluggish, cinematic feel. Lower = razor-sharp tracking. |
| `max_speed` | How fast the jet can move at full afterburner |
| `shoot_dist` | Increase for a more aggressive, trigger-happy jet |
| `missile_turn_spd` | Raise for heat-seeker missiles; lower for lazy arcs |
| `explosion_chance` | Set to `1.0` if you want every cursor-catch to be fatal |

---

## 🗂️ Project Structure

```
Jet-Follower/
├── jet_follower.py      ← Main simulation — all physics, rendering, weapons
├── Run Jet.bat          ← Windows launcher shortcut
├── Jet Follower.exe     ← Pre-compiled Windows binary
├── icon.png             ← Application icon
└── README.md
```

---

## 🛠️ Built With

- **Python 3** — Core language
- **tkinter** — Rendering and window management (no external dependencies)
- **Pure math** — All physics computed from scratch (no game engine, no library)

---

## 🗺️ Roadmap Ideas

- [ ] Sound effects (engine roar, weapon fire, explosions)
- [ ] Configurable jet skin / color scheme
- [ ] Scoreboard — how long can you dodge?
- [ ] Linux / macOS support
- [ ] Multiple jets at once

---

<div align="center">

---

*Developed with ❤️ by [**GIANT**](https://github.com/not-GIANT)*

*If it made you smile, consider leaving a ⭐*

</div>
