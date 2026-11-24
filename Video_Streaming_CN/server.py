# # server_with_web.py
# import cv2, socket, pickle, struct, time, pyaudio, numpy as np
# import threading
# from http.server import BaseHTTPRequestHandler, HTTPServer

# # Config
# VIDEO_WIDTH, VIDEO_HEIGHT = 480, 320
# JPEG_QUALITY = 50
# SERVER_IP = "0.0.0.0"
# UDP_PORT = 9999
# HTTP_PORT = 8080  # Web server port
# RATE = 16000
# CHUNK = 1024
# AUDIO_THRESHOLD = 500

# # Global variable to store latest frame
# latest_frame = None
# frame_lock = threading.Lock()

# def make_packet(t: bytes, payload: bytes):
#     return t + struct.pack("Q", len(payload)) + payload

# class StreamHandler(BaseHTTPRequestHandler):
#     def log_message(self, format, *args):
#         pass  # Suppress log messages
    
#     def do_GET(self):
#         if self.path == '/':
#             # Serve the HTML page
#             self.send_response(200)
#             self.send_header('Content-type', 'text/html')
#             self.end_headers()
#             html = f"""
#             <!DOCTYPE html>
#             <html>
#             <head>
#                 <meta name="viewport" content="width=device-width, initial-scale=1.0">
#                 <title>Live Stream</title>
#                 <style>
#                     body {{
#                         margin: 0;
#                         padding: 20px;
#                         background: #000;
#                         display: flex;
#                         flex-direction: column;
#                         align-items: center;
#                         justify-content: center;
#                         min-height: 100vh;
#                         font-family: Arial, sans-serif;
#                     }}
#                     h1 {{
#                         color: #0f0;
#                         text-align: center;
#                         margin-bottom: 20px;
#                     }}
#                     img {{
#                         max-width: 100%;
#                         height: auto;
#                         border: 3px solid #0f0;
#                         border-radius: 10px;
#                         box-shadow: 0 0 20px rgba(0,255,0,0.5);
#                     }}
#                     .info {{
#                         color: #0f0;
#                         text-align: center;
#                         margin-top: 10px;
#                         font-size: 14px;
#                     }}
#                 </style>
#             </head>
#             <body>
#                 <h1>🎥 Live Stream - GeekPro</h1>
#                 <img src="/stream" alt="Live Stream">
#                 <div class="info">📡 Streaming from your computer</div>
#             </body>
#             </html>
#             """
#             self.wfile.write(html.encode())
        
#         elif self.path == '/stream':
#             # Serve MJPEG stream
#             self.send_response(200)
#             self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
#             self.end_headers()
            
#             try:
#                 while True:
#                     with frame_lock:
#                         if latest_frame is not None:
#                             _, jpg = cv2.imencode('.jpg', latest_frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
#                             frame_bytes = jpg.tobytes()
                    
#                     if latest_frame is not None:
#                         self.wfile.write(b'--frame\r\n')
#                         self.send_header('Content-type', 'image/jpeg')
#                         self.send_header('Content-length', len(frame_bytes))
#                         self.end_headers()
#                         self.wfile.write(frame_bytes)
#                         self.wfile.write(b'\r\n')
                    
#                     time.sleep(0.033)  # ~30 FPS
#             except:
#                 pass

# def udp_stream_thread():
#     """Handle UDP streaming to desktop clients"""
#     global latest_frame
    
#     print("✅ UDP Server starting...")
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
#     sock.bind((SERVER_IP, UDP_PORT))
#     sock.settimeout(1.0)  # Non-blocking with timeout
    
#     clients = []
#     print(f"📡 UDP server listening on port {UDP_PORT}...")
    
#     # Audio capture
#     pa = pyaudio.PyAudio()
#     audio_stream = pa.open(format=pyaudio.paInt16,
#                            channels=1,
#                            rate=RATE,
#                            input=True,
#                            frames_per_buffer=CHUNK)
    
#     try:
#         while True:
#             # Check for new clients
#             try:
#                 data, addr = sock.recvfrom(1024)
#                 if addr not in clients:
#                     clients.append(addr)
#                     print("✅ UDP Client connected:", addr)
#             except socket.timeout:
#                 pass
            
