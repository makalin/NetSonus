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
* 🔊 **Volume control** and auto-gain
* 🎙️ **Audio recording** to WAV files
* 🔍 **Device discovery** on local network
* 📊 **Peak level monitoring**
* 📝 **Comprehensive logging**
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

### 🖥 Basic Usage

```bash
# Receive mode (macOS recommended)
python netsonus.py --mode receive --port 5005 --rate 44100 --blocksize 1024 --channels 2 --timeout 2

# Send mode (Windows recommended)
python netsonus.py --mode send --ip 192.168.1.102 --port 5005 --rate 44100 --blocksize 1024 --channels 2
```

### 🎛 Advanced Usage

```bash
# List available audio devices
python netsonus.py --list-devices

# Discover other NetSonus devices on network
python netsonus.py --discover

# Start streaming with volume control and auto-gain
python netsonus.py --mode send --ip 192.168.1.100 --volume 0.8 --auto-gain

# Start streaming with recording enabled
python netsonus.py --mode receive --port 5005 --record

# Save current settings
python netsonus.py --mode send --ip 192.168.1.100 --volume 0.8 --auto-gain --save
```

💾 Add `--save` to persist these settings in `netsonus_config.json`.

---

## 💡 Configuration Options

### Command Line Arguments

| Option | Description | Default |
|--------|-------------|---------|
| `--mode` | Operation mode (send/receive) | Required |
| `--ip` | Target IP address (required for send mode) | None |
| `--port` | UDP port | 5005 |
| `--rate` | Sample rate | 44100 |
| `--blocksize` | Block size | 1024 |
| `--channels` | Number of channels | 2 |
| `--timeout` | Network timeout (seconds) | 2 |
| `--volume` | Output volume (0.0 to 1.0) | 1.0 |
| `--auto-gain` | Enable automatic gain control | False |
| `--record` | Enable audio recording | False |
| `--discover` | Discover NetSonus devices | False |
| `--list-devices` | List audio devices | False |
| `--save` | Save settings to config file | False |

### Config File

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
  "noise_threshold": 500,
  "volume": 1.0,
  "auto_gain": false,
  "record_path": "recordings"
}
```

---

## 📁 File Structure

| File/Directory | Description |
|----------------|-------------|
| `netsonus.py` | Main CLI script |
| `netsonus_config.json` | Auto-saved user preferences |
| `netsonus.log` | Application log file |
| `recordings/` | Directory for recorded WAV files |

---

## 🔍 Device Discovery

NetSonus can automatically discover other instances on your local network:

1. Run discovery on both devices:
```bash
python netsonus.py --discover
```

2. Use the discovered IP address to start streaming:
```bash
python netsonus.py --mode send --ip <DISCOVERED_IP>
```

---

## 🎙️ Audio Recording

Recorded audio is saved in the `recordings` directory with timestamps:

```bash
recordings/
  ├── recording_20240315_123456.wav
  ├── recording_20240315_123789.wav
  └── ...
```

WAV files are saved with:
- 16-bit PCM format
- Original sample rate
- Original number of channels

---

## 📝 Logging

Logs are written to `netsonus.log` with the following information:
- Audio setup and configuration
- Network connections
- Error messages and warnings
- Recording status
- Volume and gain changes

---

## 🖥 GUI Roadmap

**NetSonus GUI** will feature:

* 🔘 Mode toggle (Send / Receive)
* 🎛 Sliders for latency, volume, and quality
* 📡 IP auto-discovery / QR pairing
* 🔄 Real-time stream visualizer
* 📊 Peak level meter
* 🎙️ Recording controls

Planned frameworks:
* **macOS / Windows**: PyQt6 / Tauri
* **Mobile (iOS/Android)**: Flutter or React Native

---

## 📱 Mobile Companion (Upcoming)

* 🎙 Record and stream phone mic to desktop
* 📡 Receive and play LAN audio
* 📱 Controls for volume/mute/stream quality
* 📊 Real-time audio visualization

---

## 📜 License

MIT — use freely, modify boldly.

---

## 🙋‍♂️ Contributing

* Fork, improve, and submit PRs
* Ideas welcome in Issues or Discussions
* GUI and mobile contributions highly appreciated!

---

Stream Sound, Seamlessly Connected – NetSonus.
