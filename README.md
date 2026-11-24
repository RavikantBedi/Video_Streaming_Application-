# 🎥 Video Streaming Application

Real-time video and audio streaming over **UDP** built with Python, OpenCV, and PyAudio. Captures webcam + microphone on the server, streams compressed frames to one or more clients over the local network, and lets clients view the live stream with on-screen stats while auto-saving recordings.

---

## ✨ Features

- 📹 **Live video + audio streaming** over UDP sockets
- ⚡ **Low-latency** transmission using JPEG-compressed frames
- 📊 **Real-time stats overlay** — FPS, bandwidth, packet-loss %
- 💾 **Auto-recording** of received video (`.avi`) and audio (`.wav`)
- 🔊 **Noise-gated & normalized** audio streaming
- 🤝 **UDP handshake** for client discovery
- 🖥️ **Resizable video window** with topmost display
- 🌐 Optional **web interface** (MJPEG stream) viewable from a browser
- 🪟 Cross-platform — Windows, Linux, macOS

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.x |
| Networking | UDP Sockets |
| Video | OpenCV (`opencv-python`) |
| Audio | PyAudio |
| Serialization | `pickle` + `struct` |
| Compression | JPEG (OpenCV) |
| Web UI (optional) | Python `http.server` + MJPEG |

---

## 📦 Installation

### 1. Clone the repository

```sh
git clone https://github.com/RavikantBedi/Video_Streaming_Application-.git
cd Video_Streaming_Application-
```

### 2. Install dependencies

```sh
pip install opencv-python numpy pyaudio
```

#### Windows — if PyAudio fails to install

```sh
pip install pipwin
pipwin install pyaudio
```

---

## 🚀 Quick Start

Run both scripts on the same local network (LAN / Wi-Fi).

### Terminal 1 — Start the server

```sh
cd Video_Streaming_CN
python server.py
```

The server prints its local IP and the ports it listens on:

```
🌐 Web Interface: http://192.168.x.x:8080
📡 UDP Server: 192.168.x.x:9999
```

### Terminal 2 — Start the client

```sh
cd Video_Streaming_CN
python client.py
```

When prompted, enter the server's IP address:

```
Enter Server IP: 192.168.x.x
```

### Stop the stream

Press **ESC** in the client window (or **Ctrl+C** in the server) to stop streaming and save the recordings.

---

## 📁 Project Structure

```
Video_Streaming_Application-/
├── README.md
├── .gitignore
└── Video_Streaming_CN/
    ├── server.py   # Captures webcam/mic, streams over UDP, optional web UI
    └── client.py   # Receives stream, shows stats, saves recordings
```

Recordings are saved by the client as `recorded_<timestamp>.avi` and `audio_<timestamp>.wav`.

---

## 📊 Packet Structure

Every UDP packet uses a fixed binary header:

| Field | Size | Purpose |
|-------|------|---------|
| Type | 1 byte | `V` = video, `A` = audio |
| Length | 8 bytes | Payload size (`uint64`) |
| Payload | N bytes | Pickled JPEG frame or raw PCM audio |

`make_packet(type, payload) = type + pack("Q", len(payload)) + payload`

---

## ⚙️ Configuration

Edit the constants at the top of each script:

| Parameter | Meaning |
|-----------|---------|
| `JPEG_QUALITY` | Video compression vs. quality (1–100) |
| `RATE` | Audio sample rate (Hz) |
| `CHUNK` | Audio frames per packet |
| `AUDIO_THRESHOLD` | Noise gate level |
| `VIDEO_FPS` / `OUTPUT_VIDEO_FPS` | Recording frame rate |
| `UDP_PORT` / `HTTP_PORT` | Network ports |

> **Important:** Keep `RATE`, `CHUNK`, and `AUDIO_THRESHOLD` identical on server and client.

---

## ⚠️ Known Limitations

- UDP may drop packets on weak networks (shown in the loss % stat).
- No encryption — raw UDP stream. Use only on trusted local networks.
- Works best on local Wi-Fi / LAN.
- Currently optimized for a single client.

---

## 🔮 Future Enhancements

- Multi-client broadcasting
- Forward Error Correction (FEC) for lossy links
- Encryption (SRTP / DTLS)
- Web client via WebRTC

---

## 📜 License

MIT License © 2025 GeekPro
