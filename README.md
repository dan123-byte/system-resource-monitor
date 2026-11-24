# System Resource Monitor

A Python-based desktop application that monitors computer performance in real time, tracks system resource utilization, visualizes performance statistics, and manages running processes through a modern dark-themed dashboard.

## Overview

The System Resource Monitor provides a centralized dashboard for monitoring computer performance and managing active processes.

It collects CPU, memory, disk, and network statistics, displays historical performance charts, and provides tools for searching, sorting, and terminating running processes.

The application runs locally on the user's computer without requiring a backend server or internet connection.

## Features

### System Resource Monitoring
- Monitor real-time CPU utilization.
- Display CPU cores and threads.
- Track RAM usage and available memory.
- Monitor disk utilization and available storage.
- Track network download and upload speeds.

### Performance Dashboard
- Display system resource statistics through metric cards.
- Automatically refresh monitoring data every 2 seconds.
- Visualize CPU and memory usage history.
- Monitor network download and upload activity through charts.

### Process Management
- Display currently running processes.
- View process IDs (PID).
- Monitor individual process CPU usage.
- Monitor individual process memory usage.
- Search processes by name.
- Sort processes by memory usage, CPU usage, or process name.
- Terminate selected processes with confirmation.

### System Information
- Display computer hostname.
- Identify the operating system.
- Display OS version.
- Retrieve processor information.

### User Interface
- Modern dark-themed dashboard.
- Sidebar navigation.
- Organized resource monitoring cards.
- Scrollable dashboard layout.
- Interactive process management table.
- Background process data collection.

## Technologies Used

- **Python** – Core application programming language.
- **CustomTkinter** – Modern desktop graphical interface.
- **Tkinter / ttk** – Native GUI components and process table.
- **psutil** – System resource and process monitoring.
- **Matplotlib** – Performance charts and data visualization.
- **Threading** – Background process data collection.

## Project Structure

```text
system-resource-monitor/
│
├── main.py
│
├── components/
│   ├── system_info.py
│   ├── monitor.py
│   ├── charts.py
│   └── process_manager.py
│
├── requirements.txt
└── README.md
```

### Interface Layout

- **Sidebar Navigation** – Provides access to Overview, Processes, Performance, and System Information.
- **Resource Overview** – Displays CPU, memory, disk, download, and upload statistics through metric cards.
- **Performance Monitoring** – Displays CPU, memory, download, and upload activity through historical performance charts.
- **Running Processes** – Provides a searchable and sortable process table with resource usage information and process termination functionality.
- **System Information** – Displays computer hostname, operating system, OS version, and processor information.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/system-resource-monitor.git
```

### 2. Navigate to the Project Directory

```bash
cd system-resource-monitor
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python main.py
```

## Requirements

- Python 3.10 or later.
- Windows, macOS, or Linux.
- Required Python packages:
  - customtkinter
  - psutil
  - matplotlib