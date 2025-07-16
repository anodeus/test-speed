import requests
import time
import subprocess
import re
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

FILE_URL = "https://raw.githubusercontent.com/anodeus/test-speed/fc754a4d7f9409c4f66ef8282de4fcabd77f45d6/testfile_5mb.bin"

# -------- Evaluation Functions --------
def evaluate_speed(speed):
    if speed >= 1000:
        return "1 Gbps+ / Future-Proof (10K+)"
    elif speed >= 500:
        return "Server-Grade / Enterprise (10K/12K)"
    elif speed >= 100:
        return "Gaming + 8K / Multi-Device (4320p)"
    elif speed >= 60:
        return "8K Ultra HD (4320p)"
    elif speed >= 35:
        return "4K Ultra HD (2160p)"
    elif speed >= 20:
        return "1440p Quad HD"
    elif speed >= 10:
        return "Full HD (1080p)"
    elif speed >= 5:
        return "HD Ready (720p)"
    elif speed >= 3:
        return "Standard Definition (480p)"
    elif speed >= 2:
        return "Basic SD (360p)"
    elif speed >= 1:
        return "Low SD (240p)"
    else:
        return "Too Slow for Video"

def evaluate_latency(latency):
    if latency < 30:
        return Fore.GREEN + "Excellent"
    elif latency < 60:
        return Fore.GREEN + "Good"
    elif latency < 100:
        return Fore.YELLOW + "Moderate"
    else:
        return Fore.RED + "Poor"

def evaluate_jitter(jitter):
    if jitter < 10:
        return Fore.GREEN + "Good"
    elif jitter < 30:
        return Fore.YELLOW + "Fair"
    else:
        return Fore.RED + "Unstable"



def overall_quality(speed, latency, jitter, packet_loss):
    if speed > 25 and latency < 50 and jitter < 10 and packet_loss < 1:
        return Fore.GREEN + "Excellent"
    elif speed > 10 and latency < 80 and jitter < 20 and packet_loss < 3:
        return Fore.YELLOW + "Good"
    elif speed > 5 and latency < 150 and packet_loss < 5:
        return Fore.YELLOW + "Average"
    else:
        return Fore.RED + "Poor"

