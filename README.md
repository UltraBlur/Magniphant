# 🐘 Magniphant

[English](README.md) | [简体中文](README_CN.md)

> Revealing the Invisible with Elephant's Power

Amplify subtle motions and color changes invisible to the naked eye. Visualize heartbeats, breathing, building vibrations, and create psychedelic art from ordinary videos using Eulerian Video Magnification.

## ✨ Features

- 🫀 **Visualize Heartbeats** - See skin color changes with each heartbeat
- 🌬️ **Amplify Breathing** - Make subtle chest movements visible
- 🏢 **Building Vibrations** - Reveal micro-movements in structures
- 🎨 **Psychedelic Art** - Create surreal visual effects
- 🎵 **Music Visualization** - Sync visuals with rhythm

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (Fast Python package installer)
- FFmpeg (for video processing)

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# or
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Clone the repository
git clone https://github.com/yourusername/magniphant.git
cd magniphant

# Install dependencies with uv
uv sync

# Install FFmpeg
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg
# Windows: Download from https://ffmpeg.org/download.html
```

### Usage

```bash
# Run with GUI
uv run evm

# Or use command line
uv run python main.py input.mp4 -o output.mp4 -m color -a 30 -fl 0.8 -fh 3.0
```

## 📖 Examples

### Heartbeat Visualization

```bash
uv run python main.py face.mp4 -o heartbeat.mp4 \
  -m color -a 30 -fl 0.83 -fh 3.0
```

**Parameters:**
- Frequency: 0.83-3.0 Hz = 50-180 BPM (heartbeat range)
- Mode: Color amplification for blood flow changes

### Breathing Amplification

```bash
uv run python main.py sleeping.mp4 -o breathing.mp4 \
  -m motion -a 50 -fl 0.2 -fh 0.5
```

**Parameters:**
- Frequency: 0.2-0.5 Hz = 12-30 breaths/min
- Mode: Motion amplification for chest movement

### Psychedelic Art

```bash
uv run python main.py scene.mp4 -o psychedelic.mp4 \
  -m hybrid -a 80 -fl 0.1 -fh 10.0
```

**Parameters:**
- Wide frequency range for all changes
- Hybrid mode: Amplify both color and motion
- High amplification for extreme effects

## 🎛️ Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `-m, --mode` | Processing mode: `motion`, `color`, `hybrid` | `-m color` |
| `-a, --amplification` | Amplification factor (5-100) | `-a 30` |
| `-fl, --freq-low` | Low frequency cutoff (Hz) | `-fl 0.8` |
| `-fh, --freq-high` | High frequency cutoff (Hz) | `-fh 3.0` |
| `-l, --levels` | Pyramid levels (3-6) | `-l 4` |
| `--keep-audio` | Keep original audio | `--keep-audio` |

## 📊 Frequency Guide

| Phenomenon | Frequency Range | Parameters |
|------------|----------------|------------|
| Breathing | 0.2-0.5 Hz | `--fl 0.2 --fh 0.5` |
| Heartbeat | 0.8-3.0 Hz | `--fl 0.8 --fh 3.0` |
| Building Vibration | 0.5-2.0 Hz | `--fl 0.5 --fh 2.0` |
| Music (120 BPM) | 1.6-2.4 Hz | `--fl 1.6 --fh 2.4` |

**BPM to Hz:** Hz = BPM / 60

## 🎥 Shooting Tips

**For Best Results:**
- Use a tripod (camera shake will be amplified)
- Stable lighting (avoid flickering)
- Static subject (for heartbeat/breathing)
- High frame rate (60fps+ captures more detail)

**For Creative Effects:**
- Intentional handheld for abstract effects
- Use changing light (sunset, neon)
- Combine with slow motion
- Time-lapse for plant growth

## 🔧 Development

```bash
# Run tests
uv run pytest

# Format code
uv run black .

# Type checking
uv run mypy .
```

## 📚 References

- MIT Paper: ["Eulerian Video Magnification for Revealing Subtle Changes in the World"](http://people.csail.mit.edu/mrub/vidmag/) (2012)
- Phase-based: "Phase-Based Video Motion Processing" (2013)

## 📄 License

MIT License - Based on MIT's open-source implementation for learning and artistic creation.

## 🤝 Contributing

Issues and pull requests are welcome!

---

**Make the invisible visible.** 🎨✨
