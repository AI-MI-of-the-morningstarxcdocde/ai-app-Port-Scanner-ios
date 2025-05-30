import subprocess


class VPNManager:
    @staticmethod
    def connect_vpn(config_path):
        """Connect to a VPN using the provided configuration file."""
        try:
            subprocess.run(["openvpn", "--config", config_path], check=True)
            print("VPN connected successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to connect to VPN: {e}")

    @staticmethod
    def disconnect_vpn():
        """Disconnect from the VPN."""
        try:
            subprocess.run(["killall", "openvpn"], check=True)
            print("VPN disconnected successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to disconnect VPN: {e}")

# Added network traffic analysis functionality


class NetworkTrafficAnalyzer:
    def __init__(self):
        self.captured_packets = []
        self.is_capturing = False
        self.capture_thread = None

    def start_capture(self, interface="en0", filter_str="", capture_time=60):
        """Start capturing network traffic on the specified interface."""
        try:
            # Check if we're already capturing
            if self.is_capturing:
                print("Already capturing traffic.")
                return False

            import subprocess  # Local import is fine for this method
            import threading
            import time

            def capture_packets():
                try:
                    cmd = ["tcpdump", "-i", interface]
                    if filter_str:
                        cmd.extend(["-n", filter_str])
                    cmd.extend(["-v", "-w", "traffic_capture.pcap"])

                    self.process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )

                    # Capture for specified time
                    time.sleep(capture_time)

                    # Stop capture
                    self.process.terminate()
                    self.is_capturing = False

                    # Analyze the captured packets
                    self.analyze_capture("traffic_capture.pcap")

                except Exception as e:
                    print(f"Error during packet capture: {e}")
                    self.is_capturing = False

            self.is_capturing = True
            self.capture_thread = threading.Thread(target=capture_packets)
            self.capture_thread.daemon = True
            self.capture_thread.start()

            print(f"Started capturing traffic on interface {interface}")
            return True

        except Exception as e:
            print(f"Failed to start packet capture: {e}")
            return False

    def stop_capture(self):
        """Stop the current packet capture."""
        if self.is_capturing and hasattr(self, 'process'):
            self.process.terminate()
            self.is_capturing = False
            print("Packet capture stopped.")
            return True
        else:
            print("No active packet capture to stop.")
            return False

    def analyze_capture(self, pcap_file):
        """Analyze the captured packet file and extract insights."""
        try:
            import subprocess  # Local import

            # Get a summary of the capture
            cmd = ["tcpdump", "-r", pcap_file, "-n", "-q"]
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    check=False)  # check=False if non-zero is ok

            # Extract basic statistics
            packet_count = len(result.stdout.split('\n')) - 1

            # Extract protocol statistics
            tcp_count = result.stdout.count("TCP")
            udp_count = result.stdout.count("UDP")
            icmp_count = result.stdout.count("ICMP")

            # Get unique IPs
            ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
            import re  # Local import
            unique_ips = set(re.findall(ip_pattern, result.stdout))

            analysis = {
                "packet_count": packet_count,
                "tcp_count": tcp_count,
                "udp_count": udp_count,
                "icmp_count": icmp_count,
                "unique_ips": list(unique_ips),
                "capture_file": pcap_file
            }

            print("Traffic Analysis Results:")
            print(f"Total packets: {packet_count}")
            print(f"TCP packets: {tcp_count}")
            print(f"UDP packets: {udp_count}")
            print(f"ICMP packets: {icmp_count}")
            print(f"Unique IPs: {len(unique_ips)}")

            return analysis

        except Exception as e:
            print(f"Error analyzing packet capture: {e}")
            return None