#             if latest_frame is not None and len(clients) > 0:
#                 # Send video to UDP clients
#                 _, jpg = cv2.imencode(".jpg", latest_frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
#                 v_payload = pickle.dumps(jpg)
#                 v_packet = make_packet(b'V', v_payload)
                
#                 for c in clients[:]:
#                     try:
#                         sock.sendto(v_packet, c)
#                     except Exception as e:
#                         print(f"Removing dead client {c}")
#                         clients.remove(c)
                
#                 # Send audio
#                 try:
#                     raw = audio_stream.read(CHUNK, exception_on_overflow=False)
#                     arr = np.frombuffer(raw, dtype=np.int16)
#                     if np.abs(arr).mean() > AUDIO_THRESHOLD:
#                         peak = max(1, np.max(np.abs(arr)))
#                         factor = 15000 / peak
#                         arr = (arr * factor).astype(np.int16)
#                         a_payload = arr.tobytes()
#                         a_packet = make_packet(b'A', a_payload)
#                         for c in clients:
#                             try:
#                                 sock.sendto(a_packet, c)
#                             except Exception:
#                                 pass
#                 except Exception:
#                     pass
            
#             time.sleep(0.02)
    
#     finally:
#         audio_stream.stop_stream()
#         audio_stream.close()
#         pa.terminate()
#         sock.close()

# def main():
#     global latest_frame
    
#     print("🎥 Starting GeekPro Streaming Server...")
    
#     # Start UDP thread
#     udp_thread = threading.Thread(target=udp_stream_thread, daemon=True)
#     udp_thread.start()
    
#     # Get local IP
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     try:
#         s.connect(("8.8.8.8", 80))
#         local_ip = s.getsockname()[0]
#         s.close()
#     except:
#         local_ip = "localhost"
    
#     # Start HTTP server
#     print(f"\n{'='*50}")
#     print(f"🌐 Web Server: http://{local_ip}:{HTTP_PORT}")
#     print(f"📱 Open this URL on your phone's browser")
#     print(f"📡 UDP Server: {local_ip}:{UDP_PORT} (for desktop client)")
#     print(f"{'='*50}\n")
    
#     # Video capture
#     cap = cv2.VideoCapture(0)
#     cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
#     cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
    
#     if not cap.isOpened():
#         raise SystemExit("❌ Camera not found")
    
#     print("✅ Camera opened successfully")
#     print("🎬 Streaming started... Press Ctrl+C to stop\n")
    
#     # Start HTTP server in separate thread
#     server = HTTPServer(('0.0.0.0', HTTP_PORT), StreamHandler)
#     server_thread = threading.Thread(target=server.serve_forever, daemon=True)
#     server_thread.start()
    
#     try:
#         while True:
#             ret, frame = cap.read()
#             if ret:
#                 frame = cv2.resize(frame, (VIDEO_WIDTH, VIDEO_HEIGHT))
#                 with frame_lock:
#                     latest_frame = frame.copy()
#             time.sleep(0.01)
    
#     except KeyboardInterrupt:
#         print("\n⏹️  Stopping server...")
    
#     finally:
#         cap.release()
#         server.shutdown()
#         print("✅ Server stopped")

# if __name__ == "__main__":
#     main()







# server_with_web.py
import cv2, socket, pickle, struct, time, pyaudio, numpy as np
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# Config
VIDEO_WIDTH, VIDEO_HEIGHT = 480, 320
JPEG_QUALITY = 50
SERVER_IP = "0.0.0.0"
UDP_PORT = 9999
HTTP_PORT = 8080
RATE = 16000
CHUNK = 1024
AUDIO_THRESHOLD = 500

# Global variables
latest_frame = None
frame_lock = threading.Lock()
stream_stats = {"viewers": 0, "start_time": None, "frames_sent": 0}
stats_lock = threading.Lock()

def make_packet(t: bytes, payload: bytes):
    return t + struct.pack("Q", len(payload)) + payload

class StreamHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GeekPro Live Stream</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
            max-width: 900px;
            width: 100%;
            backdrop-filter: blur(10px);
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            color: white;
            text-align: center;
            position: relative;
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 5px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .live-badge {
            position: absolute;
            top: 20px;
            right: 20px;
            background: #ff4444;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            animation: pulse 2s infinite;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .live-dot {
            width: 8px;
            height: 8px;
            background: white;
            border-radius: 50%;
            animation: blink 1s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        
        .video-container {
            position: relative;
            background: #000;
            width: 100%;
            padding-top: 66.67%; /* 3:2 aspect ratio */
        }
        
        .video-stream {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: contain;
        }
        
        .loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 18px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 15px;
        }
        
        .spinner {
            border: 3px solid rgba(255,255,255,0.3);
            border-top: 3px solid white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            padding: 25px;
            background: #f8f9fa;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .stat-icon {
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 13px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .footer {
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .footer p {
            margin: 5px 0;
            font-size: 14px;
        }
        
        .team-name {
            font-weight: bold;
            color: #667eea;
            font-size: 16px;
        }
        
        .controls {
            padding: 20px;
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
            transform: scale(1.05);
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 22px;
            }
            
            .live-badge {
                position: static;
                margin: 10px auto 0;
                width: fit-content;
            }
            
            .stats {
                grid-template-columns: 1fr 1fr;
                padding: 15px;
                gap: 10px;
            }
            
            .stat-card {
                padding: 15px;
            }
            
            .stat-icon {
                font-size: 24px;
            }
            
            .stat-value {
                font-size: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="live-badge">
                <div class="live-dot"></div>
                LIVE
            </div>
            <h1>
                🎥 GeekPro Live Stream
            </h1>
            <p>Professional Real-Time Video Streaming</p>
        </div>
        
        <div class="video-container">
            <img src="/stream" alt="Live Stream" class="video-stream" id="videoStream" style="display:none;">
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <div>Connecting to stream...</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="btn btn-primary" onclick="toggleFullscreen()">
                <span>⛶</span> Fullscreen
            </button>
            <button class="btn btn-secondary" onclick="refreshStream()">
                <span>🔄</span> Refresh
            </button>
            <button class="btn btn-secondary" onclick="takeScreenshot()">
                <span>📸</span> Screenshot
            </button>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-icon">👥</div>
                <div class="stat-value" id="viewers">0</div>
                <div class="stat-label">Active Viewers</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">⏱️</div>
                <div class="stat-value" id="uptime">00:00:00</div>
                <div class="stat-label">Stream Uptime</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">🎬</div>
                <div class="stat-value" id="fps">30</div>
                <div class="stat-label">FPS</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-value" id="quality">HD</div>
                <div class="stat-label">Quality</div>
            </div>
        </div>
        
        <div class="footer">
            <p class="team-name">🚀 Developed by Team GeekPro</p>
            <p>Ravikant Bedi • Dev Saxena • Sushant Kanijiya</p>
            <p style="margin-top: 10px; opacity: 0.7;">© 2025 All Rights Reserved</p>
        </div>
    </div>
    
    <script>
        const videoStream = document.getElementById('videoStream');
        const loading = document.getElementById('loading');
        let startTime = Date.now();
        
        // Show stream once loaded
        videoStream.onload = function() {
            loading.style.display = 'none';
            videoStream.style.display = 'block';
        };
        
        // Update stats
        function updateStats() {
            // Update uptime
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            const hours = Math.floor(elapsed / 3600).toString().padStart(2, '0');
            const minutes = Math.floor((elapsed % 3600) / 60).toString().padStart(2, '0');
            const seconds = (elapsed % 60).toString().padStart(2, '0');
            document.getElementById('uptime').textContent = `${hours}:${minutes}:${seconds}`;
            
            // Simulate viewer count (in production, get from server)
            const viewers = Math.floor(Math.random() * 3) + 1;
            document.getElementById('viewers').textContent = viewers;
        }
        
        setInterval(updateStats, 1000);
        
        // Fullscreen
        function toggleFullscreen() {
            const container = document.querySelector('.video-container');
            if (!document.fullscreenElement) {
                container.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        }
        
        // Refresh stream
        function refreshStream() {
            const currentSrc = videoStream.src;
            videoStream.style.display = 'none';
            loading.style.display = 'flex';
            videoStream.src = currentSrc + '?t=' + Date.now();
        }
        
        // Screenshot
        function takeScreenshot() {
            const canvas = document.createElement('canvas');
            canvas.width = videoStream.naturalWidth;
            canvas.height = videoStream.naturalHeight;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(videoStream, 0, 0);
            
            const link = document.createElement('a');
            link.download = `screenshot_${Date.now()}.png`;
            link.href = canvas.toDataURL();
            link.click();
        }
        
        // Handle stream errors
        videoStream.onerror = function() {
            loading.innerHTML = '<div class="spinner"></div><div>Connection lost. Retrying...</div>';
            setTimeout(() => {
                videoStream.src = '/stream?t=' + Date.now();
            }, 2000);
        };
    </script>
</body>
</html>
            """
            self.wfile.write(html.encode())
        
        elif self.path == '/stream':
            with stats_lock:
                stream_stats["viewers"] += 1
            
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            
            try:
                while True:
                    with frame_lock:
                        if latest_frame is not None:
                            _, jpg = cv2.imencode('.jpg', latest_frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
                            frame_bytes = jpg.tobytes()
                            
                            with stats_lock:
                                stream_stats["frames_sent"] += 1
                    
                    if latest_frame is not None:
                        self.wfile.write(b'--frame\r\n')
                        self.send_header('Content-type', 'image/jpeg')
                        self.send_header('Content-length', len(frame_bytes))
                        self.end_headers()
                        self.wfile.write(frame_bytes)
                        self.wfile.write(b'\r\n')
                    
                    time.sleep(0.033)
            except:
                pass
            finally:
                with stats_lock:
                    stream_stats["viewers"] = max(0, stream_stats["viewers"] - 1)

def udp_stream_thread():
    global latest_frame
    
    print("✅ UDP Server starting...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
    sock.bind((SERVER_IP, UDP_PORT))
    sock.settimeout(1.0)
    
    clients = []
    print(f"📡 UDP server listening on port {UDP_PORT}...")
    
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(format=pyaudio.paInt16,
                           channels=1,
                           rate=RATE,
                           input=True,
                           frames_per_buffer=CHUNK)
    
    try:
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                if addr not in clients:
                    clients.append(addr)
                    print("✅ UDP Client connected:", addr)
            except socket.timeout:
                pass
            
            if latest_frame is not None and len(clients) > 0:
                _, jpg = cv2.imencode(".jpg", latest_frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
                v_payload = pickle.dumps(jpg)
                v_packet = make_packet(b'V', v_payload)
                
                for c in clients[:]:
                    try:
                        sock.sendto(v_packet, c)
                    except Exception:
                        clients.remove(c)
                
                try:
                    raw = audio_stream.read(CHUNK, exception_on_overflow=False)
                    arr = np.frombuffer(raw, dtype=np.int16)
                    if np.abs(arr).mean() > AUDIO_THRESHOLD:
                        peak = max(1, np.max(np.abs(arr)))
                        factor = 15000 / peak
                        arr = (arr * factor).astype(np.int16)
                        a_payload = arr.tobytes()
                        a_packet = make_packet(b'A', a_payload)
                        for c in clients:
                            try:
                                sock.sendto(a_packet, c)
                            except Exception:
                                pass
                except Exception:
                    pass
            
            time.sleep(0.02)
    
    finally:
        audio_stream.stop_stream()
        audio_stream.close()
        pa.terminate()
        sock.close()

def main():
    global latest_frame, stream_stats
    
    print("\n" + "="*60)
    print("🎥 GeekPro Professional Streaming Server")
    print("="*60 + "\n")
    
    stream_stats["start_time"] = datetime.now()
    
    udp_thread = threading.Thread(target=udp_stream_thread, daemon=True)
    udp_thread.start()
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "localhost"
    
    print(f"🌐 Web Interface: http://{local_ip}:{HTTP_PORT}")
    print(f"📱 Mobile Access: http://{local_ip}:{HTTP_PORT}")
    print(f"📡 UDP Server: {local_ip}:{UDP_PORT}")
    print(f"\n{'='*60}\n")
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
    
    if not cap.isOpened():
        raise SystemExit("❌ Camera not found")
    
    print("✅ Camera initialized")
    print("🎬 Streaming active... Press Ctrl+C to stop\n")
    
    server = HTTPServer(('0.0.0.0', HTTP_PORT), StreamHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    
    try:
        while True:
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (VIDEO_WIDTH, VIDEO_HEIGHT))
                with frame_lock:
                    latest_frame = frame.copy()
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n⏹️  Stopping server...")
    
    finally:
        cap.release()
        server.shutdown()
        print("✅ Server stopped successfully")

if __name__ == "__main__":
    main()