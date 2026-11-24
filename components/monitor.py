import time
import psutil

from components.system_info import (
    get_cpu_info,
    get_memory_info,
    get_disk_info,
    get_network_info
)

class SystemMonitor:

    def __init__(self, history_limit=60):

        psutil.cpu_percent(interval=None)

        self.previous_network = get_network_info()
        self.previous_time = time.monotonic()

        self.history_limit = history_limit

        self.history = {
            "cpu": [],
            "memory": [],
            "download": [],
            "upload": []
        }

    def update_history(self, key, value):

        self.history[key].append(value)

        if len(self.history[key]) > self.history_limit:
            self.history[key].pop(0)

    def get_metrics(self):

        cpu = get_cpu_info()
        memory = get_memory_info()
        disks = get_disk_info()

        current_network = get_network_info()
        current_time = time.monotonic()

        elapsed = current_time - self.previous_time

        if elapsed > 0:
            download_speed = (
                current_network["bytes_received"]
                - self.previous_network["bytes_received"]
            ) / elapsed

            upload_speed = (
                current_network["bytes_sent"]
                - self.previous_network["bytes_sent"]
            ) / elapsed
        else:
            download_speed = 0
            upload_speed = 0

        download_speed = max(0, download_speed)
        upload_speed = max(0, upload_speed)

        self.previous_network = current_network
        self.previous_time = current_time

        self.update_history("cpu", cpu["usage"])
        self.update_history("memory", memory["percent"])
        self.update_history("download", download_speed)
        self.update_history("upload", upload_speed)

        return {
            "cpu": cpu,
            "memory": memory,
            "disks": disks,
            "network": {
                "download_speed": download_speed,
                "upload_speed": upload_speed,
                "bytes_received": current_network["bytes_received"],
                "bytes_sent": current_network["bytes_sent"]
            },
            "history": self.history
        }