# -------- Test Functions --------
def test_download_speed():
    print(Fore.YELLOW + "[*] Testing download speed...", end=" ")
    start_time = time.time()
    try:
        response = requests.get(FILE_URL, stream=True, timeout=10)
    except:
        print(Fore.RED + "Failed (network error)")
        return 0.0
    total_bytes = 0

    with open("/tmp/test_download.bin", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                total_bytes += len(chunk)

    end_time = time.time()
    duration = end_time - start_time
    if total_bytes == 0 or duration == 0:
        print(Fore.RED + "Failed")
        return 0.0
    speed_mbps = (total_bytes * 8) / (duration * 1024 * 1024)
    print(Style.BRIGHT + Fore.MAGENTA + evaluate_speed(speed_mbps))
    print(Fore.YELLOW + "[*] " + Fore.YELLOW + "Downloaded " + 
          Fore.GREEN + f"{total_bytes}" + 
          Fore.YELLOW + " bytes in " + 
          Fore.GREEN + f"{duration:.2f}" + 
          Fore.YELLOW + " seconds")
    return speed_mbps

def test_latency():
    print(Fore.YELLOW + "[*] Testing latency (ping)...", end=" ")
    try:
        result = subprocess.run(["ping", "-c", "1", "8.8.8.8"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        match = re.search(r'time=(\d+\.\d+)', result.stdout)
        if match:
            latency = float(match.group(1))
            print(evaluate_latency(latency))
            return latency
        else:
            print(Fore.RED + "Unavailable")
            return -1
    except Exception as e:
        print(Fore.RED + f"Error: {e}")
        return -1

def test_jitter(samples=5):
    print(Fore.YELLOW + "[*] Testing jitter...", end=" ")
    times = []
    for _ in range(samples):
        result = subprocess.run(["ping", "-c", "1", "8.8.8.8"],
                                stdout=subprocess.PIPE, text=True)
        match = re.search(r'time=(\d+\.\d+)', result.stdout)
        if match:
            times.append(float(match.group(1)))
        time.sleep(0.2)
    if len(times) < 2:
        print(Fore.RED + "Not enough data")
        return 0.0
    jitter = max(times) - min(times)
    print(evaluate_jitter(jitter))
    return jitter

def test_packet_loss():
    print(Fore.YELLOW + "[*] Testing packet loss...", end=" ")
    try:
        result = subprocess.run(["ping", "-c", "5", "8.8.8.8"],
                                stdout=subprocess.PIPE, text=True)
        match = re.search(r'(\d+)% packet loss', result.stdout)
        if match:
            loss = float(match.group(1))
            color = Fore.GREEN if loss == 0 else Fore.YELLOW if loss < 5 else Fore.RED
            print(color + f"{loss}%")
            return loss
        else:
            print(Fore.GREEN + "0.0%")
            return 0.0
    except:
        print(Fore.RED + "Error")
        return -1

def get_ip_info():
    print(Fore.YELLOW + "[*] Fetching IP & location info...")
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5)
        data = res.json()
        return {
            "ip": data.get("ip", "N/A"),
            "org": data.get("org", "N/A"),
            "city": data.get("city", "N/A"),
            "region": data.get("region", "N/A"),
            "country": data.get("country", "N/A")
        }
    except:
        return {
            "ip": "N/A",
            "org": "N/A",
            "city": "N/A",
            "region": "N/A",
            "country": "N/A"
        }


def show_results1(download_speed, latency, jitter, packet_loss, ipinfo, rating):
    frame_color = Fore.CYAN  # You can change this to WHITE, LIGHTGREEN_EX, etc.

    print(frame_color + "\n┌───────────────" + Fore.CYAN + " Speed Test Results " + frame_color + "──────────────┐")

    speed_color = Fore.GREEN if download_speed > 15 else Fore.RED
    print(frame_color + "│ " + Style.BRIGHT+Fore.BLUE + "Download Speed : " + speed_color + f"{download_speed:.2f} Mbps" +
          frame_color + ' ' * (25 - len(f"{download_speed:.2f}")) + " │")

   # Latency Coloring
    if latency < 38.4:
        latency_color = Fore.GREEN
    elif latency < 80:
        latency_color = Fore.YELLOW
    else:
        latency_color = Fore.RED
    print(frame_color + "│ " + Style.BRIGHT+Fore.BLUE + "Latency        : " + latency_color + f"{latency:.2f} ms" +
          frame_color + ' ' * (28 - len(f"{latency:.2f}")) + "│")
    # Jitter Coloring
    if jitter < 10:
        jitter_color = Fore.GREEN
    elif jitter < 30:
        jitter_color = Fore.YELLOW
    else:
        jitter_color = Fore.RED
    print(frame_color + "│ " + Style.BRIGHT+Fore.BLUE + "Jitter         : " + jitter_color + f"{jitter:.2f} ms" +
          frame_color + ' ' * (28 - len(f"{jitter:.2f}")) + "│")

    packet_color = Fore.GREEN if packet_loss == 0 else Fore.RED
    print(frame_color + "│ " + Style.BRIGHT+Fore.BLUE + "Packet Loss    : " + packet_color + f"{packet_loss:.1f}%" +
          frame_color + ' ' * (29 - len(f"{packet_loss:.1f}")) + " │")

    print(frame_color + "└─────────────────────────────────────────────────┘")

    print(Style.BRIGHT + Fore.MAGENTA + f"\nOverall Connection Quality: {rating}")
    print(Fore.LIGHTGREEN_EX + "Public IP : " + Fore.GREEN + ipinfo['ip'])
    print(Fore.LIGHTGREEN_EX + "ISP       : " + Fore.GREEN + ipinfo['org'])
    print(Fore.LIGHTGREEN_EX + "Location  : " + Fore.GREEN + f"{ipinfo['city']}, {ipinfo['region']}, {ipinfo['country']}")


# -------- Main Execution --------
if __name__ == "__main__":
    print(Style.BRIGHT + Fore.MAGENTA + "Testing internet speed and quality...\n")
    latency = test_latency()
    jitter = test_jitter()
    packet_loss = test_packet_loss()
    download_speed = test_download_speed()
    ipinfo = get_ip_info()
    rating = overall_quality(download_speed, latency, jitter, packet_loss)
    show_results1(download_speed, latency, jitter, packet_loss, ipinfo, rating)
