# 🛡️ PORT-SCANNER 🔭 | LIVE Network Security Recon Tool (MacOS)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue.svg" alt="Python 3.13">
  <img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/Security-Hardened-critical" alt="Security">
</p>

<p align="center">
  ⚔️ Monitor network activity, detect scans, and identify threats in real-time with AI-ready scanning modules and next-gen integrations!
</p>

---

## 🎬 Demo Preview

<p align="center">
  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOWxjNnU5eTN5emZzd3kxd3FtbXFzZmJmY3BiaWF0emJna3JybThwNiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/XaQzXJym8lREI/giphy.gif" width="75%" alt="Live Threat Monitoring">
  <br/>
  <em>Live Threat Monitoring in Action</em>
</p>

---

## 🚀 Project Overview

`PORT-SCANNER` is a live network security monitoring and recon tool designed for MacOS (and beyond 🧠), combining powerful tools like:

- 🛰️ `nmap`
- 🧠 `shodan`
- 📊 CSV & PDF Report Gen
- 🖼️ GUI + CLI scanner interface
- 🧪 Smart detection scripts

Perfect for:

- 👨‍💻 Ethical Hackers
- 🛡️ Cybersecurity Students
- 🔍 Red/Blue Teams

---

## ⚙️ Core Features

| 🔥 Feature                    | 🧠 Description                                                                 |
|------------------------------|------------------------------------------------------------------------------|
| 🎯 Real-Time Monitoring       | Detect live scans, probes, and suspicious port activity                       |
| 🛰️ Shodan Integration         | Pull device info, known vulns, fingerprints from Shodan API                   |
| 🔭 Nmap Scanning              | Use CLI-powered scans with multiple techniques (stealth, version, OS)         |
| 🖥️ GUI Dashboard              | Visual interface to scan, view results, and control options                   |
| 📝 Auto Logging               | Save all activity into logs + formatted CSV/PDF reports                       |
| 🧪 Vulnerability Detection    | Match banner versions against public CVEs                                    |

---

## 📥 Installation Instructions

To get started with the `PORT-SCANNER`, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/morningstarxcdcode/port-scanner.git
   cd port-scanner
   ```

2. **Install Dependencies**:
   Make sure you have Python 3.13 installed. Then, install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   You can start the application by running:
   ```bash
   python main.py
   ```

---

## 🛠️ Usage Examples

### Targeting Specific Ports

To scan specific ports, you can specify the port range in the input field. For example, to scan ports 22 (SSH) and 80 (HTTP), you can enter:

```
22,80
```

### Using Nmap Options

You can also utilize various `nmap` options by modifying the command in the `advanced_port_scanner.py` file. For example, to enable OS detection, you can add the `-O` flag:

```python
subprocess.Popen(["nmap", "-O", target, port_range])
```

This will provide additional information about the operating system of the target.

---

## 📝 Contribution Guidelines

Contributions are welcome! If you would like to contribute to the project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with a clear message.
4. Push your changes to your forked repository.
5. Create a pull request to the main repository.

---

## 🛠️ Built With

- 🐍 Python 3.13  
- 🛰️ [Nmap](https://nmap.org/) – Scan engine  
- 🌐 [Shodan](https://shodan.io/) – Internet intelligence  
- 📦 Libraries:
  - `shodan`, `nmap`, `tkinter`, `fpdf`, `pandas`

---

## 📸 Screenshots & Live Demos

### 🎞️ GUI in Action

**What to Showcase:**

- The main dashboard displaying real-time scan results.
- Interactive elements like buttons or menus.
- Any dynamic graphs or charts representing network activity.

**How to Create:**

- Use screen recording tools like **Gifox** (macOS) or **Peek** (Linux) to capture the GUI in action.
- Keep the recording concise (5-10 seconds) focusing on key interactions.
- Optimize the GIF to be under 10MB for smooth loading on GitHub.

**Example Placeholder:**

```markdown
![GUI Demo](https://github.com/morningstarxcdcode/PORT-SCANNER/assets/YOUR_USERNAME/gui-demo.gif)
```

---

### 🛰️ Live Network Scan Detection

**What to Showcase:**

- Terminal output during a live scan.
- Detection of open ports and services.
- Integration with Shodan API displaying device information.

**How to Create:**

- Record your terminal session using **asciinema** and convert it to an animated SVG using **svg-term-cli**.
- Alternatively, use screen recording tools to capture the terminal output and convert it to a GIF.

**Example Placeholder:**

```markdown
![Live Scan](https://github.com/morningstarxcdcode/PORT-SCANNER/assets/YOUR_USERNAME/live-scan.gif)
```

---

### 📁 Auto Logs + Threat Reports

**What to Showcase:**

- A sample of the generated CSV or PDF report.
- Highlighted sections indicating detected threats or anomalies.
- The process of exporting or viewing reports within the application.

**How to Create:**

- Take high-resolution screenshots of the reports.
- Annotate or highlight key sections to draw attention.
- Ensure sensitive information is redacted or anonymized.

**Example Placeholder:**

```markdown
![Threat Report](https://github.com/morningstarxcdcode/PORT-SCANNER/assets/YOUR_USERNAME/threat-report.png)
```

---

## 🛠️ Advanced Usage Examples

### Targeting Specific Ports

To scan specific ports, you can specify the port range in the input field. For example, to scan ports 22 (SSH) and 80 (HTTP), you can enter:

```
22,80
```

### Using Nmap Options

You can also utilize various `nmap` options by modifying the command in the `advanced_port_scanner.py` file. For example, to enable OS detection, you can add the `-O` flag:

```python
subprocess.Popen(["nmap", "-O", target, port_range])
```

This will provide additional information about the operating system of the target.

---

## 🐍 GitHub Contribution Snake Animation

Add a dynamic snake animation to your README to showcase your GitHub activity in a fun way.

**Steps:**

1. **Set Up the Workflow:**
   - Navigate to your repository's **Actions
