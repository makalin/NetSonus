#!/usr/bin/env python3
import argparse
import json
import socket
import sys
import time
import numpy as np
import threading
import queue
import os
import logging
from datetime import datetime
import wave
import struct

# Platform-specific imports
if sys.platform == 'darwin':  # macOS
    import pyaudio
    import netifaces
elif sys.platform == 'win32':  # Windows
    import sounddevice as sd
else:
    print("Unsupported platform")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('netsonus.log'),
        logging.StreamHandler()
    ]
)

class AudioStreamer:
    def __init__(self, config):
        self.config = config
        self.running = False
        self.audio_queue = queue.Queue()
        self.sock = None
        self.recording = False
        self.volume = 1.0
        self.peak_level = 0
        self.recording_buffer = []
        
        # Initialize audio parameters
        self.rate = config.get('rate', 44100)
        self.blocksize = config.get('blocksize', 1024)
        self.channels = config.get('channels', 2)
        self.timeout = config.get('timeout', 2)
        self.noise_threshold = config.get('noise_threshold', 500)
        self.auto_gain = config.get('auto_gain', False)
        self.record_path = config.get('record_path', 'recordings')

    def setup_audio(self):
        try:
            if sys.platform == 'darwin':
                self.p = pyaudio.PyAudio()
                self.stream = self.p.open(
                    format=pyaudio.get_format_from_width(2),
                    channels=self.channels,
                    rate=self.rate,
                    input=True,
                    output=True,
                    frames_per_buffer=self.blocksize
                )
            elif sys.platform == 'win32':
                self.stream = sd.Stream(
                    samplerate=self.rate,
                    channels=self.channels,
                    blocksize=self.blocksize,
                    dtype=np.int16
                )
            logging.info("Audio setup completed successfully")
        except Exception as e:
            logging.error(f"Failed to setup audio: {e}")
            raise

    def setup_network(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if self.config['mode'] == 'receive':
                self.sock.bind(('0.0.0.0', self.config['port']))
            else:
                self.sock.settimeout(self.timeout)
            logging.info(f"Network setup completed for {self.config['mode']} mode")
        except Exception as e:
            logging.error(f"Failed to setup network: {e}")
            raise

    def get_audio_devices(self):
        """List available audio devices"""
        devices = []
        if sys.platform == 'darwin':
            for i in range(self.p.get_device_count()):
                device_info = self.p.get_device_info_by_index(i)
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels']
                })
        elif sys.platform == 'win32':
            devices = sd.query_devices()
        return devices

    def set_volume(self, volume):
        """Set output volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        logging.info(f"Volume set to {self.volume}")

    def get_peak_level(self, audio_data):
        """Calculate peak audio level"""
        return np.abs(audio_data).max()

    def apply_auto_gain(self, audio_data):
        """Apply automatic gain control"""
        if not self.auto_gain:
            return audio_data
        
        peak = self.get_peak_level(audio_data)
        if peak > 0:
            gain = min(1.0, 32767 / peak)
            return (audio_data * gain).astype(np.int16)
        return audio_data

    def start_recording(self):
        """Start recording audio to WAV file"""
        if not self.recording:
            self.recording = True
            self.recording_buffer = []
            os.makedirs(self.record_path, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.recording_file = os.path.join(self.record_path, f"recording_{timestamp}.wav")
            logging.info(f"Started recording to {self.recording_file}")

    def stop_recording(self):
        """Stop recording and save WAV file"""
        if self.recording:
            self.recording = False
            with wave.open(self.recording_file, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.recording_buffer))
            logging.info(f"Recording saved to {self.recording_file}")

    def discover_devices(self):
        """Discover other NetSonus devices on the network"""
        discovery_port = self.config['port'] + 1
        discovery_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        discovery_sock.settimeout(1)
        
        # Get local network interfaces
        interfaces = []
        if sys.platform == 'darwin':
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        if 'addr' in addr and not addr['addr'].startswith('127.'):
                            interfaces.append(addr['addr'])
        
        # Broadcast discovery message
        for interface in interfaces:
            try:
                discovery_sock.sendto(b'NETSONUS_DISCOVER', (interface, discovery_port))
            except Exception as e:
                logging.error(f"Discovery error on {interface}: {e}")
        
        # Listen for responses
        devices = []
        try:
            while True:
                data, addr = discovery_sock.recvfrom(1024)
                if data == b'NETSONUS_RESPONSE':
                    devices.append(addr[0])
        except socket.timeout:
            pass
        
        discovery_sock.close()
        return devices

    def sender_loop(self):
        print(f"Starting sender to {self.config['ip']}:{self.config['port']}")
        while self.running:
            try:
                if sys.platform == 'darwin':
                    data = self.stream.read(self.blocksize)
                else:
                    data, _ = self.stream.read(self.blocksize)
                    data = data.tobytes()
                
                # Process audio data
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Apply volume and auto-gain
                audio_data = self.apply_auto_gain(audio_data)
                audio_data = (audio_data * self.volume).astype(np.int16)
                
                # Update peak level
                self.peak_level = self.get_peak_level(audio_data)
                
                # Record if enabled
                if self.recording:
                    self.recording_buffer.append(data)
                
                # Send if above noise threshold
                if np.abs(audio_data).mean() > self.noise_threshold:
                    self.sock.sendto(audio_data.tobytes(), (self.config['ip'], self.config['port']))
            except Exception as e:
                logging.error(f"Sender error: {e}")
                time.sleep(0.1)

    def receiver_loop(self):
        print(f"Starting receiver on port {self.config['port']}")
        while self.running:
            try:
                data, addr = self.sock.recvfrom(self.blocksize * self.channels * 2)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Apply volume
                audio_data = (audio_data * self.volume).astype(np.int16)
                
                # Update peak level
                self.peak_level = self.get_peak_level(audio_data)
                
                # Record if enabled
                if self.recording:
                    self.recording_buffer.append(data)
                
                if sys.platform == 'darwin':
                    self.stream.write(audio_data.tobytes())
                else:
                    self.stream.write(audio_data)
            except socket.timeout:
                continue
            except Exception as e:
                logging.error(f"Receiver error: {e}")
                time.sleep(0.1)

    def start(self):
        self.running = True
        self.setup_audio()
        self.setup_network()
        
        if self.config['mode'] == 'send':
            self.sender_loop()
        else:
            self.receiver_loop()

    def stop(self):
        self.running = False
        if self.recording:
            self.stop_recording()
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
        if hasattr(self, 'p'):
            self.p.terminate()
        if self.sock:
            self.sock.close()
        logging.info("AudioStreamer stopped")

def load_config():
    config_file = 'netsonus_config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open('netsonus_config.json', 'w') as f:
        json.dump(config, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='NetSonus - Real-time audio streaming over LAN')
    parser.add_argument('--mode', choices=['send', 'receive'], required=True,
                      help='Operation mode: send or receive')
    parser.add_argument('--ip', help='Target IP address (required for send mode)')
    parser.add_argument('--port', type=int, default=5005, help='UDP port (default: 5005)')
    parser.add_argument('--rate', type=int, default=44100, help='Sample rate (default: 44100)')
    parser.add_argument('--blocksize', type=int, default=1024, help='Block size (default: 1024)')
    parser.add_argument('--channels', type=int, default=2, help='Number of channels (default: 2)')
    parser.add_argument('--timeout', type=int, default=2, help='Network timeout in seconds (default: 2)')
    parser.add_argument('--volume', type=float, default=1.0, help='Output volume (0.0 to 1.0)')
    parser.add_argument('--auto-gain', action='store_true', help='Enable automatic gain control')
    parser.add_argument('--record', action='store_true', help='Enable audio recording')
    parser.add_argument('--discover', action='store_true', help='Discover NetSonus devices on network')
    parser.add_argument('--list-devices', action='store_true', help='List available audio devices')
    parser.add_argument('--save', action='store_true', help='Save current settings to config file')
    
    args = parser.parse_args()
    
    # Load existing config
    config = load_config()
    
    # Update config with command line arguments
    config.update(vars(args))
    
    # Handle special commands
    if args.list_devices:
        streamer = AudioStreamer(config)
        devices = streamer.get_audio_devices()
        print("\nAvailable audio devices:")
        for device in devices:
            print(f"- {device}")
        sys.exit(0)
    
    if args.discover:
        streamer = AudioStreamer(config)
        devices = streamer.discover_devices()
        print("\nDiscovered NetSonus devices:")
        for device in devices:
            print(f"- {device}")
        sys.exit(0)
    
    # Validate required parameters
    if args.mode == 'send' and not args.ip:
        parser.error("--ip is required in send mode")
    
    # Save config if requested
    if args.save:
        save_config(config)
    
    # Start streaming
    streamer = AudioStreamer(config)
    try:
        if args.record:
            streamer.start_recording()
        streamer.start()
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        streamer.stop()

if __name__ == '__main__':
    main() 