# 🎧 NetSonus

**Real-time audio streaming over LAN — simple, efficient, and noise-tolerant.**

Stream uncompressed audio between devices on your local network using Python. NetSonus is lightweight, latency-tunable, and supports both CLI and GUI usage on Windows, macOS, and future mobile platforms.

---

## ⚙️ Features

* 🔄 **Bi-directional audio streaming** over LAN
* 🎚️ **Configurable latency**, sample rate, and buffer size
* 🧠 **Auto device detection** (supports VB-Audio on Windows)
* 💾 **Saves preferred settings** to a local config file
* 📡 **UDP-based transfer** with timeout detection
* 💻 CLI tool for advanced users
* 🖼️ GUI (planned) for ease of use
* 📱 Mobile version (Android/iOS – planned)

---

## 📦 Requirements

### macOS (Receiver or Sender)

```bash
pip install pyaudio netifaces numpy
```

### Windows (Sender or Receiver)

```bash
pip install sounddevice numpy
```

💡 For Windows audio routing, install [VB-Audio Virtual Cable](https://vb-audio.com/Cable/).

---

## 🚀 Quick Start

### 🖥 CLI Usage

```bash
# Receive mode (macOS recommended)
python netsonus.py --mode receive --port 5005 --rate 44100 --blocksize 1024 --channels 2 --timeout 2

# Send mode (Windows recommended)
python netsonus.py --mode send --ip 192.168.1.102 --port 5005 --rate 44100 --blocksize 1024 --channels 2
```

💾 Add `--save` to persist these settings in `netsonus_config.json`.

---

## 💡 Config File

After using `--save`, your configuration is saved as:

```json
{
  "mode": "send",
  "ip": "192.168.1.102",
  "port": 5005,
  "rate": 44100,
  "blocksize": 1024,
  "channels": 2,
  "timeout": 2,
  "noise_threshold": 500
}
```

---

## 🖥 GUI Roadmap

**NetSonus GUI** will feature:

* 🔘 Mode toggle (Send / Receive)
* 🎛 Sliders for latency, volume, and quality
* 📡 IP auto-discovery / QR pairing
* 🔄 Real-time stream visualizer

Planned frameworks:

* **macOS / Windows**: PyQt6 / Tauri
* **Mobile (iOS/Android)**: Flutter or React Native

---

## 📱 Mobile Companion (Upcoming)

* 🎙 Record and stream phone mic to desktop
* 📡 Receive and play LAN audio
* 📱 Controls for volume/mute/stream quality

---

## 📁 File Structure

| File                   | Description                                |
| ---------------------- | ------------------------------------------ |
| `netsonus.py`          | Main CLI script (combined sender/receiver) |
| `netsonus_config.json` | Auto-saved user preferences                |

---

## 📜 License

MIT — use freely, modify boldly.

---

## 🙋‍♂️ Contributing

* Fork, improve, and submit PRs
* Ideas welcome in Issues or Discussions
* GUI and mobile contributions highly appreciated!
